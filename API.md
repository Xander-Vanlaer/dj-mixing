# DJ Mixing Platform API Reference

## Base URL

```
http://localhost:8000
```

All API endpoints are prefixed with `/api`.

## Authentication

Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

## Endpoints

### Health Check

#### GET /health

Check if the API is running.

**Response**
```json
{
  "status": "healthy",
  "service": "dj-mixing-backend",
  "version": "1.0.0"
}
```

---

## Track Management

### Upload Track

#### POST /api/tracks/upload

Upload a new audio track for analysis.

**Request**
- Content-Type: `multipart/form-data`
- Body: `file` (audio file: .mp3, .wav, .flac, .aac, .m4a)

**Response**
```json
{
  "id": 1,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "genre": "Electronic",
  "duration": 245.5,
  "file_path": "/app/uploads/song.mp3",
  "file_format": ".mp3",
  "file_size": 5242880,
  "bpm": 128.5,
  "key": "A",
  "energy": 0.75,
  "danceability": 0.82,
  "waveform_data": [0.1, 0.2, 0.3, ...],
  "created_at": "2026-02-04T20:00:00Z"
}
```

**Errors**
- 400: Invalid file format
- 500: Analysis failed

### List Tracks

#### GET /api/tracks/

List all tracks in the library.

**Query Parameters**
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum records to return

**Response**
```json
[
  {
    "id": 1,
    "title": "Song Title",
    "artist": "Artist Name",
    "bpm": 128.5,
    "key": "A",
    ...
  }
]
```

### Get Track

#### GET /api/tracks/{track_id}

Get details of a specific track.

**Response**
```json
{
  "id": 1,
  "title": "Song Title",
  "artist": "Artist Name",
  ...
}
```

**Errors**
- 404: Track not found

### Get Track Audio

#### GET /api/tracks/{track_id}/audio

Stream the audio file for a track.

**Response**
- Content-Type: `audio/mpeg`
- Body: Audio file stream

**Errors**
- 404: Track or audio file not found

### Delete Track

#### DELETE /api/tracks/{track_id}

Delete a track and its associated audio file.

**Response**
```json
{
  "message": "Track deleted successfully"
}
```

**Errors**
- 404: Track not found

### Add Cue Point

#### POST /api/tracks/{track_id}/cue-points

Add a cue point to a track.

**Request Body**
```json
{
  "position": 45.5,
  "label": "Drop",
  "color": "#ff0000"
}
```

**Response**
```json
{
  "id": 1,
  "track_id": 1,
  "position": 45.5,
  "label": "Drop",
  "color": "#ff0000",
  "created_at": "2026-02-04T20:00:00Z"
}
```

### Get Cue Points

#### GET /api/tracks/{track_id}/cue-points

Get all cue points for a track.

**Response**
```json
[
  {
    "id": 1,
    "track_id": 1,
    "position": 45.5,
    "label": "Drop",
    "color": "#ff0000"
  }
]
```

---

## Audio Analysis

### Get Track Analysis

#### GET /api/analysis/{track_id}

Get detailed audio analysis for a track.

**Response**
```json
{
  "id": 1,
  "track_id": 1,
  "bpm": 128.5,
  "key": "A",
  "camelot_key": "11B",
  "energy_level": 0.75,
  "structure": {
    "intro": {"start": 0, "end": 30},
    "main": {"start": 30, "end": 215},
    "outro": {"start": 215, "end": 245}
  },
  "beat_positions": [0.5, 1.0, 1.5, ...],
  "spectral_centroid": 2500.5,
  "spectral_rolloff": 5000.2,
  "analyzed_at": "2026-02-04T20:00:00Z"
}
```

### Re-analyze Track

#### POST /api/analysis/{track_id}/reanalyze

Re-run audio analysis on a track.

**Response**
```json
{
  "id": 1,
  "track_id": 1,
  "bpm": 128.5,
  ...
}
```

### Get Compatible Tracks

#### GET /api/analysis/{track_id}/compatible

Find tracks that are compatible for mixing.

