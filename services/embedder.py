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

# URL 중복 확인
def is_url_already_embedded(url: str) -> bool:
    results = vectordb.similarity_search("url_check_dummy", k=20)
    for doc in results:
        if doc.metadata.get("source") == url:
            return True
    return False

# 텍스트 분할 함수
def split_text(text: str, chunk_size=1200, chunk_overlap=200):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

# 문서 임베딩 및 저장
def embed_split_text(text: str, url: str, metadata: dict = None):
    if not text.strip():
        print("빈 텍스트입니다. 저장을 생략합니다.")
        return

    chunks = split_text(text)
    print(f"[INFO] URL: {url}")
    print(f"[INFO] 텍스트 분할 개수: {len(chunks)}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    final_metadata = {
        "source": url,
        "timestamp": now
    }

    # 외부에서 전달된 metadata가 있다면 병합
    if metadata:
        final_metadata.update(metadata)

    docs = [Document(page_content=chunk, metadata=final_metadata) for chunk in chunks]

    vectordb.add_documents(docs)
    vectordb.persist()