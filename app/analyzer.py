"""On-page SEO analysis: parse HTML into facts, then evaluate weighted rules against them.

Pure functions only (no network, no disk), so everything here is easy to unit test.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from html.parser import HTMLParser

from app.models import AnalyzeResponse, Finding, PageStats, Severity

logger = logging.getLogger(__name__)

WORD_RE = re.compile(r"\w+", re.UNICODE)
SKIP_TEXT_TAGS = frozenset({"script", "style", "noscript", "template"})
HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})

TITLE_RANGE = (30, 60)
DESCRIPTION_RANGE = (70, 160)
MIN_WORDS = 300


@dataclass
class PageFacts:
    """Everything the rules need to know about a page, extracted in one pass."""

    lang: str | None = None
    title: str | None = None
    meta: dict[str, str] = field(default_factory=dict)
    canonical: str | None = None
    heading_levels: list[int] = field(default_factory=list)
    image_count: int = 0
    images_missing_alt: int = 0
    word_count: int = 0

    @property
    def description(self) -> str:
        return self.meta.get("description", "")


class _FactsParser(HTMLParser):
    """Collects PageFacts while parsing. Tolerant of malformed HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.facts = PageFacts()
        self._in_head = False
        self._in_title = False
        self._title_seen = False
        self._title_parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {name: (value or "") for name, value in attrs}
        if tag == "html":
            self.facts.lang = a.get("lang", "").strip() or None
        elif tag == "head":
            self._in_head = True
        elif tag == "title" and not self._title_seen:
            self._title_seen = True
            self._in_title = True
        elif tag == "meta":
            name = a.get("name", "").strip().lower()
            if name and name not in self.facts.meta:
                self.facts.meta[name] = a.get("content", "").strip()
        elif tag == "link":
            rel = a.get("rel", "").lower().split()
            href = a.get("href", "").strip()
            if "canonical" in rel and href:
                self.facts.canonical = href
        elif tag in HEADING_TAGS:
            self.facts.heading_levels.append(int(tag[1]))
        elif tag == "img":
            self.facts.image_count += 1
            if "alt" not in a:  # empty alt="" is valid for decorative images
                self.facts.images_missing_alt += 1
        elif tag in SKIP_TEXT_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self._in_head = False
        elif tag == "title":
            self._in_title = False
        elif tag in SKIP_TEXT_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        elif not self._in_head and self._skip_depth == 0:
            self.facts.word_count += len(WORD_RE.findall(data))

    def finish(self) -> PageFacts:
        if self._title_seen:
            self.facts.title = " ".join("".join(self._title_parts).split())
        return self.facts


# --------------------------------------------------------------------------- rules

CheckResult = tuple[bool, str]


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    severity: Severity
    weight: int
    check: Callable[[PageFacts], CheckResult]


def _range_check(value: int, bounds: tuple[int, int], label: str) -> CheckResult:
    low, high = bounds
    if low <= value <= high:
        return True, f"{label} is {value} characters (ideal {low}-{high})."
    return False, f"{label} is {value} characters; aim for {low}-{high}."


def _title_present(f: PageFacts) -> CheckResult:
    if f.title:
        return True, "Page has a <title>."
    return False, "Missing <title>. Add a unique, descriptive title."


def _title_length(f: PageFacts) -> CheckResult:
    if not f.title:
        return False, "No title to measure."
    return _range_check(len(f.title), TITLE_RANGE, "Title")


def _meta_description_present(f: PageFacts) -> CheckResult:
    if f.description:
        return True, "Page has a meta description."
    return False, "Missing meta description. Summarize the page in one or two sentences."


def _meta_description_length(f: PageFacts) -> CheckResult:
    if not f.description:
        return False, "No meta description to measure."
    return _range_check(len(f.description), DESCRIPTION_RANGE, "Meta description")


def _single_h1(f: PageFacts) -> CheckResult:
    count = f.heading_levels.count(1)
    if count == 1:
        return True, "Page has exactly one <h1>."
    if count == 0:
        return False, "Missing <h1>. Add one main heading."
    return False, f"Found {count} <h1> tags; use exactly one."


