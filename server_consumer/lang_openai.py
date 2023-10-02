import os
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

 
persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: “text-davinci-003”
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
  

def load_data(mongo_history):
    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
    You can assume the question about greetings and credit card information.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
    
    template = """
    你是一個銀行信用卡介紹與優惠資訊的聊天機器人，包含：
    1.'銀行名稱':'台新', 'web_domian':'https://www.taishinbank.com.tw',
    2.'銀行名稱':'國泰世華', 'web_domain':'https://www.cathaybk.com.tw',
    3.'銀行名稱':'中國信託', 'web_domain':'https://www.ctbcbank.com',
    4.'銀行名稱':'滙豐匯豐', 'web_domain':'https://www.hsbc.com.tw',
    請依據下方給定的內容與使用者本次問題進行回覆。
    請依使用者提問的語言回答他的問題，若有不清楚使用者語言或是簡體中文，一律使用繁體中文回答。
    如果使用者的問題與信用卡、基本問候無關的話，請回答「抱歉，我目前沒有這個問題的相關資訊。您可以調整您的提問，或是詢問我其他問題。」
    當你無法理解使用者的提問時，請引導使用者作出更詳細的提問。
    Question: {question}
    =========
    {context}
    =========
    Answer in Markdown:"""
    QA_PROMPT = PromptTemplate(template=template, input_variables=[
                            "question", "context"])

    # 4. Now we can load the persisted database from disk
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    
    # retriever = vectordb.as_retriever() 
    # retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 2}) 
    retriever = vectordb.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": .5})
    memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=mongo_history, return_messages=True)
    conversation_qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        memory=memory,
        verbose=True,
        # chain_type="stuff",
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        max_tokens_limit=350)
    return conversation_qa_chain

