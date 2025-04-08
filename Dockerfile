# Use official Python slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=WebApp.app \
    FLASK_ENV=production

# Expose port
EXPOSE 5002

# Install system dependencies (required for cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser && \
    chown -R appuser /app
USER appuser

# Runtime command (choose one)
# Option 1: For production with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "WebApp.app:app"]

# Option 2: For development (uncomment if needed)
# CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5002"]

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "WebApp.app:app"]