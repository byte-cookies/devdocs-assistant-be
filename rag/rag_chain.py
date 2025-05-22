from langchain.chains import RetrievalQA
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
load_dotenv()


vectorstore = Chroma( # 벡터 DB 로드
    persist_directory="vectorstore",
    embedding_function=OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY"))
)

llm = ChatOpenAI( #llm 모델 로드
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff",
    return_source_documents=True
)


def run_rag_chain(query: str):
    result = qa_chain.invoke(query)
    return {
        "answer": result["result"],
        "sources": [doc.metadata for doc in result["source_documents"]]
    }
