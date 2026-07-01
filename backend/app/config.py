from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    base_dir: Path
    data_dir: Path
    assets_dir: Path
    images_dir: Path
    store_file: Path
    max_upload_size_bytes: int
    allowed_image_extensions: tuple[str, ...]


def build_settings() -> Settings:
    """
    Build local filesystem paths relative to this backend app.

    We keep settings explicit and small for now so the code stays easy to
    understand. Later we can move these values to environment variables when
    the project grows.
    """
    app_dir = Path(__file__).resolve().parent
    base_dir = app_dir.parent
    data_dir = base_dir / "data"
    assets_dir = base_dir / "assets"
    images_dir = assets_dir / "images"
    store_file = data_dir / "store.json"

    return Settings(
        app_name="Polyphony Backend",
        app_version="0.1.0",
        base_dir=base_dir,
        data_dir=data_dir,
        assets_dir=assets_dir,
        images_dir=images_dir,
        store_file=store_file,
        max_upload_size_bytes=10 * 1024 * 1024,
        allowed_image_extensions=(".png", ".jpg", ".jpeg", ".webp"),
    )


settings = build_settings()


def ensure_app_directories() -> None:
    """
    Create the local folders Polyphony needs for this first milestone.

    Current milestone only stores JSON metadata and uploaded image files.
    """
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.assets_dir.mkdir(parents=True, exist_ok=True)
    settings.images_dir.mkdir(parents=True, exist_ok=True)
