# Testing Guide

## Overview

This guide covers testing strategies for the DJ Mixing Platform.

## Backend Testing

### Setup

Install test dependencies:
```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tracks.py

# Run with verbose output
pytest -v
```

### Test Structure

```
backend/
  tests/
    __init__.py
    conftest.py          # Shared fixtures
    test_tracks.py       # Track API tests
    test_analysis.py     # Analysis tests
    test_mixer.py        # Mixer tests
    test_audio.py        # Audio analysis tests
```

### Example Test

```python
# tests/test_tracks.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_tracks():
    response = client.get("/api/tracks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Frontend Testing

### Setup

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Test Structure

```
frontend/
  src/
    components/
      __tests__/
        Deck.test.js
        Mixer.test.js
        TrackLibrary.test.js
```

### Example Test

```javascript
// src/components/__tests__/Deck.test.js
import { render, screen } from '@testing-library/react';
import Deck from '../Deck';

test('renders deck label', () => {
  render(<Deck deckId="deckA" label="Deck A" />);
  const labelElement = screen.getByText(/Deck A/i);
  expect(labelElement).toBeInTheDocument();
});
```

## Integration Testing

### Docker Testing

Test the full stack in Docker:

```bash
# Build and start
docker-compose up -d

# Wait for services
sleep 30

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:3000

# Stop
docker-compose down
```

### API Integration Tests

```python
import requests

def test_upload_and_analyze():
    # Upload track
    with open("test_track.mp3", "rb") as f:
        response = requests.post(
            "http://localhost:8000/api/tracks/upload",
            files={"file": f}
        )
    
    assert response.status_code == 200
    track = response.json()
    
    # Check analysis was performed
    assert track["bpm"] is not None
    assert track["waveform_data"] is not None
```

## Manual Testing Checklist

### Track Upload
- [ ] Upload MP3 file
- [ ] Upload WAV file
- [ ] Upload FLAC file
- [ ] Verify BPM detection works
- [ ] Verify key detection works
- [ ] Verify waveform is generated
- [ ] Check file size limits

### DJ Mixer
- [ ] Load track to Deck A
- [ ] Load track to Deck B
- [ ] Play/pause on both decks
- [ ] Adjust volume controls
- [ ] Adjust pitch controls
- [ ] Use crossfader
- [ ] Adjust EQ controls
- [ ] Check waveform displays correctly

### Track Library
- [ ] View all tracks
- [ ] Delete track
- [ ] View track details
- [ ] Sort/filter tracks (future feature)

## Performance Testing

### Load Testing

Use tools like Apache Bench or Locust:

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test track listing endpoint
ab -n 1000 -c 10 http://localhost:8000/api/tracks/

# Expected: <50ms response time
```

### Analysis Performance

```python
import time
from app.services.audio_analysis import AudioAnalysisService

def test_analysis_performance():
    start = time.time()
    result = AudioAnalysisService.analyze_track("test.mp3")
    duration = time.time() - start
    
    # Should complete in <30 seconds
    assert duration < 30
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test
```

## Security Testing

### Dependency Scanning

```bash
# Backend
pip install safety
safety check

# Frontend
npm audit
```

### OWASP Testing

- [ ] SQL injection prevention (using SQLAlchemy ORM)
- [ ] File upload validation
- [ ] Rate limiting on API endpoints
- [ ] CORS configuration
- [ ] Secrets management

## Accessibility Testing

### Frontend
- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast
- [ ] Focus indicators
- [ ] ARIA labels

Use tools like:
- Lighthouse
- axe DevTools
- WAVE

## Common Issues & Solutions

### Backend Issues

**Issue**: Import errors
```bash
# Solution: Ensure PYTHONPATH is set
export PYTHONPATH=/app:$PYTHONPATH
```

**Issue**: Database connection fails
```bash
# Solution: Check database is running
docker-compose ps db
docker-compose logs db
```

### Frontend Issues

**Issue**: API calls fail
```bash
# Solution: Check REACT_APP_API_URL
echo $REACT_APP_API_URL
# Should be http://localhost:8000
```

**Issue**: Audio playback fails
```bash
# Solution: Check CORS settings in backend
# Verify Audio element has correct src
```

## Test Data

### Sample Tracks

For testing, use royalty-free music from:
- FreeMusicArchive.org
- Incompetech.com
- Bensound.com

### Mock Data

```python
# tests/fixtures.py
MOCK_TRACK = {
    "title": "Test Track",
    "artist": "Test Artist",
    "bpm": 128.0,
    "key": "A",
    "duration": 180.0
}

MOCK_ANALYSIS = {
    "bpm": 128.0,
    "key": "A",
    "camelot_key": "11B",
    "energy_level": 0.75
}
```

## Reporting Issues

When reporting bugs, include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Environment details (OS, Docker version)
5. Logs (backend and frontend)
6. Screenshots/videos if UI-related
