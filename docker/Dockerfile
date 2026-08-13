FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration files first for optimal Docker layer caching
COPY pyproject.toml README.md ./

# Enable bytecode compilation and sync project dependencies (excluding dev tools)
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --no-install-project --no-dev

# Copy application source code
COPY . .

# Sync the full project package into the virtual environment
RUN uv sync --no-dev

# Set environment variables and path bindings
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV AUTH_DIR_PATH=/app/auth

CMD ["sleep", "infinity"]
