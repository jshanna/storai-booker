# Docker Compose Commands Cheatsheet

Quick reference for managing StorAI-Booker with Docker Compose.

## Basic Commands

```bash
# Start all services
docker compose up -d

# Start with rebuild
docker compose up -d --build

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes all data)
docker compose down -v

# View status
docker compose ps

# View logs
docker compose logs -f

# Logs for specific service
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f frontend
```

## Service Management

```bash
# Restart specific service
docker compose restart backend

# Update single service without downtime
docker compose up -d --no-deps --build backend

# Scale Celery workers (if needed)
docker compose up -d --scale celery-worker=3
```

## Maintenance Commands

```bash
# Execute command in running container
docker compose exec backend bash
docker compose exec mongodb mongosh

# View resource usage
docker stats

# Prune unused resources
docker system prune
docker system prune -a  # WARNING: Removes all unused images

# View disk usage
docker system df

# List volumes
docker volume ls

# Inspect volume
docker volume inspect storai-booker_mongodb_data
```

## Database Operations

```bash
# Access MongoDB shell
docker compose exec mongodb mongosh storai_booker

# Access Redis CLI
docker compose exec redis redis-cli

# Backup MongoDB
docker compose exec mongodb \
  mongodump --out=/backup --db=storai_booker

# Copy backup to host
docker cp storai-mongodb:/backup ./mongodb_backup

# Restore MongoDB
docker compose exec mongodb \
  mongorestore --db=storai_booker /backup
```

## Debugging

```bash
# Check service health
docker compose ps

# View detailed container info
docker inspect storai-backend

# Check networks
docker network ls
docker network inspect storai-network

# Test connectivity between services
docker compose exec backend ping mongodb
docker compose exec backend curl http://redis:6379

# View environment variables
docker compose exec backend env

# Check resolved configuration
docker compose config
```

## Port Reference

| Service | Port(s) | Purpose |
|---------|---------|---------|
| Frontend | 80 | Web application |
| Backend | 8000 | API server |
| MongoDB | 27017 | Database |
| Redis | 6379 | Cache/Queue |
| MinIO | 9000 | S3 API |
| MinIO Console | 9001 | Admin UI |

## Common Workflows

### Full Restart

```bash
docker compose down
docker compose up -d
```

### Update Application Code

```bash
git pull
docker compose up -d --build
```

### Rolling Update (Zero Downtime)

```bash
# Update backend
docker compose up -d --no-deps --build backend

# Wait for health check
sleep 10

# Update Celery workers
docker compose up -d --no-deps --build celery-worker

# Update frontend
docker compose up -d --no-deps --build frontend
```

### Clean Rebuild

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### View All Logs Since Yesterday

```bash
docker compose logs --since 24h
```

### Follow Logs for Multiple Services

```bash
docker compose logs -f backend celery-worker
```

## Development Mode

For local development with hot-reload, start only infrastructure:

```bash
# Start only MongoDB, Redis, MinIO
docker compose up -d mongodb redis minio createbuckets

# Then run backend and frontend locally
# See QUICK_START.md for details
```
