from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app.config import ensure_app_directories, settings
from app.models import (
    HealthResponse,
    ImageAssetResponse,
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectResponse,
    SessionCreateRequest,
    SessionDetailResponse,
    SessionResponse,
    StoreData,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Local backend for the Polyphony creative operating system.",
)


@app.on_event("startup")
def on_startup() -> None:
    ensure_app_directories()
    initialize_store_file()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
    )


@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(request: ProjectCreateRequest) -> ProjectResponse:
    store = load_store()

    project = ProjectResponse(
        id=generate_id("project"),
        title=request.title.strip(),
        creative_goal=request.creative_goal.strip(),
        created_at=current_time(),
    )

    store.projects.append(project)
    save_store(store)
    return project


@app.get("/projects", response_model=list[ProjectResponse])
def list_projects() -> list[ProjectResponse]:
    store = load_store()
    return store.projects


@app.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: str) -> ProjectDetailResponse:
    store = load_store()
    project = find_project_or_404(store, project_id)

    session_ids = [session.id for session in store.sessions if session.project_id == project_id]
    asset_ids = [asset.id for asset in store.assets if asset.project_id == project_id]

    return ProjectDetailResponse(
        id=project.id,
        title=project.title,
        creative_goal=project.creative_goal,
        created_at=project.created_at,
        session_ids=session_ids,
        asset_ids=asset_ids,
    )


@app.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(request: SessionCreateRequest) -> SessionResponse:
    store = load_store()
    find_project_or_404(store, request.project_id)

    session = SessionResponse(
        id=generate_id("session"),
        project_id=request.project_id,
        title=request.title.strip(),
        status="active",
        created_at=current_time(),
    )

    store.sessions.append(session)
    save_store(store)
    return session


@app.get("/sessions", response_model=list[SessionResponse])
def list_sessions(project_id: str | None = None) -> list[SessionResponse]:
    store = load_store()

    if project_id is None:
        return store.sessions

    find_project_or_404(store, project_id)
    return [session for session in store.sessions if session.project_id == project_id]


@app.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str) -> SessionDetailResponse:
    store = load_store()
    session = find_session_or_404(store, session_id)

    asset_ids = [asset.id for asset in store.assets if asset.session_id == session_id]

    return SessionDetailResponse(
        id=session.id,
        project_id=session.project_id,
        title=session.title,
        status=session.status,
        created_at=session.created_at,
        asset_ids=asset_ids,
    )


@app.post(
    "/sessions/{session_id}/images",
    response_model=ImageAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image_to_session(
    session_id: str,
    file: UploadFile = File(...),
) -> ImageAssetResponse:
    store = load_store()
    session = find_session_or_404(store, session_id)
    validate_upload(file)

    content = await file.read()
    validate_upload_size(content)

    original_filename = sanitize_filename(file.filename or "uploaded-image")
    suffix = Path(original_filename).suffix.lower()
    stored_filename = f"{uuid4().hex}{suffix}"
    stored_path = settings.images_dir / stored_filename
    stored_path.write_bytes(content)

    asset = ImageAssetResponse(
        id=generate_id("asset"),
        project_id=session.project_id,
        session_id=session.id,
        asset_type="image",
        original_filename=original_filename,
        stored_filename=stored_filename,
        stored_path=str(stored_path),
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        created_at=current_time(),
    )

    store.assets.append(asset)
    save_store(store)
    return asset


@app.get("/projects/{project_id}/assets", response_model=list[ImageAssetResponse])
def list_project_assets(project_id: str) -> list[ImageAssetResponse]:
    store = load_store()
    find_project_or_404(store, project_id)
    return [asset for asset in store.assets if asset.project_id == project_id]


def current_time() -> datetime:
    return datetime.now(UTC)


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def initialize_store_file() -> None:
    if settings.store_file.exists():
        return

    empty_store = StoreData()
    settings.store_file.write_text(
        empty_store.model_dump_json(indent=2),
        encoding="utf-8",
    )


def load_store() -> StoreData:
    try:
        raw_text = settings.store_file.read_text(encoding="utf-8")
        raw_data = json.loads(raw_text)
        return StoreData.model_validate(raw_data)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local store file is missing.",
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local store file is invalid JSON.",
        ) from exc


def save_store(store: StoreData) -> None:
    settings.store_file.write_text(
        store.model_dump_json(indent=2),
        encoding="utf-8",
    )


def find_project_or_404(store: StoreData, project_id: str) -> ProjectResponse:
    for project in store.projects:
        if project.id == project_id:
            return project

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Project '{project_id}' was not found.",
    )


def find_session_or_404(store: StoreData, session_id: str) -> SessionResponse:
    for session in store.sessions:
        if session.id == session_id:
            return session

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Session '{session_id}' was not found.",
    )


def validate_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename.",
        )

    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.allowed_image_extensions:
        allowed = ", ".join(settings.allowed_image_extensions)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type. Allowed extensions: {allowed}.",
        )


def validate_upload_size(content: bytes) -> None:
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is too large for the current local milestone.",
        )


def sanitize_filename(filename: str) -> str:
    """
    Keep uploaded filenames simple and safe for local storage.

    This is not perfect security, but it removes path traversal risk for this
    first milestone by keeping only the final filename component.
    """
    return Path(filename).name.replace(" ", "_")
