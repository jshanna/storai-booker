# Docker Compose Commands Cheatsheet

Quick reference for managing StorAI-Booker with Docker Compose.

## Development Commands

```bash
# Start infrastructure only (MongoDB, Redis, MinIO)
docker compose up -d

# Start all services including backend and Celery
docker compose --profile full up -d

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes all data)
docker compose down -v

# View logs
docker compose logs -f
docker compose logs -f backend
docker compose logs -f celery-worker

# Rebuild specific service
docker compose up -d --build backend

# Restart specific service
docker compose restart backend
```

## Production Commands

```bash
# Build all images
docker compose -f docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Start with build
docker compose -f docker-compose.prod.yml up -d --build

# Stop all services
docker compose -f docker-compose.prod.yml down

# View status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Logs for specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f celery-worker
docker compose -f docker-compose.prod.yml logs -f frontend

# Scale Celery workers
docker compose -f docker-compose.prod.yml up -d --scale celery-worker=3

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# Update single service without downtime
docker compose -f docker-compose.prod.yml up -d --no-deps --build backend
```

## Maintenance Commands

```bash
# Execute command in running container
docker compose -f docker-compose.prod.yml exec backend bash
docker compose -f docker-compose.prod.yml exec mongodb mongosh

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
docker compose -f docker-compose.prod.yml exec mongodb mongosh storai_booker

# Access Redis CLI
docker compose -f docker-compose.prod.yml exec redis redis-cli

# Backup MongoDB
docker compose -f docker-compose.prod.yml exec mongodb \
  mongodump --out=/backup --db=storai_booker

# Copy backup to host
docker cp storai-mongodb-prod:/backup ./mongodb_backup

# Restore MongoDB
docker compose -f docker-compose.prod.yml exec mongodb \
  mongorestore --db=storai_booker /backup
```

## Debugging

```bash
# Check service health
docker compose -f docker-compose.prod.yml ps

# View detailed container info
docker inspect storai-backend-prod

# Check networks
docker network ls
docker network inspect storai-network

# Test connectivity between services
docker compose -f docker-compose.prod.yml exec backend ping mongodb
docker compose -f docker-compose.prod.yml exec backend curl http://redis:6379

# View environment variables
docker compose -f docker-compose.prod.yml exec backend env

# Check resolved configuration
docker compose -f docker-compose.prod.yml config
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
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Update Application Code

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

### Rolling Update (Zero Downtime)

```bash
# Update backend
docker compose -f docker-compose.prod.yml up -d --no-deps --build backend

# Wait for health check
sleep 10

# Update Celery workers
docker compose -f docker-compose.prod.yml up -d --no-deps --build celery-worker

# Update frontend
docker compose -f docker-compose.prod.yml up -d --no-deps --build frontend
```

### Clean Rebuild

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### View All Logs Since Yesterday

```bash
docker compose -f docker-compose.prod.yml logs --since 24h
```

### Follow Logs for Multiple Services

```bash
docker compose -f docker-compose.prod.yml logs -f backend celery-worker
```
