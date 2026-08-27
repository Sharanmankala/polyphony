from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from app import config, main


def test_current_polyphony_api_flow(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    assets_dir = tmp_path / "assets"
    images_dir = assets_dir / "images"

    test_settings = replace(
        config.settings,
        base_dir=tmp_path,
        data_dir=data_dir,
        assets_dir=assets_dir,
        images_dir=images_dir,
        store_file=data_dir / "store.json",
    )

    monkeypatch.setattr(config, "settings", test_settings)
    monkeypatch.setattr(main, "settings", test_settings)

    with TestClient(main.app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        project = client.post(
            "/projects",
            json={
                "title": "Launch Film",
                "creative_goal": "Create a premium product reveal.",
            },
        )
        assert project.status_code == 201
        project_id = project.json()["id"]

        session = client.post(
            "/sessions",
            json={
                "project_id": project_id,
                "title": "Visual exploration",
            },
        )
        assert session.status_code == 201
        session_id = session.json()["id"]

        image = client.post(
            f"/sessions/{session_id}/images",
            files={
                "file": (
                    "reference.png",
                    b"test image content",
                    "image/png",
                )
            },
        )
        assert image.status_code == 201
        assert Path(image.json()["stored_path"]).exists()

        assets = client.get(f"/projects/{project_id}/assets")
        assert assets.status_code == 200
        assert len(assets.json()) == 1

        invalid_upload = client.post(
            f"/sessions/{session_id}/images",
            files={"file": ("notes.txt", b"not an image", "text/plain")},
        )
        assert invalid_upload.status_code == 400
