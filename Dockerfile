# Use Python 3.13.5 slim image for minimal footprint
FROM python:3.13.5-slim

# Set environment variables for MCP optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ASEPRITE_MCP_MODE=mcp

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set work directory
WORKDIR /app

# Copy only essential files
COPY requirements.txt ./
COPY aseprite_mcp/ ./aseprite_mcp/
COPY app.py ./

# Install core dependencies only
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for Aseprite files
RUN mkdir -p /app/projects /app/exports && \
    chown -R appuser:appuser /app

# Create mock Aseprite for testing (replace with real installation)
RUN echo '#!/bin/bash\necho "Aseprite mock v1.3.0"\necho "Arguments: $@"\nexit 0' > /usr/local/bin/aseprite && \
    chmod +x /usr/local/bin/aseprite

# Switch to non-root user
USER appuser

# Set environment variables
ENV ASEPRITE_PATH=/usr/local/bin/aseprite

# Default command - MCP mode only
CMD ["python", "-m", "aseprite_mcp"]

# Labels
LABEL org.opencontainers.image.title="Aseprite MCP Server" \
      org.opencontainers.image.description="Minimal MCP server for Aseprite" \
      org.opencontainers.image.version="0.3.0"
