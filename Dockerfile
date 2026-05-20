FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY wheels ./wheels/
RUN pip install --no-cache-dir --no-index ./wheels -r requirements.txt

COPY proto/     proto/
COPY *.py       ./

COPY models/embeddings.npz models/embeddings.npz

ENV GRPC_PORT=50051 \
    MODEL_DIR=/app/models

EXPOSE 50051

CMD ["python", "main.py"]