import os
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain, ConversationalRetrievalChain, ConversationChain
from langchain.memory import ConversationBufferMemory


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

 
persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: “text-davinci-003”
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
  

def load_data():
    # human_message_prompt = HumanMessagePromptTemplate(
    #     prompt=PromptTemplate(
    #         template="What is a good name for a company that makes {product}?",
    #         input_variables=["product"],
    #     )
    # )
    # chat_prompt_template = ChatPromptTemplate.from_messages([human_message_prompt])
    chat_prompt_template = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """
                你是一個親切且優秀的聊天機器人，擁有台灣各家銀行的信用卡介紹與優惠資訊。
                請依使用者提問的語言回答他的問題，預設是繁體中文。
                回答內容以條列式呈現，字數最多不要超過300字。
                當你無法理解使用者的提問時，請引導使用者作出更詳細的提問。
                當資料庫中完全沒有相關資訊時，請回答「抱歉，我目前沒有這個問題的相關資訊。您可以調整您的提問，或是詢問我其他問題。」
                """
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
    )
    # chat_prompt_template = PromptTemplate(
    #     input_variables=["chat_history", "question"],
    #     template = """
    #     你是一個親切且優秀的聊天機器人，擁有台灣各家銀行的信用卡介紹與優惠資訊。
    #     請依使用者提問的語言回答他的問題，預設是繁體中文。
    #     回答內容以條列式呈現，字數最多不要超過300字。
    #     當無法理解使用者的提問時，請引導使用者作出更詳細的提問。
    #     當資料庫中完全沒有相關資訊時，請回答「抱歉，我目前沒有這個問題的相關資訊。您可以調整您的提問，或是詢問我其他問題。」
    #     歷史對話紀錄:{chat_history}
    #     Human:{question}
    #     """
    # )
    # 4. Now we can load the persisted database from disk
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    
    retriever = vectordb.as_retriever() # retriever = vectordb.as_retriever(search_kwargs={"k": 2}) 
    # memory_key的chat_history参数要跟前面的历史消息模板参数对应，`return_messages=True` 参数目的是返回langchain封装的对话消息格式
    # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=retriever, 
        # memory=memory,
        verbose=True,
        # chain_type="stuff",
        condense_question_prompt=chat_prompt_template 
        )
    
    return conversation_qa_chain

    # qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever,
    #                                 #  chain_type_kwargs={"prompt": PromptTemplate(
    #                                 #             template=template,
    #                                 #             input_variables=["summaries", "question"],
    #                                 #         ),
    #                                 #     }, 
    #                                  return_source_documents=True, verbose=True)
    # return qa


if __name__ == '__main__':
    # qa_database = load_data()
    # query = "Richart 利上加利是什麼" #"同意申請卡號速取是什麼" "Richart 利上加利是什麼"
    # result = qa_database(query)
    # print(result)
    pass