from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from mutagen import File as MutagenFile
from app.core.database import get_db
from app.models.models import Track, TrackAnalysis, CuePoint
from app.schemas.schemas import (
    TrackResponse, TrackCreate, CuePointCreate, CuePointResponse,
    SpotifyImportRequest, SpotifyImportResponse
)
from app.services.audio_analysis import AudioAnalysisService
from app.services.spotify_integration import SpotifyIntegrationService
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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

@router.post("/import/spotify", response_model=SpotifyImportResponse)
async def import_from_spotify(
    request: SpotifyImportRequest,
    db: Session = Depends(get_db)
):
    """Import tracks from Spotify playlist, album, or track"""
    try:
        # Initialize Spotify service
        spotify_service = SpotifyIntegrationService()
        
        # Import tracks from Spotify
        spotify_tracks = spotify_service.import_from_url(request.url)
        
        if not spotify_tracks:
            raise HTTPException(status_code=404, detail="No tracks found at the provided URL")
        
        imported_count = 0
        matched_count = 0
        errors = []
        
        # Try to match with existing local tracks if requested
        if request.match_local:
            for track_info in spotify_tracks:
                try:
                    # Search for existing track by title and artist
                    existing_track = db.query(Track).filter(
                        Track.title.ilike(f"%{track_info['title']}%"),
                        Track.artist.ilike(f"%{track_info['artist']}%")
                    ).first()
                    
                    if existing_track:
                        # Update existing track with Spotify metadata
                        if track_info.get('bpm') and not existing_track.bpm:
                            existing_track.bpm = track_info['bpm']
                        if track_info.get('key') and not existing_track.key:
                            existing_track.key = track_info['key']
                        if track_info.get('energy') and not existing_track.energy:
                            existing_track.energy = track_info['energy']
                        
                        db.commit()
                        matched_count += 1
                        logger.info(f"Matched Spotify track: {track_info['title']}")
                    else:
                        logger.info(f"No local match for: {track_info['title']}")
                
                except Exception as e:
                    error_msg = f"Error matching {track_info.get('title', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        imported_count = len(spotify_tracks)
        
        logger.info(f"Spotify import complete: {imported_count} tracks, {matched_count} matched")
        
        return SpotifyImportResponse(
            imported_count=imported_count,
            matched_count=matched_count,
            tracks=spotify_tracks,
            errors=errors
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Spotify import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Spotify import failed: {str(e)}")
