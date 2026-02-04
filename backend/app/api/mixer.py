from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Mix, Track
from app.schemas.schemas import MixCreate, MixResponse

router = APIRouter()

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

@router.post("/auto-mix")
async def generate_auto_mix(
    seed_tracks: List[int],
    duration_minutes: int = 60,
    mood: str = "energetic",
    db: Session = Depends(get_db)
):
    """
    Generate an automatic mix based on seed tracks and preferences
    This is a simplified version - full implementation would use ML/AI
    """
    # Get seed tracks
    seeds = db.query(Track).filter(Track.id.in_(seed_tracks)).all()
    if not seeds:
        raise HTTPException(status_code=404, detail="Seed tracks not found")
    
    # For MVP, just return the seed tracks in order
    # TODO: Implement intelligent track selection and ordering
    tracklist = [
        {
            'track_id': track.id,
            'start_time': idx * 180,  # 3 min per track for now
            'title': track.title,
            'artist': track.artist
        }
        for idx, track in enumerate(seeds)
    ]
    
    return {
        "suggested_tracklist": tracklist,
        "total_duration": len(tracklist) * 180,
        "mood": mood
    }
