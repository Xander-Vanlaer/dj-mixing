"""
Spotify integration service for importing tracks and metadata
"""

from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from app.core.config import settings
import logging
import re

logger = logging.getLogger(__name__)


class SpotifyIntegrationService:
    """Service for integrating with Spotify API"""
    
    def __init__(self):
        """Initialize Spotify client"""
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            raise ValueError(
                "Spotify credentials not configured. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
            )
        
        auth_manager = SpotifyClientCredentials(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        logger.info("Spotify client initialized")
    
    def parse_spotify_url(self, url: str) -> Dict[str, str]:
        """
        Parse Spotify URL to extract type and ID
        
        Args:
            url: Spotify URL or URI
        
        Returns:
            Dict with 'type' (playlist/track/album) and 'id'
        """
        # Handle Spotify URIs (spotify:playlist:xxxxx)
        uri_pattern = r'spotify:(playlist|track|album):([a-zA-Z0-9]+)'
        uri_match = re.match(uri_pattern, url)
        if uri_match:
            return {
                'type': uri_match.group(1),
                'id': uri_match.group(2)
            }
        
        # Handle Spotify URLs (https://open.spotify.com/playlist/xxxxx)
        url_pattern = r'https?://open\.spotify\.com/(playlist|track|album)/([a-zA-Z0-9]+)'
        url_match = re.search(url_pattern, url)
        if url_match:
            return {
                'type': url_match.group(1),
                'id': url_match.group(2)
            }
        
        # Try as direct ID (assume track if no type specified)
        if re.match(r'^[a-zA-Z0-9]+$', url):
            return {
                'type': 'track',
                'id': url
            }
        
        raise ValueError(f"Invalid Spotify URL or URI: {url}")
    
    def import_from_url(self, url: str) -> List[Dict]:
        """
        Import tracks from Spotify URL (playlist, track, or album)
        
        Args:
            url: Spotify URL or URI
        
        Returns:
            List of track info dictionaries
        """
        parsed = self.parse_spotify_url(url)
        spotify_type = parsed['type']
        spotify_id = parsed['id']
        
        logger.info(f"Importing from Spotify {spotify_type}: {spotify_id}")
        
        if spotify_type == 'playlist':
            return self._import_playlist(spotify_id)
        elif spotify_type == 'track':
            return [self._import_track(spotify_id)]
        elif spotify_type == 'album':
            return self._import_album(spotify_id)
        else:
            raise ValueError(f"Unsupported Spotify type: {spotify_type}")
    
    def _import_playlist(self, playlist_id: str) -> List[Dict]:
        """Import all tracks from a Spotify playlist"""
        tracks = []
        results = self.sp.playlist_tracks(playlist_id)
        
        while results:
            for item in results['items']:
                if item['track']:  # Can be None for local files
                    track_info = self._extract_track_info(item['track'])
                    if track_info:
                        tracks.append(track_info)
            
            # Handle pagination
            if results['next']:
                results = self.sp.next(results)
            else:
                results = None
        
        logger.info(f"Imported {len(tracks)} tracks from playlist")
        return tracks
    
    def _import_album(self, album_id: str) -> List[Dict]:
        """Import all tracks from a Spotify album"""
        tracks = []
        results = self.sp.album_tracks(album_id)
        album_info = self.sp.album(album_id)
        
        while results:
            for item in results['items']:
                # Enrich with album info
                item['album'] = {
                    'name': album_info['name'],
                    'release_date': album_info.get('release_date')
                }
                track_info = self._extract_track_info(item)
                if track_info:
                    tracks.append(track_info)
            
            # Handle pagination
            if results['next']:
                results = self.sp.next(results)
            else:
                results = None
        
        logger.info(f"Imported {len(tracks)} tracks from album")
        return tracks
    
    def _import_track(self, track_id: str) -> Dict:
        """Import a single track from Spotify"""
        track = self.sp.track(track_id)
        return self._extract_track_info(track)
    
    def _extract_track_info(self, track: Dict) -> Optional[Dict]:
        """Extract relevant track information from Spotify track object"""
        if not track:
            return None
        
        try:
            # Get audio features (BPM, key, energy, etc.)
            audio_features = None
            try:
                audio_features = self.sp.audio_features([track['id']])[0]
            except Exception as e:
                logger.warning(f"Could not get audio features for {track['name']}: {e}")
            
            # Extract basic info
            track_info = {
                'spotify_id': track['id'],
                'title': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track.get('album', {}).get('name'),
                'duration_ms': track['duration_ms'],
                'preview_url': track.get('preview_url')
            }
            
            # Add audio features if available
            if audio_features:
                # BPM
                track_info['bpm'] = audio_features.get('tempo')
                
                # Key (convert from Spotify pitch class to note name)
                key_mapping = {
                    0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F',
                    6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
                }
                pitch_class = audio_features.get('key')
                mode = audio_features.get('mode')  # 0 = minor, 1 = major
                if pitch_class is not None and pitch_class >= 0:
                    note = key_mapping.get(pitch_class, 'C')
                    track_info['key'] = f"{note}{'m' if mode == 0 else ''}"
                
                # Energy and danceability (0-1 scale)
                track_info['energy'] = audio_features.get('energy')
                track_info['danceability'] = audio_features.get('danceability')
            
            return track_info
        
        except Exception as e:
            logger.error(f"Error extracting track info: {e}")
            return None
    
    def search_track(self, title: str, artist: str) -> Optional[Dict]:
        """
        Search for a track on Spotify
        
        Args:
            title: Track title
            artist: Artist name
        
        Returns:
            Track info if found, None otherwise
        """
        try:
            query = f"track:{title} artist:{artist}"
            results = self.sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                return self._extract_track_info(results['tracks']['items'][0])
            return None
        
        except Exception as e:
            logger.error(f"Error searching for track: {e}")
            return None
