# Document Intelligence Refinery - Docker Image
# Multi-stage build for production

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install uv for fast package management
RUN pip install uv

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
COPY rubric ./rubric
COPY .gitignore ./

# Install Python dependencies
RUN uv pip install --system -e .

# Create non-root user for security
RUN useradd -m -u 1000 refinery && \
    chown -R refinery:refinery /app
USER refinery

# Expose API port (if running server)
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.api.server"]

---
# Development image (uncomment for local development)
# FROM base as development
# RUN uv pip install --system -e ".[dev]"
# CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

---
# Production build with OCI distribution
# FROM gcr.io/distroless/python3-debian11 as production
# COPY --from=base /app /app
# USER nonroot
# CMD ["python", "-m", "src.api.server"]
