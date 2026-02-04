# DJ Mixing Platform - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              React Frontend (Port 3000)                    │  │
│  │                                                             │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │   DJ Mixer  │  │    Track     │  │   Waveform      │  │  │
│  │  │  Interface  │  │   Library    │  │  Visualization  │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │      Zustand State Management                         │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            │ HTTP/REST API                       │
│                            ▼                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                           │
│                      (Port 80/443)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┴─────────────────────┐
        │                                          │
        ▼                                          ▼
┌──────────────────┐                    ┌──────────────────────┐
│  Static Files    │                    │   API Proxy          │
│  (Frontend)      │                    │   /api/* → :8000     │
└──────────────────┘                    └──────────┬───────────┘
                                                   │
                                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                FastAPI Backend (Port 8000)                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     API Endpoints                         │  │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌────────┐  │  │
│  │  │  Tracks  │  │ Analysis  │  │  Mixer   │  │ Health │  │  │
│  │  │   API    │  │    API    │  │   API    │  │  Check │  │  │
│  │  └──────────┘  └───────────┘  └──────────┘  └────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Business Logic                          │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │     Audio Analysis Service                        │    │  │
│  │  │  • BPM Detection (librosa)                        │    │  │
│  │  │  • Key Detection                                  │    │  │
│  │  │  • Waveform Generation                            │    │  │
│  │  │  • Energy Analysis                                │    │  │
│  │  │  • Track Structure Detection                      │    │  │
│  │  │  • Harmonic Compatibility                         │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              SQLAlchemy ORM Layer                         │  │
│  │  ┌─────────┐  ┌──────────────┐  ┌──────────┐  ┌──────┐  │  │
│  │  │  Track  │  │ TrackAnalysis│  │ CuePoint │  │  Mix │  │  │
│  │  │  Model  │  │    Model     │  │  Model   │  │ Model│  │  │
│  │  └─────────┘  └──────────────┘  └──────────┘  └──────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────┐                    ┌──────────────────┐
│   PostgreSQL     │                    │      Redis       │
│   (Port 5432)    │                    │   (Port 6379)    │
│                  │                    │                  │
│  • Track Data    │                    │  • Cache         │
│  • Analysis Data │                    │  • Session Data  │
│  • Mix Sessions  │                    │                  │
│  • Cue Points    │                    │                  │
└──────────────────┘                    └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      File System Storage                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    /app/uploads/                          │  │
│  │  • Audio Files (MP3, WAV, FLAC, AAC, M4A)                │  │
│  │  • Organized by upload date                              │  │
│  │  • Served via FileResponse API                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### 1. Track Upload Flow
```
User → Frontend Upload
  ↓
Frontend → POST /api/tracks/upload (FormData)
  ↓
Backend Receives File
  ↓
Save to /app/uploads/
  ↓
Extract Metadata (mutagen)
  ↓
Audio Analysis (librosa)
  • BPM Detection
  • Key Detection  
  • Waveform Generation
  • Energy Analysis
  ↓
Create Database Records
  • Track
  • TrackAnalysis
  ↓
Return Track Object → Frontend
  ↓
Update UI with New Track
```

### 2. Mixing Flow
```
User Loads Track to Deck
  ↓
Frontend Requests Audio
  ↓
GET /api/tracks/{id}/audio
  ↓
Backend Streams Audio File
  ↓
Frontend Audio Player (Web Audio API)
  • Decode Audio
  • Create AudioContext
  • Apply Volume/Pitch/EQ
  ↓
Real-time Playback
```

### 3. Analysis Flow
```
Track Upload Triggers Analysis
  ↓
AudioAnalysisService.analyze_track()
  ↓
Load Audio with librosa
  ↓
Parallel Analysis:
  ├─ BPM Detection (beat_track)
  ├─ Key Detection (chroma_cqt)
  ├─ Energy (RMS)
  ├─ Spectral Features
  └─ Waveform Downsampling
  ↓
Store Results in Database
  ├─ Track.bpm, .key, .energy
  └─ TrackAnalysis (detailed)
  ↓
Return to Frontend for Display
```

## Data Flow

### Track Entity
```
Track
├─ Metadata (title, artist, album, genre)
├─ File Info (path, format, size, duration)
├─ Basic Analysis (bpm, key, energy)
├─ Waveform Data (JSON array)
└─ Relationships
    ├─ TrackAnalysis (1:1)
    └─ CuePoints (1:many)
```

### Analysis Pipeline
```
Audio File → librosa.load()
  ↓
Tempo Detection → librosa.beat.beat_track()
  ↓
Key Detection → librosa.feature.chroma_cqt()
  ↓
Energy → librosa.feature.rms()
  ↓
Structure → Heuristic-based segmentation
  ↓
TrackAnalysis Record
```

## Technology Stack Layers

```
┌─────────────────────────────────────────────┐
│            Presentation Layer                │
│  React, Material-UI, Zustand, Canvas API    │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│            Application Layer                 │
│  FastAPI, Pydantic, Python Async/Await      │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│            Business Logic Layer              │
│  Audio Analysis, Mixing Algorithms,         │
│  Compatibility Matching                      │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│              Data Layer                      │
│  SQLAlchemy ORM, Alembic Migrations         │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│            Persistence Layer                 │
│  PostgreSQL, Redis, File System             │
└─────────────────────────────────────────────┘
```

## Deployment Architecture

```
Docker Host
├─ frontend container (Node/Nginx)
├─ backend container (Python/FastAPI)
├─ db container (PostgreSQL)
├─ redis container (Redis)
└─ Shared Networks & Volumes
    ├─ Network: dj-mixing-network
    ├─ Volume: postgres_data
    └─ Volume: uploads
```

## Security Layers

```
┌─────────────────────────────────────────────┐
│          Input Validation Layer              │
│  Pydantic Schemas, File Type Validation     │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│            Authentication Layer              │
│  (Future: JWT, OAuth)                        │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│            Database Layer                    │
│  SQL Injection Prevention (ORM)              │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│            Network Layer                     │
│  CORS, Rate Limiting (Future)                │
└─────────────────────────────────────────────┘
```

## Performance Optimization

### Caching Strategy
- Redis caches expensive analysis results
- Browser caches static assets
- Database query optimization with indexes

### Async Processing
- FastAPI async endpoints
- Background tasks for analysis
- Streaming responses for large files

### Frontend Optimization
- Code splitting
- Lazy loading of components
- Memoization of expensive calculations
- Canvas-based waveform (60 FPS)

## Scalability Considerations

### Horizontal Scaling
- Backend: Multiple FastAPI instances behind load balancer
- Database: PostgreSQL read replicas
- Redis: Redis cluster for distributed caching

### Vertical Scaling
- Increase container resources
- Optimize audio analysis algorithms
- Database connection pooling

## Monitoring & Logging

```
Application Logs
  ↓
Docker Logs
  ↓
Centralized Logging (Future)
  • ELK Stack
  • CloudWatch
  • Datadog
```

## Future Architecture Enhancements

1. **Microservices**
   - Separate audio analysis service
   - Dedicated export/recording service

2. **Message Queue**
   - RabbitMQ/Celery for background jobs
   - Asynchronous audio analysis

3. **CDN Integration**
   - CloudFront/CloudFlare for assets
   - S3 for audio file storage

4. **Real-time Features**
   - WebSocket for live collaboration
   - Server-Sent Events for updates

5. **AI/ML Pipeline**
   - TensorFlow/PyTorch models
   - Genre classification
   - Advanced transition generation
