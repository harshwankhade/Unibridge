FROM python:3.11-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .
COPY database.py .
COPY models.py .
COPY seed.py .
COPY start.sh .
RUN chmod +x start.sh   # ensure executable on Linux regardless of Windows git attrs

EXPOSE 8001

# Auto-seed demo users then start the server
CMD ["sh", "start.sh"]
