# Multi-stage build for smaller image
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.10-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY prompts/ ./prompts/
COPY data/processed/ ./data/processed/

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH

# Create necessary directories
RUN mkdir -p data/raw data/interim data/processed figures report

# Default command
CMD ["python", "-m", "src.metrics.aui", "--demo"]