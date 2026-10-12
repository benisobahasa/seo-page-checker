"""Pydantic schemas for the HTTP API."""

from typing import Literal

from pydantic import BaseModel, Field

from app.config import MAX_HTML_CHARS

Severity = Literal["error", "warning", "info"]

_EXAMPLE_HTML = "<html lang='en'><head><title>Hello</title></head><body><h1>Hi</h1></body></html>"


class AnalyzeRequest(BaseModel):
    html: str = Field(
        min_length=1,
        max_length=MAX_HTML_CHARS,
        description="Raw HTML of the page to analyze.",
    )

    model_config = {"json_schema_extra": {"examples": [{"html": _EXAMPLE_HTML}]}}


class RuleInfo(BaseModel):
    id: str
    description: str
    severity: Severity
    weight: int


class Finding(BaseModel):
    rule_id: str
    passed: bool
    severity: Severity
    message: str


class PageStats(BaseModel):
    title: str | None
    title_length: int
    meta_description_length: int
    h1_count: int
    image_count: int
    images_missing_alt: int
    word_count: int


class AnalyzeResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    grade: str
    passed: int
    failed: int
    stats: PageStats
    findings: list[Finding]
