"""
Auto-mixing service for DJ Mixing Platform
Automatically creates DJ mixes by selecting compatible tracks and calculating transitions
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.models import Track, TrackAnalysis
from app.services.audio_analysis import AudioAnalysisService
import random
import logging

logger = logging.getLogger(__name__)


class AutoMixerService:
    """Service for automatically generating DJ mixes"""
    
    @staticmethod
    def generate_auto_mix(
        db: Session,
        start_track_id: Optional[int] = None,
        target_duration_minutes: int = 60,
        bpm_tolerance: float = 6.0,
        energy_variation: float = 0.3
    ) -> Dict:
        """
        Generate an automatic DJ mix
        
        Args:
            db: Database session
            start_track_id: ID of starting track (random if None)
            target_duration_minutes: Target mix duration in minutes
            bpm_tolerance: BPM tolerance for track selection
            energy_variation: Allowed energy level variation (0-1)
        
        Returns:
            Dict with tracklist, transitions, and metadata
        """
        # Get all tracks with analysis
        tracks_with_analysis = (
            db.query(Track)
            .join(TrackAnalysis)
            .filter(TrackAnalysis.bpm.isnot(None))
            .all()
        )
        
        if not tracks_with_analysis:
            raise ValueError("No analyzed tracks available for auto-mixing")
        
        # Select starting track
        if start_track_id:
            current_track = db.query(Track).filter(Track.id == start_track_id).first()
            if not current_track or not current_track.analysis:
                raise ValueError("Start track not found or not analyzed")
        else:
            # Pick a random track with medium-high energy to start
            suitable_starters = [
                t for t in tracks_with_analysis 
                if t.analysis.energy_level and t.analysis.energy_level > 0.5
            ]
            if not suitable_starters:
                suitable_starters = tracks_with_analysis
            current_track = random.choice(suitable_starters)
        
        logger.info(f"Starting auto-mix with track: {current_track.title}")
        
        # Initialize mix data
        target_duration_seconds = target_duration_minutes * 60
        tracklist = []
        transitions = []
        total_duration = 0.0
        used_track_ids = set()
        
        # Add first track
        first_transition = AutoMixerService._calculate_transition_point(current_track)
        tracklist.append({
            'track_id': current_track.id,
            'title': current_track.title,
            'artist': current_track.artist,
            'bpm': current_track.analysis.bpm,
            'key': current_track.analysis.camelot_key,
            'energy': current_track.analysis.energy_level,
            'start_time': 0.0,
            'mix_in_point': first_transition['mix_in_point'],
            'mix_out_point': first_transition['mix_out_point']
        })
        total_duration = current_track.duration
        used_track_ids.add(current_track.id)
        
        # Build the mix
        max_iterations = 50  # Prevent infinite loops
        iteration = 0
        
        while total_duration < target_duration_seconds and iteration < max_iterations:
            iteration += 1
            
            # Find compatible next track
            next_track = AutoMixerService._find_next_track(
                current_track,
                tracks_with_analysis,
                used_track_ids,
                bpm_tolerance,
                energy_variation
            )
            
            if not next_track:
                logger.info("No more compatible tracks found, ending mix")
                break
            
            # Calculate transition
            transition = AutoMixerService._calculate_transition(
                current_track,
                next_track,
                total_duration
            )
            
            transitions.append(transition)
            
            # Add next track to tracklist
            next_transition = AutoMixerService._calculate_transition_point(next_track)
            tracklist.append({
                'track_id': next_track.id,
                'title': next_track.title,
                'artist': next_track.artist,
                'bpm': next_track.analysis.bpm,
                'key': next_track.analysis.camelot_key,
                'energy': next_track.analysis.energy_level,
                'start_time': transition['start_time'],
                'mix_in_point': next_transition['mix_in_point'],
                'mix_out_point': next_transition['mix_out_point']
            })
            
            # Update state
            total_duration += next_track.duration - transition['overlap_duration']
            used_track_ids.add(next_track.id)
            current_track = next_track
        
        logger.info(f"Auto-mix complete: {len(tracklist)} tracks, {total_duration:.1f}s")
        
        return {
            'tracklist': tracklist,
            'transitions': transitions,
            'total_duration': total_duration,
            'track_count': len(tracklist),
            'metadata': {
                'target_duration': target_duration_minutes,
                'bpm_tolerance': bpm_tolerance,
                'energy_variation': energy_variation
            }
        }
    
    @staticmethod
    def _find_next_track(
        current_track: Track,
        available_tracks: List[Track],
        used_track_ids: set,
        bpm_tolerance: float,
        energy_variation: float
    ) -> Optional[Track]:
        """Find the next compatible track for the mix"""
        if not current_track.analysis:
            return None
        
        # Convert tracks to dict format for compatibility checking
        tracks_data = []
        for track in available_tracks:
            if track.id in used_track_ids or not track.analysis:
                continue
            tracks_data.append({
                'id': track.id,
                'bpm': track.analysis.bpm,
                'camelot_key': track.analysis.camelot_key,
                'energy_level': track.analysis.energy_level
            })
        
        if not tracks_data:
            return None
        
        current_data = {
            'track_id': current_track.id,
            'bpm': current_track.analysis.bpm,
            'camelot_key': current_track.analysis.camelot_key
        }
        
        # Get compatible tracks
        compatible = AudioAnalysisService.get_compatible_tracks(
            current_data,
            tracks_data,
            bpm_tolerance=bpm_tolerance
        )
        
        # Filter by energy level if current track has energy data
        if current_track.analysis.energy_level:
            current_energy = current_track.analysis.energy_level
            compatible = [
                c for c in compatible
                if c['track'].get('energy_level') and
                abs(c['track']['energy_level'] - current_energy) <= energy_variation
            ]
        
        if not compatible:
            return None
        
        # Get the best match
        best_match_id = compatible[0]['track']['id']
        return next((t for t in available_tracks if t.id == best_match_id), None)
    
    @staticmethod
    def _calculate_transition_point(track: Track) -> Dict:
        """Calculate mix in/out points for a track"""
        duration = track.duration
        
        # Default transition points
        # Mix in: Start of main section (skip intro)
        # Mix out: Before outro section
        
        if track.analysis and track.analysis.structure:
            structure = track.analysis.structure
            mix_in = structure.get('intro', {}).get('end', duration * 0.1)
            outro_start = structure.get('outro', {}).get('start', duration * 0.85)
            mix_out = outro_start
        else:
            # Default: 10% in, 85% out
            mix_in = duration * 0.1
            mix_out = duration * 0.85
        
        return {
            'mix_in_point': mix_in,
            'mix_out_point': mix_out
        }
    
    @staticmethod
    def _calculate_transition(
        track_a: Track,
        track_b: Track,
        current_time: float
    ) -> Dict:
        """Calculate transition between two tracks"""
        # Get transition points
        track_a_points = AutoMixerService._calculate_transition_point(track_a)
        track_b_points = AutoMixerService._calculate_transition_point(track_b)
        
        # Calculate BPM-based transition duration
        # Faster transitions for similar BPMs, longer for different ones
        if track_a.analysis and track_b.analysis:
            bpm_diff = abs(track_a.analysis.bpm - track_b.analysis.bpm)
            # 8-32 seconds based on BPM difference
            overlap_duration = min(32, max(8, 8 + bpm_diff))
        else:
            overlap_duration = 16  # Default 16 seconds
        
        # Track A mix out point in mix timeline
        track_a_mix_out = current_time - (track_a.duration - track_a_points['mix_out_point'])
        
        # Track B starts during Track A outro
        track_b_start = track_a_mix_out - overlap_duration
        
        return {
            'from_track_id': track_a.id,
            'to_track_id': track_b.id,
            'start_time': track_b_start,
            'overlap_duration': overlap_duration,
            'from_track_out_point': track_a_points['mix_out_point'],
            'to_track_in_point': track_b_points['mix_in_point'],
            'type': 'crossfade'
        }