def _heading_order(f: PageFacts) -> CheckResult:
    levels = f.heading_levels
    for prev, cur in zip(levels, levels[1:], strict=False):
        if cur - prev > 1:
            return False, f"Heading level jumps from h{prev} to h{cur}; do not skip levels."
    return True, "Heading levels are in order."


def _images_alt(f: PageFacts) -> CheckResult:
    if f.images_missing_alt == 0:
        return True, "All images have an alt attribute."
    return False, f"{f.images_missing_alt} of {f.image_count} images are missing alt text."


def _canonical_present(f: PageFacts) -> CheckResult:
    if f.canonical:
        return True, "Canonical link is set."
    return False, 'Missing <link rel="canonical">. It helps avoid duplicate-content issues.'


def _lang_attribute(f: PageFacts) -> CheckResult:
    if f.lang:
        return True, f"Page language is declared ({f.lang})."
    return False, "Missing lang attribute on <html>."


def _viewport_meta(f: PageFacts) -> CheckResult:
    if "viewport" in f.meta:
        return True, "Viewport meta tag is present."
    return False, "Missing viewport meta tag; the page may not be mobile friendly."


def _word_count(f: PageFacts) -> CheckResult:
    if f.word_count >= MIN_WORDS:
        return True, f"Page has {f.word_count} words."
    return False, f"Page has {f.word_count} words; thin content (aim for {MIN_WORDS}+)."


def _indexable(f: PageFacts) -> CheckResult:
    tokens = {t.strip() for t in f.meta.get("robots", "").lower().split(",")}
    if tokens & {"noindex", "none"}:
        return False, "Robots meta tag blocks indexing (noindex)."
    return True, "Page is indexable."


RULES: tuple[Rule, ...] = (
    Rule("title_present", "Page has a non-empty <title>", "error", 15, _title_present),
    Rule("title_length", "Title is 30-60 characters", "warning", 5, _title_length),
    Rule(
        "meta_description_present",
        "Page has a meta description",
        "error",
        15,
        _meta_description_present,
    ),
    Rule(
        "meta_description_length",
        "Meta description is 70-160 characters",
        "warning",
        5,
        _meta_description_length,
    ),
    Rule("single_h1", "Page has exactly one <h1>", "error", 15, _single_h1),
    Rule("heading_order", "Heading levels do not skip", "warning", 5, _heading_order),
    Rule("images_alt", "Every <img> has an alt attribute", "warning", 10, _images_alt),
    Rule("canonical_present", "Canonical link is set", "info", 5, _canonical_present),
    Rule("lang_attribute", "<html> declares a lang", "warning", 5, _lang_attribute),
    Rule("viewport_meta", "Viewport meta tag is present", "warning", 5, _viewport_meta),
    Rule("word_count", "Page has at least 300 words", "info", 10, _word_count),
    Rule("indexable", "Robots meta does not block indexing", "error", 5, _indexable),
)


# ------------------------------------------------------------------------ analysis


def grade_for(score: int) -> str:
    for threshold, grade in ((90, "A"), (75, "B"), (60, "C"), (40, "D")):
        if score >= threshold:
            return grade
    return "F"


def extract_facts(html: str) -> PageFacts:
    parser = _FactsParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception:  # html.parser is lenient, but never let odd input crash the API
        logger.warning("HTML parsing stopped early; analyzing partial result", exc_info=True)
    return parser.finish()


def analyze_html(html: str) -> AnalyzeResponse:
    facts = extract_facts(html)

    findings: list[Finding] = []
    earned = 0
    for rule in RULES:
        passed, message = rule.check(facts)
        if passed:
            earned += rule.weight
        findings.append(
            Finding(rule_id=rule.id, passed=passed, severity=rule.severity, message=message)
        )

    total = sum(rule.weight for rule in RULES)
    score = round(100 * earned / total)
    passed_count = sum(1 for f in findings if f.passed)

    return AnalyzeResponse(
        score=score,
        grade=grade_for(score),
        passed=passed_count,
        failed=len(findings) - passed_count,
        stats=PageStats(
            title=facts.title,
            title_length=len(facts.title or ""),
            meta_description_length=len(facts.description),
            h1_count=facts.heading_levels.count(1),
            image_count=facts.image_count,
            images_missing_alt=facts.images_missing_alt,
            word_count=facts.word_count,
        ),
        findings=findings,
    )
