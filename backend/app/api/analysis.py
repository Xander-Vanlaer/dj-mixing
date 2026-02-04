from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.database import get_db
from app.models.models import Track, TrackAnalysis
from app.schemas.schemas import TrackAnalysisResponse
from app.services.audio_analysis import AudioAnalysisService

router = APIRouter()

@router.get("/{track_id}", response_model=TrackAnalysisResponse)
async def get_track_analysis(track_id: int, db: Session = Depends(get_db)):
    """Get detailed analysis for a track"""
    analysis = db.query(TrackAnalysis).filter(TrackAnalysis.track_id == track_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.post("/{track_id}/reanalyze", response_model=TrackAnalysisResponse)
async def reanalyze_track(track_id: int, db: Session = Depends(get_db)):
    """Re-analyze a track"""
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Re-analyze
    analysis_result = AudioAnalysisService.analyze_track(track.file_path)
    
    # Update track
    track.bpm = analysis_result['bpm']
    track.key = analysis_result['key']
    track.energy = analysis_result['energy_level']
    track.waveform_data = analysis_result['waveform_data']
    
    # Update or create analysis
    analysis = db.query(TrackAnalysis).filter(TrackAnalysis.track_id == track_id).first()
    if analysis:
        analysis.bpm = analysis_result['bpm']
        analysis.key = analysis_result['key']
        analysis.camelot_key = analysis_result['camelot_key']
        analysis.energy_level = analysis_result['energy_level']
        analysis.structure = analysis_result['structure']
        analysis.beat_positions = analysis_result['beat_positions']
        analysis.spectral_centroid = analysis_result['spectral_centroid']
        analysis.spectral_rolloff = analysis_result['spectral_rolloff']
    else:
        analysis = TrackAnalysis(
            track_id=track_id,
            bpm=analysis_result['bpm'],
            key=analysis_result['key'],
            camelot_key=analysis_result['camelot_key'],
            energy_level=analysis_result['energy_level'],
            structure=analysis_result['structure'],
            beat_positions=analysis_result['beat_positions'],
            spectral_centroid=analysis_result['spectral_centroid'],
            spectral_rolloff=analysis_result['spectral_rolloff']
        )
        db.add(analysis)
    
    db.commit()
    db.refresh(analysis)
    
    return analysis

@router.get("/{track_id}/compatible")
async def get_compatible_tracks(
    track_id: int,
    bpm_tolerance: float = 10.0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get tracks compatible for mixing with the given track"""
    # Get source track analysis
    source_analysis = db.query(TrackAnalysis).filter(TrackAnalysis.track_id == track_id).first()
    if not source_analysis:
        raise HTTPException(status_code=404, detail="Track analysis not found")
    
    # Get all other tracks with analysis
    all_tracks = db.query(Track).join(TrackAnalysis).all()
    
    # Convert to dict format for analysis service
    tracks_data = []
    for track in all_tracks:
        tracks_data.append({
            'id': track.id,
            'title': track.title,
            'artist': track.artist,
            'bpm': track.analysis.bpm if track.analysis else None,
            'camelot_key': track.analysis.camelot_key if track.analysis else None,
            'energy_level': track.analysis.energy_level if track.analysis else None
        })
    
    source_data = {
        'track_id': track_id,
        'bpm': source_analysis.bpm,
        'camelot_key': source_analysis.camelot_key
    }
    
    # Get compatible tracks
    compatible = AudioAnalysisService.get_compatible_tracks(
        source_data,
        tracks_data,
        bpm_tolerance=bpm_tolerance
    )
    
    return compatible[:limit]
