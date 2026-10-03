# Video Slides MCP

Dockerized FastMCP server that extracts presentation slides from videos using PySceneDetect and OpenCV.

## Stack

- FastMCP
- PySceneDetect
- OpenCV
- FFmpeg
- Docker / Docker Compose

## Run

```bash
mkdir -p data/input data/output
cp /path/to/presentation.mp4 data/input/
docker compose up --build -d
```

MCP endpoint: `http://localhost:8000/mcp`

Input is mounted read-only and the container runs as a non-root user.
