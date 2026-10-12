from fastapi import FastAPI

app = FastAPI(title="SEO Page Checker", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness endpoint used by Docker HEALTHCHECK, CI and monitors."""
    return {"status": "ok"}
