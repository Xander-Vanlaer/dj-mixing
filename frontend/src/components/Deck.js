import React, { useRef, useEffect, useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Slider,
  Paper,
  Menu,
  MenuItem,
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import LibraryMusicIcon from '@mui/icons-material/LibraryMusic';
import useMixerStore from '../contexts/mixerStore';

const Deck = ({ deckId, label }) => {
  const deck = useMixerStore((state) => state[deckId]);
  const tracks = useMixerStore((state) => state.tracks);
  const { togglePlay, setVolume, setPitch, loadTrack } = useMixerStore();
  
  const [anchorEl, setAnchorEl] = useState(null);
  const audioRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (deck.track && audioRef.current) {
      // Load audio file
      const audioUrl = `/api/tracks/${deck.track.id}/audio`; // This endpoint needs to be added
      // For now, we'll use a placeholder
      // audioRef.current.src = audioUrl;
    }
  }, [deck.track]);

  useEffect(() => {
    // Handle play/pause
    if (audioRef.current) {
      if (deck.isPlaying) {
        audioRef.current.play().catch(e => console.error('Error playing:', e));
      } else {
        audioRef.current.pause();
      }
    }
  }, [deck.isPlaying]);

  useEffect(() => {
    // Draw waveform if available
    if (deck.track?.waveform_data && canvasRef.current) {
      drawWaveform(deck.track.waveform_data);
    }
  }, [deck.track]);

  const drawWaveform = (waveformData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, width, height);

    // Draw waveform
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 2;
    ctx.beginPath();

    const step = width / waveformData.length;
    for (let i = 0; i < waveformData.length; i++) {
      const x = i * step;
      const y = height / 2 + (waveformData[i] * height / 2);
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
  };

  const handleTrackSelect = (track) => {
    loadTrack(deckId, track);
    setAnchorEl(null);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 2 }}>
      {/* Deck Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6">{label}</Typography>
        <IconButton
          onClick={(e) => setAnchorEl(e.currentTarget)}
          color="primary"
        >
          <LibraryMusicIcon />
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          {tracks.map((track) => (
            <MenuItem key={track.id} onClick={() => handleTrackSelect(track)}>
              {track.artist} - {track.title}
            </MenuItem>
          ))}
        </Menu>
      </Box>

      {/* Track Info */}
      {deck.track ? (
        <Paper sx={{ p: 1, bgcolor: '#1a1a1a' }}>
          <Typography variant="body2" noWrap>
            {deck.track.artist} - {deck.track.title}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            {deck.track.bpm ? `${deck.track.bpm.toFixed(1)} BPM` : 'No BPM'} • 
            {deck.track.key || 'No Key'}
          </Typography>
        </Paper>
      ) : (
        <Paper sx={{ p: 1, bgcolor: '#1a1a1a' }}>
          <Typography variant="body2" color="textSecondary">
            No track loaded
          </Typography>
        </Paper>
      )}

      {/* Waveform Display */}
      <Box sx={{ flexGrow: 1, bgcolor: '#1a1a1a', borderRadius: 1, overflow: 'hidden' }}>
        <canvas
          ref={canvasRef}
          width={800}
          height={200}
          style={{ width: '100%', height: '100%' }}
        />
      </Box>

      {/* Transport Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
        <IconButton
          onClick={() => togglePlay(deckId)}
          color="primary"
          size="large"
          disabled={!deck.track}
        >
          {deck.isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
        </IconButton>
      </Box>

      {/* Volume Control */}
      <Box sx={{ px: 2 }}>
        <Typography variant="caption">Volume</Typography>
        <Slider
          value={deck.volume * 100}
          onChange={(e, value) => setVolume(deckId, value / 100)}
          disabled={!deck.track}
          marks
          step={10}
          min={0}
          max={100}
        />
      </Box>

      {/* Pitch Control */}
      <Box sx={{ px: 2 }}>
        <Typography variant="caption">
          Pitch: {deck.pitch > 0 ? '+' : ''}{deck.pitch.toFixed(1)}%
        </Typography>
        <Slider
          value={deck.pitch}
          onChange={(e, value) => setPitch(deckId, value)}
          disabled={!deck.track}
          marks
          step={0.1}
          min={-8}
          max={8}
        />
      </Box>

      {/* Hidden audio element */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </Box>
  );
};

export default Deck;
