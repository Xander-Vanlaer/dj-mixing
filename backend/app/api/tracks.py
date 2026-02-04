from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from mutagen import File as MutagenFile
from app.core.database import get_db
from app.models.models import Track, TrackAnalysis, CuePoint
from app.schemas.schemas import TrackResponse, TrackCreate, CuePointCreate, CuePointResponse
from app.services.audio_analysis import AudioAnalysisService
from app.core.config import settings

router = APIRouter()

ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.m4a'}

@router.post("/upload", response_model=TrackResponse)
async def upload_track(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and analyze a new track"""
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract metadata using mutagen
    try:
        audio_file = MutagenFile(file_path, easy=True)
        title = audio_file.get('title', [file.filename])[0] if audio_file else file.filename
        artist = audio_file.get('artist', ['Unknown'])[0] if audio_file else 'Unknown'
        album = audio_file.get('album', [None])[0] if audio_file else None
        genre = audio_file.get('genre', [None])[0] if audio_file else None
    except:
        title = file.filename
        artist = 'Unknown'
        album = None
        genre = None
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Analyze track
    analysis_result = AudioAnalysisService.analyze_track(file_path)
    
    # Create track record
    track = Track(
        title=title,
        artist=artist,
        album=album,
        genre=genre,
        duration=analysis_result['duration'],
        file_path=file_path,
        file_format=file_ext,
        file_size=file_size,
        bpm=analysis_result['bpm'],
        key=analysis_result['key'],
        energy=analysis_result['energy_level'],
        waveform_data=analysis_result['waveform_data']
    )
    
    db.add(track)
    db.commit()
    db.refresh(track)
    
    # Create detailed analysis record
    track_analysis = TrackAnalysis(
        track_id=track.id,
        bpm=analysis_result['bpm'],
        key=analysis_result['key'],
        camelot_key=analysis_result['camelot_key'],
        energy_level=analysis_result['energy_level'],
        structure=analysis_result['structure'],
        beat_positions=analysis_result['beat_positions'],
        spectral_centroid=analysis_result['spectral_centroid'],
        spectral_rolloff=analysis_result['spectral_rolloff']
    )
    
    db.add(track_analysis)
    db.commit()
    
    return track

@router.get("/", response_model=List[TrackResponse])
async def list_tracks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all tracks"""
    tracks = db.query(Track).offset(skip).limit(limit).all()
    return tracks

@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(track_id: int, db: Session = Depends(get_db)):
    """Get a specific track"""
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track

@router.delete("/{track_id}")
async def delete_track(track_id: int, db: Session = Depends(get_db)):
    """Delete a track"""
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Delete file
    if os.path.exists(track.file_path):
        os.remove(track.file_path)
    
    # Delete from database
    db.delete(track)
    db.commit()
    
    return {"message": "Track deleted successfully"}

@router.post("/{track_id}/cue-points", response_model=CuePointResponse)
async def add_cue_point(
    track_id: int,
    cue_point: CuePointCreate,
    db: Session = Depends(get_db)
):
    """Add a cue point to a track"""
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    cue = CuePoint(
        track_id=track_id,
        position=cue_point.position,
        label=cue_point.label,
        color=cue_point.color
    )
    
    db.add(cue)
    db.commit()
    db.refresh(cue)
    
    return cue

@router.get("/{track_id}/cue-points", response_model=List[CuePointResponse])
async def get_cue_points(track_id: int, db: Session = Depends(get_db)):
    """Get all cue points for a track"""
    cue_points = db.query(CuePoint).filter(CuePoint.track_id == track_id).all()
    return cue_points

@router.get("/{track_id}/audio")
async def get_track_audio(track_id: int, db: Session = Depends(get_db)):
    """Serve audio file for a track"""
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    if not os.path.exists(track.file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(track.file_path, media_type="audio/mpeg")
