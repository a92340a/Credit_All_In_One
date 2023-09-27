import os
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

 
persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: “text-davinci-003”
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
  

def load_data():
    # prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say GTGTGTGTGTGTGTGTGTG, don't try to make up an answer.
    #     {context}
    #     Question: {question}
    #     Helpful Answer:"""
    # QA_PROMPT = ChatPromptTemplate(
    #     template=prompt_template, input_variables=['context',"question"]
    # )
    # 4. Now we can load the persisted database from disk
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
    
    retriever = vectordb.as_retriever() # retriever = vectordb.as_retriever(search_kwargs={"k": 2}) # retriever = index.vectorstore.as_retriever()
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever,
                                    #  chain_type_kwargs={"prompt": PromptTemplate(
                                    #             template=template,
                                    #             input_variables=["summaries", "question"],
                                    #         ),
                                    #     }, 
                                     return_source_documents=True, verbose=True)
    return qa


if __name__ == '__main__':
    qa_database = load_data()
    query = "Richart 利上加利是什麼" #"同意申請卡號速取是什麼" "Richart 利上加利是什麼"
    result = qa_database(query)
    print(result)