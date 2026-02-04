from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import Mix, Track
from app.schemas.schemas import MixCreate, MixResponse, AutoMixRequest, AutoMixResponse
from app.services.auto_mixer import AutoMixerService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/mixes", response_model=MixResponse)
async def create_mix(mix: MixCreate, db: Session = Depends(get_db)):
    """Create a new mix"""
    # Calculate total duration from tracklist
    total_duration = 0.0
    for track_item in mix.tracklist:
        track_id = track_item.get('track_id')
        track = db.query(Track).filter(Track.id == track_id).first()
        if track:
            total_duration += track.duration
    
    new_mix = Mix(
        name=mix.name,
        description=mix.description,
        duration=total_duration,
        tracklist=mix.tracklist,
        transitions=mix.transitions
    )
    
    db.add(new_mix)
    db.commit()
    db.refresh(new_mix)
    
    return new_mix

@router.get("/mixes", response_model=List[MixResponse])
async def list_mixes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all mixes"""
    mixes = db.query(Mix).offset(skip).limit(limit).all()
    return mixes

@router.get("/mixes/{mix_id}", response_model=MixResponse)
async def get_mix(mix_id: int, db: Session = Depends(get_db)):
    """Get a specific mix"""
    mix = db.query(Mix).filter(Mix.id == mix_id).first()
    if not mix:
        raise HTTPException(status_code=404, detail="Mix not found")
    return mix

@router.delete("/mixes/{mix_id}")
async def delete_mix(mix_id: int, db: Session = Depends(get_db)):
    """Delete a mix"""
    mix = db.query(Mix).filter(Mix.id == mix_id).first()
    if not mix:
        raise HTTPException(status_code=404, detail="Mix not found")
    
    db.delete(mix)
    db.commit()
    
    return {"message": "Mix deleted successfully"}

@router.post("/auto-mix", response_model=AutoMixResponse)
async def generate_auto_mix(
    request: AutoMixRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an automatic mix based on preferences
    Uses intelligent track selection based on BPM, key compatibility, and energy levels
    """
    try:
        logger.info(f"Generating auto-mix: {request.dict()}")
        
        # Generate the auto-mix
        result = AutoMixerService.generate_auto_mix(
            db=db,
            start_track_id=request.start_track_id,
            target_duration_minutes=request.duration_minutes,
            bpm_tolerance=request.bpm_tolerance,
            energy_variation=request.energy_variation
        )
        
        logger.info(f"Auto-mix generated: {result['track_count']} tracks")
        
        return AutoMixResponse(
            tracklist=result['tracklist'],
            transitions=result['transitions'],
            total_duration=result['total_duration'],
            track_count=result['track_count'],
            metadata=result['metadata']
        )
    except ValueError as e:
        logger.error(f"Auto-mix generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Auto-mix generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate auto-mix")
