FROM python:3.10-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt || true

# 전체 프로젝트 복사
COPY . .

# 불필요한 캐시 제거
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]