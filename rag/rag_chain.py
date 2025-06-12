from langchain.chains import RetrievalQA
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import os
import textwrap
from dotenv import load_dotenv

load_dotenv()

# ✅ 임베딩 모델 & 벡터스토어 로드
vectorstore = Chroma(
    persist_directory="vectorstore",
    embedding_function=OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY"))
)

# ✅ LLM 로드
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# ✅ 프롬프트 템플릿 정의
qa_prompt = PromptTemplate.from_template(textwrap.dedent("""
    당신은 개발문서에 기반하여 질문에 답하는 전문 ai dev assistant 입니다.

    - 문서에서 유사하거나 관련 있는 내용을 참고하여 단계별로 설명하세요.
    - 직접적인 문장이 없더라도, 문맥상 유추 가능한 경우는 '문서에 따르면...'의 형식으로 정리해 주세요.
    - 단, 완전히 문서에 없는 경우에는 '문서에 없는 내용이라 답변 드릴 수 없습니다.'라고 말하세요.

    [문서 내용]
    {context}

    [질문]
    {question}

    [개발자 답변]
"""))

# ✅ RAG 체인 생성 (프롬프트 지정)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff",
    chain_type_kwargs={"prompt": qa_prompt},
    return_source_documents=True
)

# ✅ 쿼리 실행 함수


def run_rag_chain(query: str):
    result = qa_chain.invoke(query)
    return {
        "answer": result["result"],
        "sources": [doc.metadata for doc in result["source_documents"]]
    }
