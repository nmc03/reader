from fastapi.testclient import TestClient

from app import settings
from app.main import app

def test_audio_is_content_addressed_and_immutable(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "AUDIO_DIR", tmp_path)
    key = "a" * 64
    (tmp_path / f"{key}.mp3").write_bytes(b"ID3test")
    with TestClient(app) as client:
        response = client.get(f"/api/audio/{key}.mp3")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"
    assert response.headers["content-type"].startswith("audio/mpeg")

def test_security_headers_include_csp():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert "media-src 'self' blob:" in response.headers["content-security-policy"]
