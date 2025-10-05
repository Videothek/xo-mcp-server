# Use Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Python unbuffered
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies and small system deps for network tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    iproute2 \
    iputils-ping \
    curl \
  && pip install --no-cache-dir -r requirements.txt \
  && apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/*

# Copy the server code
COPY main.py .
COPY config.py .
COPY tools/*.py tools/

# Create non-root user and ensure /app owned by that user
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Default command to start the MCP server
CMD ["python", "main.py"]