**Query Parameters**
- `bpm_tolerance` (float, default: 10.0): Maximum BPM difference
- `limit` (integer, default: 10): Maximum results to return

**Response**
```json
[
  {
    "track": {
      "id": 2,
      "title": "Compatible Song",
      "artist": "Another Artist",
      "bpm": 130.0
    },
    "compatibility_score": 95.5,
    "bpm_diff": 1.5,
    "key_compatible": true
  }
]
```

---

## Mixer & Mixes

### Create Mix

#### POST /api/mixer/mixes

Create a new mix session.

**Request Body**
```json
{
  "name": "Friday Night Mix",
  "description": "High energy mix",
  "tracklist": [
    {
      "track_id": 1,
      "start_time": 0
    },
    {
      "track_id": 2,
      "start_time": 180
    }
  ],
  "transitions": [
    {
      "from_track": 1,
      "to_track": 2,
      "type": "crossfade",
      "duration": 16
    }
  ]
}
```

**Response**
```json
{
  "id": 1,
  "name": "Friday Night Mix",
  "description": "High energy mix",
  "duration": 360.0,
  "tracklist": [...],
  "transitions": [...],
  "created_at": "2026-02-04T20:00:00Z"
}
```

### List Mixes

#### GET /api/mixer/mixes

List all saved mixes.

**Query Parameters**
- `skip` (integer, default: 0)
- `limit` (integer, default: 100)

**Response**
```json
[
  {
    "id": 1,
    "name": "Friday Night Mix",
    "duration": 360.0,
    ...
  }
]
```

### Get Mix

#### GET /api/mixer/mixes/{mix_id}

Get details of a specific mix.

**Response**
```json
{
  "id": 1,
  "name": "Friday Night Mix",
  ...
}
```

### Delete Mix

#### DELETE /api/mixer/mixes/{mix_id}

Delete a saved mix.

**Response**
```json
{
  "message": "Mix deleted successfully"
}
```

### Generate Auto-Mix

#### POST /api/mixer/auto-mix

Generate an automatic mix based on seed tracks and preferences.

**Request Body**
```json
{
  "seed_tracks": [1, 2, 3],
  "duration_minutes": 60,
  "mood": "energetic"
}
```

**Response**
```json
{
  "suggested_tracklist": [
    {
      "track_id": 1,
      "start_time": 0,
      "title": "Track 1",
      "artist": "Artist 1"
    },
    {
      "track_id": 2,
      "start_time": 180,
      "title": "Track 2",
      "artist": "Artist 2"
    }
  ],
  "total_duration": 360,
  "mood": "energetic"
}
```

---

## Data Models

### Track
```typescript
{
  id: number
  title: string
  artist: string
  album?: string
  genre?: string
  duration: number  // seconds
  file_path: string
  file_format: string
  file_size: number  // bytes
  bpm?: number
  key?: string
  energy?: number  // 0-1
  danceability?: number  // 0-1
  waveform_data?: number[]
  created_at: datetime
  updated_at?: datetime
}
```

### TrackAnalysis
```typescript
{
  id: number
  track_id: number
  bpm?: number
  key?: string
  camelot_key?: string
  energy_level?: number
  structure?: {
    intro: {start: number, end: number}
    main: {start: number, end: number}
    outro: {start: number, end: number}
  }
  beat_positions?: number[]
  spectral_centroid?: number
  spectral_rolloff?: number
  analyzed_at: datetime
}
```

### CuePoint
```typescript
{
  id: number
  track_id: number
  position: number  // seconds
  label?: string
  color?: string  // hex color
  created_at: datetime
}
```

### Mix
```typescript
{
  id: number
  name: string
  description?: string
  duration: number
  tracklist: Array<{
    track_id: number
    start_time: number
  }>
  transitions?: Array<{
    from_track: number
    to_track: number
    type: string
    duration: number
  }>
  export_path?: string
  export_format?: string
  created_at: datetime
  updated_at?: datetime
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Interactive Documentation

For interactive API testing, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
