from langchain.text_splitter import CharacterTextSplitter
from datetime import datetime
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# 전역에서 한 번만 생성
embedding_model = OpenAIEmbeddings()
vectordb = Chroma(persist_directory="./vectorstore", embedding_function=embedding_model)

# url 중복 확인
def is_url_already_embedded(url: str) -> bool:
    results = vectordb.similarity_search("url_check_dummy", k=20)
    for doc in results:
        if doc.metadata.get("source") == url:
            return True
    return False

def split_text(text: str, chunk_size=1200, chunk_overlap=200):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

def embed_split_text(text: str, url: str):
    if not text.strip():
        print("빈 텍스트입니다. 저장을 생략합니다.")
        return

    chunks = split_text(text)
    print(f"[INFO] URL: {url}")
    print(f"[INFO] 텍스트 분할 개수: {len(chunks)}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    docs = [Document(page_content=chunk, metadata={"source": url, "timestamp": now}) for chunk in chunks]

    vectordb.add_documents(docs)
    vectordb.persist()
