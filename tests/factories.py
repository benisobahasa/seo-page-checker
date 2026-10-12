"""Helpers to build HTML pages for tests."""

DEFAULT_TITLE = "Complete Guide to Testing SEO Checkers"
DEFAULT_DESCRIPTION = (
    "A practical, plain-language guide that explains how on-page SEO checks work "
    "and how to fix the most common problems."
)


def build_page(
    *,
    title: str | None = DEFAULT_TITLE,
    description: str | None = DEFAULT_DESCRIPTION,
    lang: str | None = "en",
    canonical: bool = True,
    viewport: bool = True,
    robots: str | None = None,
    h1_count: int = 1,
    body_words: int = 320,
    extra_body: str = "",
) -> str:
    head: list[str] = []
    if title is not None:
        head.append(f"<title>{title}</title>")
    if description is not None:
        head.append(f'<meta name="description" content="{description}">')
    if viewport:
        head.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    if robots:
        head.append(f'<meta name="robots" content="{robots}">')
    if canonical:
        head.append('<link rel="canonical" href="https://example.com/page">')

    lang_attr = f' lang="{lang}"' if lang else ""
    words = " ".join(["word"] * body_words)
    body = (
        "<h1>Main heading</h1>" * h1_count
        + "<h2>Section</h2>"
        + f"<p>{words}</p>"
        + '<img src="chart.png" alt="A chart">'
        + extra_body
    )
    return f"<html{lang_attr}><head>{''.join(head)}</head><body>{body}</body></html>"
