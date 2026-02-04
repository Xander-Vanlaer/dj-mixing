from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TrackBase(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None

class TrackCreate(TrackBase):
    pass

class TrackResponse(TrackBase):
    id: int
    duration: float
    file_path: str
    file_format: str
    file_size: int
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    waveform_data: Optional[List[float]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TrackAnalysisResponse(BaseModel):
    id: int
    track_id: int
    bpm: Optional[float] = None
    key: Optional[str] = None
    camelot_key: Optional[str] = None
    energy_level: Optional[float] = None
    structure: Optional[dict] = None
    beat_positions: Optional[List[float]] = None
    analyzed_at: datetime
    
    class Config:
        from_attributes = True

class CuePointCreate(BaseModel):
    position: float
    label: Optional[str] = None
    color: Optional[str] = None

class CuePointResponse(BaseModel):
    id: int
    track_id: int
    position: float
    label: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class MixCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tracklist: List[dict]
    transitions: Optional[List[dict]] = None

class MixResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    duration: float
    tracklist: List[dict]
    transitions: Optional[List[dict]] = None
    export_path: Optional[str] = None
    export_format: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auto-mix schemas
class AutoMixRequest(BaseModel):
    start_track_id: Optional[int] = Field(None, description="Starting track ID (random if not provided)")
    duration_minutes: int = Field(60, ge=5, le=300, description="Target mix duration in minutes")
    bpm_tolerance: float = Field(6.0, ge=0, le=20, description="BPM tolerance for track selection")
    energy_variation: float = Field(0.3, ge=0, le=1, description="Allowed energy level variation")

class AutoMixResponse(BaseModel):
    tracklist: List[dict]
    transitions: List[dict]
    total_duration: float
    track_count: int
    metadata: dict

# Spotify import schemas
class SpotifyImportRequest(BaseModel):
    url: str = Field(..., description="Spotify URL (playlist, track, or album)")
    match_local: bool = Field(True, description="Try to match with local files")

class SpotifyTrackInfo(BaseModel):
    spotify_id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration_ms: int
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    preview_url: Optional[str] = None

class SpotifyImportResponse(BaseModel):
    imported_count: int
    matched_count: int
    tracks: List[SpotifyTrackInfo]
    errors: List[str] = []
