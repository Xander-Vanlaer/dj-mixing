import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import useMixerStore from '../contexts/mixerStore';
import { tracksAPI } from '../services/api';

const TrackLibrary = () => {
  const { tracks, setTracks, addTrack, removeTrack } = useMixerStore();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    loadTracks();
  }, []);

  const loadTracks = async () => {
    try {
      const fetchedTracks = await tracksAPI.list();
      setTracks(fetchedTracks);
    } catch (error) {
      console.error('Error loading tracks:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const newTrack = await tracksAPI.upload(file);
      addTrack(newTrack);
      setUploadProgress(100);
      setTimeout(() => {
        setUploading(false);
        setUploadProgress(0);
      }, 1000);
    } catch (error) {
      console.error('Error uploading track:', error);
      alert('Error uploading track. Please try again.');
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDelete = async (trackId) => {
    if (window.confirm('Are you sure you want to delete this track?')) {
      try {
        await tracksAPI.delete(trackId);
        removeTrack(trackId);
      } catch (error) {
        console.error('Error deleting track:', error);
        alert('Error deleting track. Please try again.');
      }
    }
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Track Library</Typography>
        <Button
          variant="contained"
          component="label"
          startIcon={<CloudUploadIcon />}
          disabled={uploading}
        >
          Upload Track
          <input
            type="file"
            hidden
            accept=".mp3,.wav,.flac,.aac,.m4a"
            onChange={handleFileUpload}
          />
        </Button>
      </Box>

      {uploading && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>
            Uploading and analyzing track...
          </Typography>
          <LinearProgress variant="indeterminate" />
        </Box>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Artist</TableCell>
              <TableCell>Album</TableCell>
              <TableCell>BPM</TableCell>
              <TableCell>Key</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tracks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="textSecondary">
                    No tracks in library. Upload a track to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              tracks.map((track) => (
                <TableRow key={track.id} hover>
                  <TableCell>{track.title}</TableCell>
                  <TableCell>{track.artist}</TableCell>
                  <TableCell>{track.album || '-'}</TableCell>
                  <TableCell>
                    {track.bpm ? track.bpm.toFixed(1) : '-'}
                  </TableCell>
                  <TableCell>{track.key || '-'}</TableCell>
                  <TableCell>{formatDuration(track.duration)}</TableCell>
                  <TableCell>
                    <IconButton
                      onClick={() => handleDelete(track.id)}
                      color="error"
                      size="small"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ mt: 3 }}>
        <Typography variant="body2" color="textSecondary">
          Total tracks: {tracks.length}
        </Typography>
      </Box>
    </Box>
  );
};

export default TrackLibrary;
