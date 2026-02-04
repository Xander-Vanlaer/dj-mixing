from pydantic import BaseModel
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
