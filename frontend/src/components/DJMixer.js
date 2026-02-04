import React, { useEffect, useState } from 'react';
import { Box, Grid, Paper, Alert, AlertTitle } from '@mui/material';
import Deck from './Deck';
import Mixer from './Mixer';
import useMixerStore from '../contexts/mixerStore';
import { tracksAPI } from '../services/api';

const DJMixer = () => {
  const { setTracks } = useMixerStore();
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load tracks on component mount
    const loadTracks = async () => {
      try {
        const tracks = await tracksAPI.list();
        setTracks(tracks);
        setError(null); // Clear any previous errors
      } catch (error) {
        console.error('Error loading tracks:', error);
        setError(error.userMessage || 'Failed to load tracks. Please ensure the backend server is running.');
      }
    };
    loadTracks();
  }, [setTracks]);

  return (
    <Box sx={{ height: 'calc(100vh - 100px)' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          <AlertTitle>Backend Connection Error</AlertTitle>
          {error}
        </Alert>
      )}
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* Deck A */}
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 2, height: '100%', bgcolor: '#2a2a2a' }}>
            <Deck deckId="deckA" label="Deck A" />
          </Paper>
        </Grid>

        {/* Mixer Section */}
        <Grid item xs={12} md={2}>
          <Paper sx={{ p: 2, height: '100%', bgcolor: '#1f1f1f' }}>
            <Mixer />
          </Paper>
        </Grid>

        {/* Deck B */}
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 2, height: '100%', bgcolor: '#2a2a2a' }}>
            <Deck deckId="deckB" label="Deck B" />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DJMixer;
