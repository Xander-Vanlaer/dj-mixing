# DJ Mixing Platform - Docker Deployment Guide

## Prerequisites

Before deploying the DJ Mixing Platform, ensure you have:

- **Docker Engine** 20.10 or higher
- **Docker Compose** 2.0 or higher  
- **Minimum System Requirements**:
  - 4GB RAM
  - 10GB free disk space
  - 2 CPU cores

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Xander-Vanlaer/dj-mixing.git
cd dj-mixing
```

### 2. Configure Environment Variables

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` and update the following variables:

```bash
# Database Configuration
POSTGRES_DB=djmixing
POSTGRES_USER=djuser
POSTGRES_PASSWORD=<strong-password-here>

# Backend Configuration
SECRET_KEY=<generate-random-secret-key>

# Optional: Spotify Integration
SPOTIFY_CLIENT_ID=<your-spotify-client-id>
SPOTIFY_CLIENT_SECRET=<your-spotify-client-secret>
```

**Security Note**: Always use strong, unique passwords in production!

### 3. Deploy with Docker Compose

#### Automatic Deployment (Recommended)

```bash
chmod +x deploy.sh
./deploy.sh
```

#### Manual Deployment

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 4. Verify Deployment

1. Check all services are running:
```bash
docker-compose ps
```

Expected output:
```
NAME                  STATUS              PORTS
dj-mixing-backend     Up (healthy)        0.0.0.0:8000->8000/tcp
dj-mixing-frontend    Up                  0.0.0.0:3000->80/tcp
dj-mixing-db          Up (healthy)        0.0.0.0:5432->5432/tcp
dj-mixing-redis       Up (healthy)        0.0.0.0:6379->6379/tcp
```

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Service Architecture

The application consists of four Docker containers:

### Frontend (Port 3000)
- React application with Nginx
- DJ mixer interface
- Track library management

### Backend (Port 8000)
- FastAPI application
- Audio analysis engine
- REST API endpoints

### Database (Port 5432)
- PostgreSQL 15
- Stores track metadata and analysis

### Cache (Port 6379)
- Redis 7
- Caches analysis results

## Data Persistence

Docker volumes are used for persistent data:

- `postgres_data`: Database files
- `uploads`: Audio file storage

### Backup Data

```bash
# Backup database
docker-compose exec db pg_dump -U djuser djmixing > backup.sql

# Backup uploads
docker run --rm -v dj-mixing_uploads:/data -v $(pwd):/backup \
  alpine tar czf /backup/uploads-backup.tar.gz /data
```

### Restore Data

```bash
# Restore database
docker-compose exec -T db psql -U djuser djmixing < backup.sql

# Restore uploads
docker run --rm -v dj-mixing_uploads:/data -v $(pwd):/backup \
  alpine tar xzf /backup/uploads-backup.tar.gz -C /
```

## Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services

```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop and Remove

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Services Not Starting

1. Check Docker daemon is running:
```bash
docker ps
```

2. Check service logs:
```bash
docker-compose logs backend
```

3. Verify ports are not in use:
```bash
lsof -i :3000
lsof -i :8000
lsof -i :5432
```

### Database Connection Issues

1. Check database is healthy:
```bash
docker-compose ps db
```

2. Test database connection:
```bash
docker-compose exec db psql -U djuser -d djmixing
```

### Frontend Cannot Connect to Backend

1. Check backend health endpoint:
```bash
curl http://localhost:8000/health
```

2. Verify REACT_APP_API_URL in frontend environment

### Audio Analysis Failing

1. Check FFmpeg is installed in backend container:
```bash
docker-compose exec backend ffmpeg -version
```

2. Verify upload directory permissions:
```bash
docker-compose exec backend ls -la /app/uploads
```

## Production Deployment

For production deployments, consider:

1. **Use a reverse proxy** (nginx, Traefik) with SSL/TLS
2. **Configure firewall** to restrict access to internal ports
3. **Set strong passwords** for database and secret keys
4. **Enable backup automation** for database and uploads
5. **Configure logging** and monitoring
6. **Use Docker secrets** for sensitive data
7. **Set resource limits** in docker-compose.yml

### Example Production docker-compose Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - DEBUG=false
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  frontend:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  db:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

Deploy with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Performance Tuning

### Database Optimization

Edit `docker-compose.yml` to add PostgreSQL configuration:

```yaml
db:
  environment:
    - POSTGRES_SHARED_BUFFERS=256MB
    - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
```

### Backend Workers

For high-traffic deployments, scale backend workers:

```yaml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Security Considerations

1. **Change default passwords** in `.env`
2. **Use strong SECRET_KEY** (minimum 32 characters)
3. **Restrict network access** to internal services
4. **Keep Docker images updated**
5. **Monitor logs** for suspicious activity
6. **Implement rate limiting** for API endpoints
7. **Use HTTPS** in production

## Support

For issues and questions:
- GitHub Issues: https://github.com/Xander-Vanlaer/dj-mixing/issues
- Documentation: Check `/docs` when application is running
