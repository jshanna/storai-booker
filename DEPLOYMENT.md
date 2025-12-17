# StorAI-Booker Production Deployment Guide

This guide covers deploying StorAI-Booker to production using Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Deployment Steps](#deployment-steps)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 22.04 LTS recommended) or macOS
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB+ SSD recommended (for images and database)
- **Docker**: 24.0+ with Compose V2
- **Network**: Ports 80, 8000, 9000, 9001, 27017, 6379 available

### Required Software

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker compose version
```

### API Keys

You need at least one LLM provider API key:

- **Google AI (Recommended)**: https://ai.google.dev/
- **OpenAI** (Optional): https://platform.openai.com/
- **Anthropic** (Optional): https://console.anthropic.com/

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/storai-booker.git
cd storai-booker

# 2. Create production environment file
cp .env.production.example .env.production

# 3. Edit .env.production with your API keys and credentials
nano .env.production

# 4. Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# 5. Check service health
docker compose -f docker-compose.prod.yml ps

# 6. View logs
docker compose -f docker-compose.prod.yml logs -f

# 7. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000/api/docs
# MinIO Console: http://localhost:9001
```

## Configuration

### Environment Variables

Edit `.env.production` with your actual values:

```bash
# Required: Google AI API Key
GOOGLE_API_KEY=your_actual_google_api_key_here

# Required: Change default MinIO credentials
MINIO_ROOT_USER=your_minio_admin_user
MINIO_ROOT_PASSWORD=your_strong_random_password_here

# Optional: Other LLM providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Default provider
DEFAULT_LLM_PROVIDER=google
DEFAULT_TEXT_MODEL=gemini-2.5-flash
DEFAULT_IMAGE_MODEL=gemini-2.5-flash-image
```

### Resource Limits

The production compose file includes sensible resource limits:

| Service | CPU Limit | Memory Limit | Purpose |
|---------|-----------|--------------|---------|
| MongoDB | 2.0 cores | 2GB | Database |
| Redis | 1.0 core | 512MB | Cache/Queue |
| MinIO | 1.0 core | 1GB | Object Storage |
| Backend | 2.0 cores | 2GB | API Server |
| Celery | 3.0 cores | 3GB | Background Jobs |
| Frontend | 0.5 cores | 256MB | Web Server |

Adjust in `docker-compose.prod.yml` based on your server capacity.

## Deployment Steps

### 1. Initial Deployment

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start infrastructure services first
docker compose -f docker-compose.prod.yml up -d mongodb redis minio createbuckets

# Wait for health checks (30 seconds)
sleep 30

# Start application services
docker compose -f docker-compose.prod.yml up -d backend celery-worker frontend

# Verify all services are running
docker compose -f docker-compose.prod.yml ps
```

### 2. Verify Deployment

```bash
# Check service health
docker compose -f docker-compose.prod.yml ps

# Expected output: All services should show "healthy" status

# Test backend API
curl http://localhost:8000/health

# Test frontend
curl http://localhost/health

# View logs
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs celery-worker
docker compose -f docker-compose.prod.yml logs frontend
```

### 3. Create First Story (Smoke Test)

```bash
# Access the frontend at http://localhost
# OR test API directly:

curl -X POST http://localhost:8000/api/stories/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Story",
    "generation_inputs": {
      "audience_age": 7,
      "topic": "A friendly dragon learning to fly",
      "setting": "Magical mountain kingdom",
      "format": "storybook",
      "illustration_style": "watercolor",
      "characters": ["Sparkle the dragon"],
      "page_count": 5
    }
  }'
```

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f celery-worker

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Volume usage
docker volume ls
du -sh /var/lib/docker/volumes/storai-booker_*
```

### Database Backup

```bash
# Backup MongoDB
docker exec storai-mongodb-prod mongodump \
  --out=/backup/$(date +%Y%m%d_%H%M%S) \
  --db=storai_booker

# Copy backup to host
docker cp storai-mongodb-prod:/backup ./mongodb_backup

# Restore MongoDB
docker exec storai-mongodb-prod mongorestore \
  --db=storai_booker \
  /backup/20240115_120000
```

