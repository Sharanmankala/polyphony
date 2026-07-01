from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


SessionStatus = Literal["active", "archived"]
AssetType = Literal["image"]


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class ProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    creative_goal: str = Field(min_length=1, max_length=500)


class ProjectResponse(BaseModel):
    id: str
    title: str
    creative_goal: str
    created_at: datetime


class SessionCreateRequest(BaseModel):
    project_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=120)


class SessionResponse(BaseModel):
    id: str
    project_id: str
    title: str
    status: SessionStatus
    created_at: datetime


class ImageAssetResponse(BaseModel):
    id: str
    project_id: str
    session_id: str
    asset_type: AssetType
    original_filename: str
    stored_filename: str
    stored_path: str
    content_type: str
    size_bytes: int
    created_at: datetime


class ProjectDetailResponse(ProjectResponse):
    session_ids: list[str]
    asset_ids: list[str]


class SessionDetailResponse(SessionResponse):
    asset_ids: list[str]


class StoreData(BaseModel):
    projects: list[ProjectResponse] = Field(default_factory=list)
    sessions: list[SessionResponse] = Field(default_factory=list)
    assets: list[ImageAssetResponse] = Field(default_factory=list)
