import React, { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  CircularProgress,
  Slider,
  FormControlLabel,
  Switch,
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { mixerAPI } from '../services/api';

const AutoMixer = ({ tracks, onMixGenerated }) => {
  const [open, setOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Settings
  const [startTrackId, setStartTrackId] = useState(null);
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [bpmTolerance, setBpmTolerance] = useState(6);
  const [energyVariation, setEnergyVariation] = useState(0.3);
  const [useRandomStart, setUseRandomStart] = useState(true);

  const handleOpen = () => {
    setOpen(true);
    setResult(null);
    setError(null);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    setResult(null);

    try {
      const mixResult = await mixerAPI.generateAutoMix({
        start_track_id: useRandomStart ? null : startTrackId,
        duration_minutes: durationMinutes,
        bpm_tolerance: bpmTolerance,
        energy_variation: energyVariation,
      });

      setResult(mixResult);

      if (onMixGenerated) {
        onMixGenerated(mixResult);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate auto-mix');
      console.error('Auto-mix generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <>
      <Button
        variant="contained"
        color="secondary"
        startIcon={<AutoAwesomeIcon />}
        onClick={handleOpen}
        disabled={!tracks || tracks.length === 0}
        fullWidth
        sx={{ mb: 2 }}
      >
        Auto-Mix
      </Button>

      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AutoAwesomeIcon />
            Generate Auto-Mix
          </Box>
        </DialogTitle>

        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {!result && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Mix Settings
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Typography variant="caption" gutterBottom>
                  Target Duration: {durationMinutes} minutes
                </Typography>
                <Slider
                  value={durationMinutes}
                  onChange={(e, newValue) => setDurationMinutes(newValue)}
                  min={15}
                  max={180}
                  step={15}
                  marks={[
                    { value: 15, label: '15m' },
                    { value: 60, label: '60m' },
                    { value: 120, label: '120m' },
                    { value: 180, label: '180m' },
                  ]}
                  disabled={generating}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="caption" gutterBottom>
                  BPM Tolerance: ±{bpmTolerance} BPM
                </Typography>
                <Slider
                  value={bpmTolerance}
                  onChange={(e, newValue) => setBpmTolerance(newValue)}
                  min={2}
                  max={20}
                  step={1}
                  marks={[
                    { value: 2, label: '2' },
                    { value: 6, label: '6' },
                    { value: 10, label: '10' },
                    { value: 20, label: '20' },
                  ]}
                  disabled={generating}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="caption" gutterBottom>
                  Energy Variation: ±{(energyVariation * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={energyVariation}
                  onChange={(e, newValue) => setEnergyVariation(newValue)}
                  min={0.1}
                  max={1.0}
                  step={0.1}
                  marks={[
                    { value: 0.1, label: '10%' },
                    { value: 0.5, label: '50%' },
                    { value: 1.0, label: '100%' },
                  ]}
                  disabled={generating}
                />
              </Box>

              <FormControlLabel
                control={
                  <Switch
                    checked={useRandomStart}
                    onChange={(e) => setUseRandomStart(e.target.checked)}
                    disabled={generating}
                  />
                }
                label="Random starting track"
              />
            </Box>
          )}

          {result && (
            <Box sx={{ mt: 2 }}>
              <Alert severity="success" sx={{ mb: 2 }}>
                Mix generated successfully!
              </Alert>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Mix Summary
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label={`${result.track_count} tracks`} color="primary" size="small" />
                  <Chip
                    label={`${formatDuration(result.total_duration)} total`}
                    size="small"
                  />
                  <Chip
                    label={`${result.transitions?.length || 0} transitions`}
                    size="small"
                  />
                </Box>
              </Box>

              <Typography variant="subtitle2" gutterBottom>
                Tracklist:
              </Typography>
              <List dense sx={{ maxHeight: 300, overflow: 'auto', bgcolor: '#2a2a2a', borderRadius: 1 }}>
                {result.tracklist.map((track, index) => (
                  <ListItem
                    key={track.track_id}
                    sx={{
                      borderBottom: index < result.tracklist.length - 1 ? '1px solid #3a3a3a' : 'none',
                    }}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          {index + 1}. {track.title} - {track.artist}
                        </Typography>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                          {track.bpm && (
                            <Chip label={`${Math.round(track.bpm)} BPM`} size="small" />
                          )}
                          {track.key && <Chip label={track.key} size="small" />}
                          {track.energy && (
                            <Chip
                              label={`Energy: ${(track.energy * 100).toFixed(0)}%`}
                              size="small"
                            />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>

              {result.transitions && result.transitions.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    Transitions calculated with crossfades ranging from 8-32 seconds based on BPM
                    compatibility
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={generating}>
            Close
          </Button>
          {!result && (
            <Button
              onClick={handleGenerate}
              variant="contained"
              color="primary"
              startIcon={generating ? <CircularProgress size={20} /> : <PlayArrowIcon />}
              disabled={generating || !tracks || tracks.length === 0}
            >
              {generating ? 'Generating...' : 'Generate Mix'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AutoMixer;
