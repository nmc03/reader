import asyncio
import hashlib
import logging
import time
from pathlib import Path

import edge_tts

from app import settings

logger = logging.getLogger("uvicorn.error")

class AudioService:
    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}

    @staticmethod
    def _ensure_dir() -> None:
        settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _managed(path: Path) -> bool:
        stem = path.stem
        return (
            not path.is_symlink()
            and path.is_file()
            and path.suffix == ".mp3"
            and len(stem) == 64
            and all(c in "0123456789abcdef" for c in stem)
        )

    def cleanup_expired(self) -> tuple[int, int]:
        if settings.AUDIO_CACHE_MAX_AGE_DAYS <= 0:
            return 0, 0
        self._ensure_dir()
        cutoff = time.time() - settings.AUDIO_CACHE_MAX_AGE_DAYS * 86400
        files = size = 0
        for path in settings.AUDIO_DIR.iterdir():
            try:
                if not self._managed(path) or path.stat().st_mtime >= cutoff:
                    continue
                size += path.stat().st_size
                path.unlink()
                files += 1
            except FileNotFoundError:
                pass
            except OSError:
                logger.exception("Could not remove cached audio %s", path)
        return files, size

    async def cleanup_loop(self) -> None:
        interval = max(settings.AUDIO_CACHE_CLEANUP_INTERVAL_HOURS, 1) * 3600
        while True:
            try:
                deleted, bytes_deleted = await asyncio.to_thread(self.cleanup_expired)
                if deleted:
                    logger.info("event=cache_cleanup files=%d bytes=%d", deleted, bytes_deleted)
            except Exception:
                logger.exception("Audio cache cleanup failed")
            await asyncio.sleep(interval)

    async def get_audio(self, text: str, rate: str, volume: str) -> tuple[str, Path, bool]:
        if len(text) > settings.TTS_MAX_CHARS:
            raise ValueError(f"Text exceeds {settings.TTS_MAX_CHARS} characters")
        self._ensure_dir()
        key = hashlib.sha256(
            f"{settings.EDGE_VOICE}\0{rate}\0{volume}\0{text}".encode()
        ).hexdigest()
        path = settings.AUDIO_DIR / f"{key}.mp3"
        if path.exists() and path.stat().st_size > 0:
            return key, path, True

        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            if path.exists() and path.stat().st_size > 0:
                return key, path, True
            tmp = Path(f"{path}.tmp")
            try:
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=settings.EDGE_VOICE,
                    rate=rate,
                    volume=volume,
                )
                await communicate.save(str(tmp))
                tmp.replace(path)
            finally:
                tmp.unlink(missing_ok=True)
        return key, path, False

audio_service = AudioService()
