# Base Python image
FROM python:3.11-slim

# System deps (optional: build tools if needed later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy sources
COPY orchestrator /app/orchestrator
COPY agents /app/agents
COPY config /app/config
COPY ui /app/ui
COPY PROJECT.md README.md /app/

# Install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Default command: run Seeker API with uvicorn
ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config/config.json
EXPOSE 8000
CMD ["uvicorn", "orchestrator.api:app_factory", "--factory", "--host", "0.0.0.0", "--port", "8000"]
