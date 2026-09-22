import os
from pathlib import Path

DATA_DIR = Path(os.getenv("READER_DATA_DIR", "/data"))
AUDIO_DIR = DATA_DIR / "audio"
EDGE_VOICE = os.getenv("READER_EDGE_VOICE", "es-ES-AlvaroNeural")
TTS_MAX_CHARS = int(os.getenv("READER_TTS_MAX_CHARS", "5000"))
AUDIO_CACHE_MAX_AGE_DAYS = int(os.getenv("READER_AUDIO_CACHE_MAX_AGE_DAYS", "1"))
AUDIO_CACHE_CLEANUP_INTERVAL_HOURS = int(
    os.getenv("READER_AUDIO_CACHE_CLEANUP_INTERVAL_HOURS", "6")
)
