
FROM python:3.11-slim

WORKDIR /app

ENV HF_HOME=/app/huggingface
ENV PYTHONUNBUFFERED=1

# Install CPU-only PyTorch
RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir torch \
    --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Download the embedding model during the Docker build
RUN python -c "from langchain_huggingface import HuggingFaceEmbeddings; HuggingFaceEmbeddings(model_name='HarishMaths/Hotel-Policy-Embedding', model_kwargs={'device':'cpu'}, encode_kwargs={'normalize_embeddings':True})"

# Copy the Flask application and serialized FAISS database
COPY app.py .
COPY rag_utils.py .
COPY faiss_index/ ./faiss_index/

# Use the cached embedding model at runtime
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

EXPOSE 7860

CMD ["gunicorn", "-w", "1", "--timeout", "120", "-b", "0.0.0.0:7860", "app:rag_api"]
