# Use official Python slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5002

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser /app
USER appuser

# Run Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "app:app"]