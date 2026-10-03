from __future__ import annotations

import json
import os
from pathlib import Path

from fastmcp import FastMCP

from .extractor import extract_slides as run_extraction

INPUT_DIR = Path(os.getenv("INPUT_DIR", "/data/input")).resolve()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/data/output")).resolve()
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8000"))

mcp = FastMCP("Video Slides MCP")


def _input_video(name: str) -> Path:
    candidate = (INPUT_DIR / name).resolve()
    if candidate.parent != INPUT_DIR:
        raise ValueError("video_path must be a file directly inside the input directory")
    if not candidate.is_file():
        raise FileNotFoundError(f"Input video not found: {name}")
    return candidate


@mcp.tool
def list_input_videos() -> list[str]:
    """List video files available in the mounted input directory."""
    extensions = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}
    if not INPUT_DIR.exists():
        return []
    return sorted(p.name for p in INPUT_DIR.iterdir() if p.is_file() and p.suffix.lower() in extensions)


@mcp.tool
def extract_slides(video_path: str, job_id: str, min_scene_len: int = 15) -> dict:
    """Detect presentation scene changes and extract representative slide images."""
    video = _input_video(video_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return run_extraction(video, OUTPUT_DIR, job_id, min_scene_len).model_dump()


@mcp.tool
def list_extractions() -> list[str]:
    """List existing extraction job directories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(p.name for p in OUTPUT_DIR.iterdir() if p.is_dir())


@mcp.tool
def get_extraction(job_id: str) -> dict:
    """Read the manifest for a previous extraction job."""
    manifest = (OUTPUT_DIR / job_id / "manifest.json").resolve()
    if OUTPUT_DIR not in manifest.parents or not manifest.is_file():
        raise FileNotFoundError(f"Extraction not found: {job_id}")
    return json.loads(manifest.read_text(encoding="utf-8"))


def main() -> None:
    mcp.run(transport="http", host=HOST, port=PORT)


if __name__ == "__main__":
    main()
