# Reader

Standalone text reader deployed at reader.nmc.ovh.

Features:
- Paste arbitrary text and read it with natural Edge TTS.
- Normal mode or client-side Sin referencias cleanup.
- Browser SpeechSynthesis fallback.
- Playback controls, speed and font-size settings.
- Continuous server playback with smaller internal TTS parts, multi-part lookahead and double-buffered audio preloading.
- TTS cache with automatic expiry.
- No dependency on JW Reader or jw.org.

Runtime: FastAPI + Edge TTS in Docker. The service is attached to the existing frontend Docker network and is published only through the NMC nginx/WAF reverse proxy.

Deploy: pushes to main can deploy with the Deploy to VPS GitHub Actions workflow when repository variable READER_AUTO_DEPLOY=true.

Development checks: pip install -e '.[dev]', ruff check . and pytest -q. Pull requests also build the Docker image in CI.

Required GitHub Actions secrets: VPS_HOST, VPS_USER, VPS_SSH_KEY, VPS_PORT and VPS_PROJECT_PATH. VPS_PROJECT_PATH should normally be /home/debian/www/reader.
