
# Python runtime
FROM python:3.11-slim

WORKDIR /app

# Install frontend dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy Streamlit application
COPY app.py .

# Streamlit configuration
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
