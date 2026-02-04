# DJ Mixing Platform

A comprehensive web-based DJ mixing platform that runs inside a Docker container, allowing users to import, analyze, and mix songs with a professional DJ interface.

## Features

### Core Functionality
- **Dual Deck System**: Two virtual turntables for professional mixing
- **Audio Analysis**: Automatic BPM detection, key detection, energy level analysis, and waveform generation
- **Professional Mixer**: Crossfader, 3-band EQ per deck, volume controls
- **Track Library Management**: Upload and organize your music collection
- **Real-time Playback**: Low-latency audio playback with Web Audio API

### Audio Analysis Engine
- BPM (Beats Per Minute) detection using advanced beat tracking
- Musical key detection and Camelot wheel mapping for harmonic mixing
- Energy level analysis for track compatibility
- Waveform generation for visual display
- Track structure detection (intro, main, outro)

### DJ Interface
- Play/pause, cue points, tempo adjustment
- Per-deck volume and pitch controls
- Crossfader with smooth mixing
- 3-band EQ (High, Mid, Low) per deck
- Real-time waveform visualization

## Technology Stack

### Backend
- **Python FastAPI**: High-performance API framework
- **PostgreSQL**: Relational database for metadata storage
- **Redis**: Caching layer for performance
- **librosa**: Audio analysis and feature extraction
- **aubio**: Beat detection and pitch analysis

### Frontend
- **React**: Modern UI framework
- **Material-UI**: Professional component library
- **Zustand**: Lightweight state management
- **WaveSurfer.js**: Waveform visualization
- **Web Audio API**: Real-time audio processing

### Infrastructure
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Production-ready web server

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 4GB RAM minimum
- Supported audio formats: MP3, WAV, FLAC, AAC

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Xander-Vanlaer/dj-mixing.git
cd dj-mixing
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### First Run Setup

1. Open http://localhost:3000 in your browser
2. Navigate to "Library" tab
3. Upload your first tracks (MP3, WAV, FLAC, AAC)
4. Wait for automatic analysis (BPM, key, waveform)
5. Go to "Mixer" tab and start mixing!

## Usage Guide

### Uploading Tracks

1. Click "Library" in the navigation
2. Click "Upload Track" button
3. Select audio file(s)
4. Wait for automatic analysis (15-30 seconds per track)
5. Track appears in library with BPM, key, and waveform data

### Mixing Tracks

1. Go to "Mixer" tab
2. Click the library icon on Deck A or Deck B
3. Select a track from the dropdown menu
4. Use play/pause controls to start playback
5. Adjust volume, pitch, and EQ controls
6. Use crossfader to blend between decks

### Controls

#### Deck Controls
- **Play/Pause**: Start/stop playback
- **Volume**: Control deck output level
- **Pitch**: Adjust tempo (-8% to +8%)

#### Mixer Controls
- **Crossfader**: Blend between Deck A (left) and Deck B (right)
- **EQ**: High/Mid/Low frequency control per deck (-12dB to +12dB)
- **Master Volume**: Overall output level

## API Documentation

The backend API provides comprehensive endpoints for track management, analysis, and mixing.

### Track Management
- `POST /api/tracks/upload` - Upload and analyze new track
- `GET /api/tracks/` - List all tracks
- `GET /api/tracks/{id}` - Get specific track
- `DELETE /api/tracks/{id}` - Delete track
- `GET /api/tracks/{id}/audio` - Stream audio file

### Analysis
- `GET /api/analysis/{track_id}` - Get detailed analysis
- `POST /api/analysis/{track_id}/reanalyze` - Re-analyze track
- `GET /api/analysis/{track_id}/compatible` - Find compatible tracks

### Mixer
- `POST /api/mixer/mixes` - Create new mix
- `GET /api/mixer/mixes` - List saved mixes
- `POST /api/mixer/auto-mix` - Generate automatic mix

Full API documentation available at http://localhost:8000/docs

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Frontend (React)                │
│  - DJ Mixer Interface                           │
│  - Track Library Management                      │
│  - Real-time Audio Playback                     │
└─────────────────┬───────────────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────▼───────────────────────────────┐
│              Backend (FastAPI)                   │
│  - REST API                                      │
│  - File Upload Management                        │
│  - Audio Analysis Orchestration                  │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴──────────┬──────────────┐
        │                    │              │
┌───────▼────────┐  ┌───────▼─────┐  ┌────▼─────┐
│   PostgreSQL   │  │    Redis    │  │  Audio   │
│   (Metadata)   │  │   (Cache)   │  │  Files   │
└────────────────┘  └─────────────┘  └──────────┘
```

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Running in Development Mode (Alternative)

For local development without Docker:

1. **Start Backend Services** (PostgreSQL and Redis):
```bash
# Option 1: Use Docker for services only
docker-compose up -d db redis

# Option 2: Install and run locally
# Install PostgreSQL and Redis, then start them
```

2. **Start Backend**:
```bash
./start-dev.sh
# Or manually:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. **Start Frontend** (in separate terminal):
```bash
cd frontend
npm install
npm start
```

