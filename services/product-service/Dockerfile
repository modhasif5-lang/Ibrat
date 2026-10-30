FROM python:3.11-slim-bookworm

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries 10 -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory and make entrypoint executable
RUN mkdir -p /app/uploads && chmod +x entrypoint.sh

EXPOSE 8002

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
