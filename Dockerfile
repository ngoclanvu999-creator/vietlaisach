FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure directories exist
RUN mkdir -p input output static templates

# Environment configurations
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8501
ENV AUTO_OPEN_BROWSER=0

EXPOSE 8501

CMD ["python", "app.py"]
