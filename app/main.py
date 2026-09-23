import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import __version__, settings
from app.models import TTSRequest, TTSResponse
from app.tts import audio_service

STATIC = Path("/app/static")

@asynccontextmanager
async def lifespan(_: FastAPI):
    await asyncio.to_thread(audio_service.cleanup_expired)
    task = asyncio.create_task(audio_service.cleanup_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

app = FastAPI(title="Reader", version=__version__, lifespan=lifespan)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path in {"/", "/index.html", "/app.js", "/sw.js"}:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "reader", "version": __version__}

@app.post("/api/tts", response_model=TTSResponse)
async def synthesize(request: TTSRequest) -> TTSResponse:
    try:
        key, _, cached = await audio_service.get_audio(
            request.text, rate=request.rate, volume=request.volume
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"TTS failed: {exc}") from exc
    return TTSResponse(key=key, audio_url=f"/api/audio/{key}.mp3", cached=cached)

@app.get("/api/audio/{filename}")
async def audio(filename: str) -> FileResponse:
    if not filename.endswith(".mp3"):
        raise HTTPException(status_code=404)
    key = filename[:-4]
    if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
        raise HTTPException(status_code=404)
    path = settings.AUDIO_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="audio/mpeg", filename=filename)

app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
