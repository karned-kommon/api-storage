FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=True \
    PORT=8000 \
    WORKERS=1 \
    API_NAME=api-recipe \
    API_TAG_NAME=recipes

ENV KEYCLOAK_HOST="" \
    KEYCLOAK_REALM="" \
    KEYCLOAK_CLIENT_ID="" \
    KEYCLOAK_CLIENT_SECRET=""

ENV REDIS_HOST="" \
    REDIS_PORT="" \
    REDIS_DB="" \
    REDIS_PASSWORD=""

ENV URL_API_GATEWAY=""

WORKDIR /app

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY --from=builder /install /usr/local
COPY . ./

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}"]