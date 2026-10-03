from __future__ import annotations

import json
from pathlib import Path

import cv2
from scenedetect import AdaptiveDetector, detect

from .models import ExtractionResult, Slide


def format_timestamp(seconds: float) -> str:
    total_ms = round(seconds * 1000)
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def _safe_job_id(value: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in value).strip("-_")
    if not safe:
        raise ValueError("job_id must contain at least one letter or number")
    return safe


def extract_slides(video: Path, output_root: Path, job_id: str, min_scene_len: int = 15) -> ExtractionResult:
    if not video.is_file():
        raise FileNotFoundError(f"Video not found: {video}")

    job_id = _safe_job_id(job_id)
    job_dir = output_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    scenes = detect(str(video), AdaptiveDetector(min_scene_len=min_scene_len), show_progress=False)
    if not scenes:
        raise RuntimeError("No scenes were detected in the video")

    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise RuntimeError(f"OpenCV could not open {video.name}")

    slides: list[Slide] = []
    try:
        for index, (start, _end) in enumerate(scenes, start=1):
            seconds = start.get_seconds()
            capture.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
            ok, frame = capture.read()
            if not ok:
                continue

            filename = f"slide_{index:04d}.jpg"
            destination = job_dir / filename
            if not cv2.imwrite(str(destination), frame):
                raise RuntimeError(f"Could not write {destination}")

            slides.append(Slide(
                number=index,
                timestamp_seconds=seconds,
                timestamp=format_timestamp(seconds),
                image=filename,
            ))
    finally:
        capture.release()

    manifest = job_dir / "manifest.json"
    result = ExtractionResult(
        job_id=job_id,
        video=video.name,
        scene_count=len(scenes),
        slides=slides,
        manifest=str(manifest),
    )
    manifest.write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")
    return result
