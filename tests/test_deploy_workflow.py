from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "deploy.yml"


def test_deploy_initializes_runtime_data_through_container_root():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "mkdir -p data/audio" not in workflow
    assert "docker compose build reader" in workflow
    assert "docker compose run --rm --no-deps --user 0:0 reader sh -c" in workflow
    assert "mkdir -p /data/audio && chown -R 10001:10001 /data" in workflow
    assert "docker compose up -d --no-build --remove-orphans" in workflow
