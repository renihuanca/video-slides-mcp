FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    INPUT_DIR=/data/input \
    OUTPUT_DIR=/data/output \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN mkdir -p /data/input /data/output && chown -R appuser:appuser /data /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -fsS http://127.0.0.1:8000/mcp/ >/dev/null || exit 1
CMD ["video-slides-mcp"]
