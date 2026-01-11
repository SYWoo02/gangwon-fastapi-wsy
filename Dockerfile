# -------------------------------------------------------
# 빌드 스테이지: 의존성 설치
# -------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# 빌드에 필요한 툴 + uv 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libffi-dev && \
    pip install --no-cache-dir uv && \
    rm -rf /var/lib/apt/lists/*

# 의존성 정의 파일 복사
COPY pyproject.toml ./

# 가상환경(.venv)에 의존성 설치 (dev 제외)
RUN uv sync --no-dev --no-cache

# 애플리케이션 코드 복사
COPY . .

# -------------------------------------------------------
# 런타임 스테이지: 실행 전용 이미지
# -------------------------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 보안을 위한 non-root 사용자
RUN useradd -m appuser

# 빌더에서 만든 가상환경만 복사
COPY --from=builder /app/.venv /app/.venv

# 필요한 애플리케이션 파일만 복사
COPY --from=builder /app/main.py /app/main.py
COPY --from=builder /app/app /app/app
COPY --from=builder /app/infra /app/infra
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# venv를 기본 Python 환경으로 설정
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER appuser

# 👉 Ingress / Service / FastAPI 포트 통일
EXPOSE 8880

# 👉 FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8880"]