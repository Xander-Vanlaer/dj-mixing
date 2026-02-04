# Quick Reference Guide

## Installation

```bash
# One-line setup
./setup.sh

# Manual setup
cp .env.example .env
docker-compose build
docker-compose up -d
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Commands

### Using Make
```bash
make help          # Show all commands
make build         # Build images
make up            # Start services
make down          # Stop services
make logs          # View logs
make status        # Check status
make clean         # Remove everything (WARNING)
```

### Using Docker Compose
```bash
docker-compose up -d           # Start in background
docker-compose down            # Stop all services
docker-compose logs -f         # Follow logs
docker-compose ps              # Check status
docker-compose restart         # Restart services
```

### Using Deploy Script
```bash
./deploy.sh        # Automated deployment
```

## Quick Start Workflow

1. **Start the platform**
   ```bash
   ./setup.sh
   ```

2. **Open frontend**
   - Navigate to http://localhost:3000

3. **Upload tracks**
   - Click "Library" tab
   - Click "Upload Track" button
   - Select MP3/WAV/FLAC file
   - Wait for automatic analysis

4. **Start mixing**
   - Click "Mixer" tab
   - Load track to Deck A (library icon)
   - Load track to Deck B (library icon)
   - Press play and adjust controls

## API Quick Reference

### Upload Track
```bash
curl -X POST "http://localhost:8000/api/tracks/upload" \
  -F "file=@song.mp3"
```

### List Tracks
```bash
curl "http://localhost:8000/api/tracks/"
```

### Get Track Analysis
```bash
curl "http://localhost:8000/api/analysis/1"
```

### Find Compatible Tracks
```bash
curl "http://localhost:8000/api/analysis/1/compatible"
```

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs backend
docker-compose logs frontend

# Restart
docker-compose restart
```

### Port already in use
```bash
# Change ports in docker-compose.yml
# Frontend: 3000 → 3001
# Backend: 8000 → 8001
```

### Database connection failed
```bash
# Check database is running
docker-compose ps db

# Restart database
docker-compose restart db
```

### Upload fails
```bash
# Check backend logs
docker-compose logs backend

# Verify upload directory exists
docker-compose exec backend ls -la /app/uploads

# Check file size (max 100MB by default)
```

## File Locations

### Configuration
- `.env` - Environment variables
- `docker-compose.yml` - Service configuration
- `backend/alembic.ini` - Database migrations

### Code
- `backend/app/` - Backend source
- `frontend/src/` - Frontend source

### Data
- Docker volume `postgres_data` - Database
- Docker volume `uploads` - Audio files

### Logs
```bash
docker-compose logs backend   # Backend logs
docker-compose logs frontend  # Frontend logs
docker-compose logs db        # Database logs
```

## Development Workflow

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database Migrations
```bash
cd backend
alembic revision -m "migration message"
alembic upgrade head
```

## Keyboard Shortcuts (Future)

| Key | Action |
|-----|--------|
| `A` | Play/Pause Deck A |
| `K` | Play/Pause Deck B |
| `Q/W` | Pitch Down/Up Deck A |
| `U/I` | Pitch Down/Up Deck B |
| `←/→` | Crossfader Left/Right |
| `+/-` | Master Volume |
| `T` | Library Tab |
| `M` | Mixer Tab |

## Performance Tips

1. **Use SSD for uploads volume**
2. **Allocate at least 4GB RAM to Docker**
3. **Close unused browser tabs**
4. **Use Chrome/Firefox for best Web Audio API support**

## Security Checklist

- [ ] Change default passwords in `.env`
- [ ] Generate strong SECRET_KEY
- [ ] Don't commit `.env` file
- [ ] Use HTTPS in production
- [ ] Set up firewall rules
- [ ] Regular backups

## Backup & Restore

### Backup
```bash
# Database
docker-compose exec db pg_dump -U djuser djmixing > backup.sql

# Uploads
docker run --rm -v dj-mixing_uploads:/data -v $(pwd):/backup \
  alpine tar czf /backup/uploads.tar.gz /data
```

### Restore
```bash
# Database
docker-compose exec -T db psql -U djuser djmixing < backup.sql

# Uploads
docker run --rm -v dj-mixing_uploads:/data -v $(pwd):/backup \
  alpine tar xzf /backup/uploads.tar.gz -C /
```

## Resources

- **Documentation**: `/docs` in repository
- **API Reference**: http://localhost:8000/docs
- **GitHub**: https://github.com/Xander-Vanlaer/dj-mixing
- **Issues**: GitHub Issues tab

## Support

1. Check documentation in `/docs`
2. Search existing GitHub Issues
3. Create new issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs

## Next Steps

After basic setup:
1. Upload diverse tracks for testing
2. Experiment with mixing controls
3. Check compatible track suggestions
4. Review API documentation
5. Contribute improvements (see CONTRIBUTING.md)

---

**Version**: 1.0.0-MVP  
**Last Updated**: February 4, 2026