### Database Migrations

```bash
cd backend
alembic upgrade head
```

## Troubleshooting

### Network Errors (ERR_EMPTY_RESPONSE, ERR_CONNECTION_ABORTED)

If you see errors like:
```
Error loading tracks: AxiosError: Network Error
Failed to load resource: net::ERR_EMPTY_RESPONSE
```

**This means the frontend cannot connect to the backend API.**

#### Quick Fix

1. **Verify backend is running**:
```bash
# Check health status
./check-backend.sh

# Or manually:
curl http://localhost:8000/health
```

2. **Start the backend** if not running:
```bash
# With Docker:
docker-compose up -d backend

# Or in development mode:
./start-dev.sh
```

3. **Check backend logs**:
```bash
# Docker:
docker-compose logs backend

# Development mode: Check terminal where uvicorn is running
```

#### Detailed Troubleshooting

**1. Backend Not Running**
- Check if backend process is active:
  - Docker: `docker-compose ps` (backend should be "Up")
  - Local: `ps aux | grep uvicorn`
- Start backend using one of the methods above

**2. Wrong API URL**
- Frontend connects to backend via `REACT_APP_API_URL`
- Check `.env` file has correct value:
  - For Docker/Local: `REACT_APP_API_URL=http://localhost:8000`
  - For Production: Use your actual domain
- Restart frontend after changing `.env`

**3. Port Conflicts**
- Backend needs port 8000 free
- Check what's using port 8000: `lsof -i :8000` or `netstat -an | grep 8000`
- Stop conflicting process or change backend port

**4. Docker Networking Issues**
- Ensure services are running: `docker-compose ps`
- Restart services: `docker-compose restart`
- Check logs: `docker-compose logs -f backend`

**5. Firewall/Network Issues**
- Ensure ports 3000 (frontend) and 8000 (backend) are accessible
- Try accessing backend directly: http://localhost:8000/docs

**6. Database Connection Issues**
- Backend needs PostgreSQL and Redis to start
- Check database: `docker-compose ps db` or `pg_isready -h localhost`
- Check Redis: `docker-compose ps redis` or `redis-cli ping`
- Start missing services: `docker-compose up -d db redis`

### Other Common Issues

**"Module not found" errors**
```bash
# Reinstall dependencies
cd frontend && npm install
cd backend && pip install -r requirements.txt
```

**"Permission denied" errors**
```bash
# Make scripts executable
chmod +x start-dev.sh check-backend.sh setup.sh
```

**"Database migration failed"**
```bash
# Reset and rerun migrations
cd backend
alembic downgrade base
alembic upgrade head
```

**Docker issues**
```bash
# Rebuild containers
docker-compose down
docker-compose build
docker-compose up -d

# Clean restart (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

**Key Variables:**
- `REACT_APP_API_URL`: Frontend API endpoint (default: http://localhost:8000)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Database credentials
- `SECRET_KEY`: Application secret key (generate with: `openssl rand -hex 32`)
- `UPLOAD_DIR`: Directory for uploaded audio files
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`: Optional Spotify integration

**Important:** After changing environment variables, restart the services:
```bash
# Docker:
docker-compose restart

# Development mode:
# Restart both frontend and backend processes
```

## Useful Commands

```bash
# Health check
./check-backend.sh                 # Verify backend is running

# Development mode
./start-dev.sh                     # Start backend in dev mode

# Docker management
docker-compose ps                  # Check service status
docker-compose logs -f backend     # View backend logs
docker-compose logs -f frontend    # View frontend logs
docker-compose restart             # Restart all services
docker-compose down                # Stop all services
docker-compose down -v             # Stop and remove data (WARNING!)

# Database
docker-compose exec db psql -U djuser -d djmixing  # PostgreSQL shell
make backup-db                     # Backup database
make restore-db                    # Restore database
```

## Roadmap

### Phase 1: Foundation (MVP) ✅
- Docker infrastructure
- File upload and storage
- Basic audio analysis (BPM, waveform)
- Simple dual-deck player
- Manual mixing controls

### Phase 2: DJ Features (In Progress)
- Full mixer with EQ and effects
- Beat-matching and sync
- Cue points and loops
- Improved waveform visualization
- Keyboard shortcuts

### Phase 3: Intelligence
- Advanced audio analysis (key, energy, structure)
- AI transition suggestions
- Basic auto-mix mode
- Harmonic mixing compatibility

### Phase 4: Advanced Features
- Full auto-DJ with mood/genre selection
- Export/download functionality
- Spotify integration
- Effect automation
- Session management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- GitHub Issues: https://github.com/Xander-Vanlaer/dj-mixing/issues
- Documentation: http://localhost:8000/docs (when running)

## Acknowledgments

- librosa: Audio analysis library
- FastAPI: Modern web framework
- React: UI framework
- Material-UI: Component library