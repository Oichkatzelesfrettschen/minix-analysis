FROM python:3.11-slim

LABEL description="MCP Boot Profiler Server for MINIX Analysis"
LABEL maintainer="MINIX Analysis Project"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server implementation
COPY server.py .

# Expose MCP server port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default entrypoint
CMD ["python3", "-u", "server.py"]
