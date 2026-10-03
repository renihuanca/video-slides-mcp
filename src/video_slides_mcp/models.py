from pydantic import BaseModel


class Slide(BaseModel):
    number: int
    timestamp_seconds: float
    timestamp: str
    image: str


class ExtractionResult(BaseModel):
    job_id: str
    video: str
    scene_count: int
    slides: list[Slide]
    manifest: str
