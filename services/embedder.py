from langchain.text_splitter import CharacterTextSplitter
from datetime import datetime
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os
import json
from pathlib import Path

load_dotenv()

# 전역에서 한 번만 생성
embedding_model = OpenAIEmbeddings()
vectordb = Chroma(persist_directory="./vectorstore", embedding_function=embedding_model)
URL_INDEX_PATH = Path("./indexes_urls.json")

# === URL 인덱스 로드 ===
def load_url_index() -> set:  
    if URL_INDEX_PATH.exists():
        with open(URL_INDEX_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

# === URL 인덱스 저장 ===
def save_url_index(indexed_urls: set): 
    with open(URL_INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(indexed_urls), f, ensure_ascii=False, indent=2)    

# === URL 중복 검사 (중복 -> true) ===
def is_url_already_embedded(url: str) -> bool:
    indexed_urls = load_url_index()
    return url in indexed_urls

# === 텍스트 분할 ===
def split_text(text: str, chunk_size=1200, chunk_overlap=200):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)


# === 임베딩 및 저장
def embed_split_text(text: str, url: str):
    if not text.strip():
        print("빈 텍스트입니다. 저장을 생략합니다.")
        return

    if is_url_already_embedded(url):
        print(f"[SKIP] 이미 저장된 URL입니다: {url}")
        return

    chunks = split_text(text)
    print(f"[INFO] URL: {url}")
    print(f"[INFO] 텍스트 분할 개수: {len(chunks)}")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    docs = [Document(page_content=chunk, metadata={"source": url, "timestamp": now}) for chunk in chunks]

    vectordb.add_documents(docs)
    vectordb.persist()

    indexed_urls = load_url_index()
    indexed_urls.add(url)           # Set배열에 url 추가
    save_url_index(indexed_urls)
