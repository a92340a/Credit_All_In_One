import os
import sys
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_mongodb


mongo_db = _get_mongodb()
mongo_collection = mongo_db["official_website"] 
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
    你是一個數家銀行信用卡介紹與優惠資訊的聊天機器人，包括：
    1.'銀行名稱': 'crawling_chartered', '卡片名稱': '渣打優先理財無限卡', '渣打現金回饋御璽卡', '渣打LINE Bank聯名卡', 'TheShoppingCard 分期卡'。
    請依據下方給定的內容與使用者本次問題進行回覆。
    請依使用者提問的語言回答他的問題，若有不清楚使用者語言或是簡體中文，一律使用繁體中文回答。
    如果有搜尋到相關信用卡資訊，但詳細資料不足，請提供資料庫內該資訊的url連結給使用者自行檢索。
    如果使用者的問題與信用卡、基本問候無關的話，請回答「抱歉，我目前沒有這個問題的相關資訊。您可以調整您的提問，或是詢問我其他問題。」
    當你無法理解使用者的提問時，請引導使用者作出更詳細的提問。
    Question: {question}
    =========
    {context}
    =========
    Answer in Markdown:"""
    QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])

    # 4. Now we can load the persisted database from disk
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    
    # retriever = vectordb.as_retriever() 
    # retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 2}) 
    # retriever = vectordb.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": .5})
    retriever = _build_self_query_retriever(vectordb)
    memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=mongo_history, return_messages=True)
    conversation_qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        memory=memory,
        verbose=True,
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        max_tokens_limit=350)
    return conversation_qa_chain


def _build_self_query_retriever(vectorstore):
    metadata_field_info = [
        AttributeInfo(
                name="bank",
                description="The alias name of the bank, seperated by comma",
                type="string",
            ),
            AttributeInfo(
                name="card_name",
                description="The name of the credit card",
                type="string",
            ),
            AttributeInfo(
                name="url",
                description="The link of the credit card",
                type="string",
            ),
    ]
    document_content_description = "The metadata of the credit card information"
    llm = OpenAI(temperature=0)
    retriever = SelfQueryRetriever.from_llm(
        llm, vectorstore, document_content_description, metadata_field_info, verbose=True, enable_limit=True
    )
    return retriever


def _get_distinct_source_and_cards():
    """
    Getting distinct source and link
    """
    pipeline = [{"$group": {"_id": {"source": "$source", "card_name": "$card_name"}}}]
    result = mongo_collection.aggregate(pipeline)
    
    source_dict = {}
    for doc in result:
        source = doc['_id']['source']
        card_name = doc['_id']['card_name']
        
        if source in source_dict:
            source_dict[source].append(card_name)
        else:
            source_dict[source] = [card_name]
    
    source_list = []
    for i in source_dict:
        source_list.append({'銀行名稱':i, '卡片名稱':source_dict[i]})

    return source_list



if __name__ == '__main__':
    src = _get_distinct_source_and_cards() 
    print(str(src))   
    # print('。'.join(src))
