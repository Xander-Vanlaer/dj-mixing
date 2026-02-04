import librosa
import numpy as np
import soundfile as sf
from typing import Dict, List, Optional, Tuple
import aubio

class AudioAnalysisService:
    """Service for analyzing audio files"""
    
    @staticmethod
    def analyze_track(file_path: str) -> Dict:
        """
        Comprehensive audio analysis
        Returns: dict with BPM, key, energy, waveform, etc.
        """
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=44100, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # BPM detection
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            bpm = float(tempo)
            
            # Beat positions in seconds
            beat_times = librosa.frames_to_time(beats, sr=sr)
            beat_positions = beat_times.tolist()
            
            # Key detection (using chroma features)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key_index = np.argmax(np.sum(chroma, axis=1))
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            detected_key = keys[key_index]
            
            # Camelot wheel mapping
            camelot_key = AudioAnalysisService._get_camelot_key(detected_key, key_index)
            
            # Energy level (RMS energy)
            rms = librosa.feature.rms(y=y)[0]
            energy_level = float(np.mean(rms))
            
            # Spectral features
            spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
            
            # Generate waveform data (downsampled for visualization)
            waveform_samples = 1000
            waveform_data = AudioAnalysisService._generate_waveform(y, waveform_samples)
            
            # Detect track structure
            structure = AudioAnalysisService._detect_structure(y, sr, beat_times)
            
            return {
                'duration': duration,
                'bpm': bpm,
                'key': detected_key,
                'camelot_key': camelot_key,
                'energy_level': energy_level,
                'beat_positions': beat_positions,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'waveform_data': waveform_data,
                'structure': structure
            }
        except Exception as e:
            raise Exception(f"Error analyzing track: {str(e)}")
    
    @staticmethod
    def _generate_waveform(audio: np.ndarray, num_samples: int = 1000) -> List[float]:
        """Generate downsampled waveform for visualization"""
        # Take absolute values for envelope
        audio_abs = np.abs(audio)
        
        # Downsample by averaging chunks
        chunk_size = len(audio_abs) // num_samples
        if chunk_size == 0:
            chunk_size = 1
            
        waveform = []
        for i in range(0, len(audio_abs), chunk_size):
            chunk = audio_abs[i:i + chunk_size]
            if len(chunk) > 0:
                waveform.append(float(np.mean(chunk)))
        
        # Normalize
        max_val = max(waveform) if waveform else 1.0
        if max_val > 0:
            waveform = [v / max_val for v in waveform]
        
        return waveform[:num_samples]
    
    @staticmethod
    def _get_camelot_key(key: str, key_index: int) -> str:
        """Convert musical key to Camelot wheel notation"""
        # Simplified Camelot wheel mapping (major keys)
        camelot_map = {
            'C': '8B', 'C#': '3B', 'D': '10B', 'D#': '5B',
            'E': '12B', 'F': '7B', 'F#': '2B', 'G': '9B',
            'G#': '4B', 'A': '11B', 'A#': '6B', 'B': '1B'
        }
        return camelot_map.get(key, '1A')
    
    @staticmethod
    def _detect_structure(y: np.ndarray, sr: int, beat_times: np.ndarray) -> Dict:
        """
        Detect track structure (intro, verse, chorus, outro)
        Simplified version - uses energy and spectral features
        """
        # Split track into segments
        total_duration = len(y) / sr
        
        # Simple heuristic-based structure detection
        intro_duration = min(total_duration * 0.15, 30)  # First 15% or 30s
        outro_duration = min(total_duration * 0.15, 30)  # Last 15% or 30s
        
        structure = {
            'intro': {'start': 0, 'end': intro_duration},
            'main': {'start': intro_duration, 'end': total_duration - outro_duration},
            'outro': {'start': total_duration - outro_duration, 'end': total_duration}
        }
        
        return structure
    
    @staticmethod
    def get_compatible_tracks(track_analysis: Dict, all_tracks: List[Dict], 
                             bpm_tolerance: float = 10.0) -> List[Dict]:
        """
        Find tracks compatible for mixing based on BPM and key
        """
        compatible = []
        source_bpm = track_analysis.get('bpm', 0)
        source_key = track_analysis.get('camelot_key', '')
        
        for track in all_tracks:
            if track.get('id') == track_analysis.get('track_id'):
                continue  # Skip self
                
            target_bpm = track.get('bpm', 0)
            target_key = track.get('camelot_key', '')
            
            # BPM compatibility
            bpm_diff = abs(source_bpm - target_bpm)
            if bpm_diff > bpm_tolerance and bpm_diff > source_bpm * 0.1:
                continue
            
            # Key compatibility (adjacent keys on Camelot wheel)
            key_compatible = AudioAnalysisService._are_keys_compatible(source_key, target_key)
            
            compatibility_score = 100 - (bpm_diff / bpm_tolerance * 50)
            if key_compatible:
                compatibility_score += 50
            
            compatible.append({
                'track': track,
                'compatibility_score': min(100, compatibility_score),
                'bpm_diff': bpm_diff,
                'key_compatible': key_compatible
            })
        
        # Sort by compatibility score
        compatible.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return compatible
    
    @staticmethod
    def _are_keys_compatible(key1: str, key2: str) -> bool:
        """Check if two keys are harmonically compatible on Camelot wheel"""
        if not key1 or not key2:
            return False
        
        # Same key
        if key1 == key2:
            return True
        
        # Adjacent keys (simplified - just check if numbers are ±1)
        try:
            num1 = int(key1[:-1])
            num2 = int(key2[:-1])
            letter1 = key1[-1]
            letter2 = key2[-1]
            
            # Same letter, adjacent number
            if letter1 == letter2 and abs(num1 - num2) <= 1:
                return True
            
            # Same number, different letter (relative major/minor)
            if num1 == num2 and letter1 != letter2:
                return True
        except:
            pass
        
        return False
