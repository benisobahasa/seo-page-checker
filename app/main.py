"""HTTP layer. Keep it thin: validation in models, logic in analyzer."""

import logging

from fastapi import FastAPI

from app import config
from app.analyzer import RULES, analyze_html
from app.models import AnalyzeRequest, AnalyzeResponse, RuleInfo

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SEO Page Checker",
    version="0.1.0",
    description="Analyze the HTML of a page and get an on-page SEO score with actionable findings.",
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness endpoint used by Docker HEALTHCHECK, CI and monitors."""
    return {"status": "ok"}


@app.get("/rules", response_model=list[RuleInfo], tags=["seo"])
def list_rules() -> list[RuleInfo]:
    """List every rule, its severity and its weight in the final score."""
    return [
        RuleInfo(id=r.id, description=r.description, severity=r.severity, weight=r.weight)
        for r in RULES
    ]


@app.post("/analyze", response_model=AnalyzeResponse, tags=["seo"])
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze raw HTML and return score, grade, stats and per-rule findings."""
    result = analyze_html(payload.html)
    logger.info("analyzed html chars=%d score=%d", len(payload.html), result.score)
    return result
