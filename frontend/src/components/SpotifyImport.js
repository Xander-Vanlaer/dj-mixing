import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Paper,
} from '@mui/material';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import { tracksAPI } from '../services/api';

const SpotifyImport = ({ onImportComplete }) => {
  const [spotifyUrl, setSpotifyUrl] = useState('');
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleImport = async () => {
    if (!spotifyUrl.trim()) {
      setError('Please enter a Spotify URL');
      return;
    }

    setImporting(true);
    setError(null);
    setResult(null);

    try {
      const importResult = await tracksAPI.importFromSpotify(spotifyUrl, true);
      setResult(importResult);
      
      // Notify parent component to reload tracks if any were matched
      if (importResult.matched_count > 0 && onImportComplete) {
        onImportComplete();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import from Spotify');
      console.error('Spotify import error:', err);
    } finally {
      setImporting(false);
    }
  };

  const formatDuration = (ms) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <MusicNoteIcon />
        Import from Spotify
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Paste Spotify playlist, album, or track URL"
          value={spotifyUrl}
          onChange={(e) => setSpotifyUrl(e.target.value)}
          disabled={importing}
          size="small"
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleImport}
          disabled={importing || !spotifyUrl.trim()}
          sx={{ minWidth: 120 }}
        >
          {importing ? <CircularProgress size={24} /> : 'Import'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Paper sx={{ p: 2, bgcolor: '#2a2a2a' }}>
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Import Summary
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip
                label={`${result.imported_count} tracks found`}
                color="info"
                size="small"
              />
              <Chip
                label={`${result.matched_count} matched locally`}
                color="success"
                size="small"
              />
            </Box>
          </Box>

          {result.tracks && result.tracks.length > 0 && (
            <>
              <Typography variant="subtitle2" gutterBottom>
                Tracks:
              </Typography>
              <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
                {result.tracks.map((track, index) => (
                  <ListItem
                    key={track.spotify_id || index}
                    sx={{
                      bgcolor: '#1f1f1f',
                      mb: 0.5,
                      borderRadius: 1,
                    }}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          {track.title}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {track.artist}
                          </Typography>
                          {track.bpm && (
                            <Chip label={`${Math.round(track.bpm)} BPM`} size="small" />
                          )}
                          {track.key && (
                            <Chip label={track.key} size="small" />
                          )}
                          {track.energy && (
                            <Chip
                              label={`Energy: ${(track.energy * 100).toFixed(0)}%`}
                              size="small"
                            />
                          )}
                          <Typography variant="caption" color="text.secondary">
                            {formatDuration(track.duration_ms)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}

          {result.errors && result.errors.length > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="caption">
                {result.errors.length} error(s) occurred during import
              </Typography>
            </Alert>
          )}
        </Paper>
      )}

      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Note: Spotify tracks will be matched with your local library. Upload matching audio files
        to use them in your mixes.
      </Typography>
    </Box>
  );
};

export default SpotifyImport;