### MinIO Backup

```bash
# Backup MinIO data
docker run --rm \
  -v storai-booker_minio_data:/data \
  -v $(pwd)/minio_backup:/backup \
  alpine tar czf /backup/minio_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore MinIO data
docker run --rm \
  -v storai-booker_minio_data:/data \
  -v $(pwd)/minio_backup:/backup \
  alpine tar xzf /backup/minio_20240115_120000.tar.gz -C /data
```

### Updates & Upgrades

```bash
# Pull latest code
git pull origin main

# Rebuild and restart services (zero-downtime)
docker compose -f docker-compose.prod.yml up -d --build --no-deps backend
docker compose -f docker-compose.prod.yml up -d --build --no-deps celery-worker
docker compose -f docker-compose.prod.yml up -d --build --no-deps frontend

# OR full restart (brief downtime)
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs [service-name]

# Common issues:
# 1. Port already in use
sudo lsof -i :80  # Check what's using port 80
sudo lsof -i :8000

# 2. Out of disk space
df -h
docker system prune -a  # WARNING: Removes unused images

# 3. Environment variables not set
docker compose -f docker-compose.prod.yml config  # Shows resolved config
```

### Story Generation Failing

```bash
# Check Celery worker logs
docker compose -f docker-compose.prod.yml logs -f celery-worker

# Common issues:
# 1. API key not set or invalid
# 2. Rate limiting from LLM provider
# 3. Out of memory (check docker stats)

# Restart worker
docker compose -f docker-compose.prod.yml restart celery-worker
```

### High Memory Usage

```bash
# Check stats
docker stats

# Reduce Celery concurrency
# Edit docker-compose.prod.yml:
# command: celery ... --concurrency=2  # Instead of 4

# Restart with new settings
docker compose -f docker-compose.prod.yml up -d celery-worker
```

### Database Connection Issues

```bash
# Check MongoDB health
docker compose -f docker-compose.prod.yml exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check if backend can reach MongoDB
docker compose -f docker-compose.prod.yml exec backend curl mongodb:27017

# Restart MongoDB (will cause brief downtime)
docker compose -f docker-compose.prod.yml restart mongodb
```

## Security Considerations

### 1. Change Default Credentials

**Critical**: Change `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` in `.env.production`

```bash
# Generate strong password
openssl rand -base64 32
```

### 2. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp    # Frontend
sudo ufw allow 8000/tcp  # Backend API (optional - can be internal only)
sudo ufw deny 27017/tcp  # Block MongoDB from external access
sudo ufw deny 6379/tcp   # Block Redis from external access
sudo ufw deny 9000/tcp   # Block MinIO API (use MinIO console for admin)
sudo ufw enable
```

### 3. HTTPS/SSL

For production with a domain:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Add to nginx.conf:
# server {
#     listen 443 ssl;
#     ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
# }
```

### 4. API Key Security

- Store API keys in `.env.production` only
- Never commit `.env.production` to Git
- Use read-only API keys where possible
- Rotate keys periodically
- Consider using secrets management (AWS Secrets Manager, Vault)

### 5. Network Isolation

The production compose file uses a custom bridge network (`storai-network`). Services can only communicate within this network.

### 6. Regular Updates

```bash
# Update base images monthly
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Production Checklist

Before going live:

- [ ] Change all default passwords (MinIO, etc.)
- [ ] Set up HTTPS/SSL if using domain name
- [ ] Configure firewall (UFW or cloud security groups)
- [ ] Set up automated backups (MongoDB + MinIO)
- [ ] Configure monitoring/alerts
- [ ] Test story generation end-to-end
- [ ] Document your specific deployment settings
- [ ] Set up log rotation
- [ ] Plan maintenance windows
- [ ] Test restore from backup

## Support

For issues:
- Check logs first: `docker compose -f docker-compose.prod.yml logs`
- Review troubleshooting section above
- Open issue on GitHub: https://github.com/your-username/storai-booker/issues

## License

See LICENSE file in repository root.
