#!/bin/bash
# Helper script to start StorAI-Booker services

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting StorAI-Booker Services ===${NC}\n"

# Check if we can run docker without sudo
if docker ps &> /dev/null; then
    DOCKER_CMD="docker"
    echo -e "${GREEN}✓ Docker is accessible${NC}"
else
    echo -e "${YELLOW}! Docker requires sudo${NC}"
    DOCKER_CMD="sudo docker"
fi

# Check if services are already running
echo -e "\n${BLUE}Checking service status...${NC}"
if $DOCKER_CMD ps --format '{{.Names}}' | grep -q "storai"; then
    echo -e "${YELLOW}Some services are already running:${NC}"
    $DOCKER_CMD ps --filter "name=storai" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    read -p "Do you want to restart services? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Stopping existing services...${NC}"
        $DOCKER_CMD compose down
    else
        echo -e "${GREEN}Using existing services${NC}"
        exit 0
    fi
fi

# Start services
echo -e "\n${BLUE}Starting Docker Compose services...${NC}"
if [ "$DOCKER_CMD" = "sudo docker" ]; then
    sudo docker compose up -d
else
    docker compose up -d
fi

# Wait for services to be ready
echo -e "\n${BLUE}Waiting for services to be ready...${NC}"
sleep 5

# Check service health
echo -e "\n${BLUE}Service Status:${NC}"
$DOCKER_CMD compose ps

# Test MongoDB
echo -e "\n${BLUE}Testing MongoDB connection...${NC}"
if $DOCKER_CMD compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MongoDB is ready${NC}"
else
    echo -e "${RED}✗ MongoDB is not responding${NC}"
fi

# Test Redis
echo -e "\n${BLUE}Testing Redis connection...${NC}"
if $DOCKER_CMD compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is ready${NC}"
else
    echo -e "${RED}✗ Redis is not responding${NC}"
fi

# Test MinIO
echo -e "\n${BLUE}Testing MinIO connection...${NC}"
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MinIO is ready${NC}"
else
    echo -e "${RED}✗ MinIO is not responding${NC}"
fi

echo -e "\n${GREEN}=== Services Started ===${NC}"
echo -e "
Services are now running:
  - MongoDB:  localhost:27017
  - Redis:    localhost:6379
  - MinIO:    localhost:9000 (API)
              localhost:9001 (Console)

Next steps:
  1. cd backend
  2. poetry install
  3. cp .env.example .env
  4. poetry run python main.py

Then run: ./test_phase1.sh
"
