from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    duration = Column(Float, nullable=False)  # in seconds
    file_path = Column(String, nullable=False, unique=True)
    file_format = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    
    # Analysis data
    bpm = Column(Float, nullable=True)
    key = Column(String, nullable=True)
    energy = Column(Float, nullable=True)
    danceability = Column(Float, nullable=True)
    
    # Waveform data (JSON array)
    waveform_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analysis = relationship("TrackAnalysis", back_populates="track", uselist=False)
    cue_points = relationship("CuePoint", back_populates="track")

class TrackAnalysis(Base):
    __tablename__ = "track_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), unique=True)
    
    # Detailed analysis
    bpm = Column(Float, nullable=True)
    key = Column(String, nullable=True)
    camelot_key = Column(String, nullable=True)
    energy_level = Column(Float, nullable=True)
    
    # Structure detection (JSON)
    structure = Column(JSON, nullable=True)  # intro, verse, chorus, etc.
    
    # Beat grid
    beat_positions = Column(JSON, nullable=True)  # Array of beat timestamps
    
    # Spectral analysis
    spectral_centroid = Column(Float, nullable=True)
    spectral_rolloff = Column(Float, nullable=True)
    
    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    track = relationship("Track", back_populates="analysis")

class CuePoint(Base):
    __tablename__ = "cue_points"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"))
    position = Column(Float, nullable=False)  # Position in seconds
    label = Column(String, nullable=True)
    color = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    track = relationship("Track", back_populates="cue_points")

class Mix(Base):
    __tablename__ = "mixes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Float, nullable=False)
    
    # Mix configuration (JSON)
    tracklist = Column(JSON, nullable=False)  # Array of track IDs with timestamps
    transitions = Column(JSON, nullable=True)  # Transition data between tracks
    
    # Export
    export_path = Column(String, nullable=True)
    export_format = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
