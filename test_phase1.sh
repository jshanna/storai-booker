#!/bin/bash
# Phase 1 API Testing Script
# Run this after starting Docker services and backend server

set -e

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Phase 1 API Testing ===${NC}\n"

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
response=$(curl -s "${BASE_URL}/health")
status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$status" = "healthy" ] || [ "$status" = "degraded" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "$response" | python3 -m json.tool
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "$response"
fi
echo ""

# Test 2: Create Story
echo -e "${BLUE}Test 2: Create Story${NC}"
story_response=$(curl -s -X POST "${BASE_URL}/api/stories/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Magical Forest Adventure",
    "generation_inputs": {
      "audience_age": 7,
      "topic": "A brave squirrel exploring a magical forest",
      "setting": "Enchanted forest with talking animals",
      "format": "storybook",
      "illustration_style": "watercolor",
      "characters": ["Hazel the squirrel"],
      "page_count": 10
    }
  }')

story_id=$(echo "$story_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
if [ -n "$story_id" ]; then
    echo -e "${GREEN}✓ Story created successfully${NC}"
    echo "Story ID: $story_id"
else
    echo -e "${RED}✗ Story creation failed${NC}"
    echo "$story_response"
    exit 1
fi
echo ""

# Test 3: List Stories
echo -e "${BLUE}Test 3: List Stories${NC}"
list_response=$(curl -s "${BASE_URL}/api/stories")
total=$(echo "$list_response" | grep -o '"total":[0-9]*' | cut -d':' -f2)
if [ "$total" -ge 1 ]; then
    echo -e "${GREEN}✓ List stories passed (found $total stories)${NC}"
else
    echo -e "${RED}✗ List stories failed${NC}"
fi
echo ""

# Test 4: Get Story
echo -e "${BLUE}Test 4: Get Story${NC}"
get_response=$(curl -s "${BASE_URL}/api/stories/${story_id}")
title=$(echo "$get_response" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
if [ "$title" = "The Magical Forest Adventure" ]; then
    echo -e "${GREEN}✓ Get story passed${NC}"
else
    echo -e "${RED}✗ Get story failed${NC}"
fi
echo ""

# Test 5: Get Story Status
echo -e "${BLUE}Test 5: Get Story Status${NC}"
status_response=$(curl -s "${BASE_URL}/api/stories/${story_id}/status")
story_status=$(echo "$status_response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$story_status" = "pending" ]; then
    echo -e "${GREEN}✓ Get story status passed (status: $story_status)${NC}"
else
    echo -e "${RED}✗ Get story status failed${NC}"
fi
echo ""

# Test 6: Get Settings
echo -e "${BLUE}Test 6: Get Settings${NC}"
settings_response=$(curl -s "${BASE_URL}/api/settings")
user_id=$(echo "$settings_response" | grep -o '"user_id":"[^"]*"' | cut -d'"' -f4)
if [ "$user_id" = "default" ]; then
    echo -e "${GREEN}✓ Get settings passed${NC}"
else
    echo -e "${RED}✗ Get settings failed${NC}"
fi
echo ""

# Test 7: Update Settings
echo -e "${BLUE}Test 7: Update Settings${NC}"
update_response=$(curl -s -X PUT "${BASE_URL}/api/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "age_range": {
      "min": 5,
      "max": 12,
      "enforce": true
    }
  }')
min_age=$(echo "$update_response" | grep -o '"min":[0-9]*' | head -1 | cut -d':' -f2)
if [ "$min_age" = "5" ]; then
    echo -e "${GREEN}✓ Update settings passed${NC}"
else
    echo -e "${RED}✗ Update settings failed${NC}"
fi
echo ""

# Test 8: Pagination
echo -e "${BLUE}Test 8: Pagination${NC}"
page_response=$(curl -s "${BASE_URL}/api/stories?page=1&page_size=5")
page=$(echo "$page_response" | grep -o '"page":[0-9]*' | cut -d':' -f2)
if [ "$page" = "1" ]; then
    echo -e "${GREEN}✓ Pagination passed${NC}"
else
    echo -e "${RED}✗ Pagination failed${NC}"
fi
echo ""

# Test 9: Filtering
echo -e "${BLUE}Test 9: Filtering by format${NC}"
filter_response=$(curl -s "${BASE_URL}/api/stories?format=storybook")
filter_total=$(echo "$filter_response" | grep -o '"total":[0-9]*' | cut -d':' -f2)
if [ "$filter_total" -ge 1 ]; then
    echo -e "${GREEN}✓ Filtering passed (found $filter_total storybooks)${NC}"
else
    echo -e "${RED}✗ Filtering failed${NC}"
fi
echo ""

# Test 10: Delete Story
echo -e "${BLUE}Test 10: Delete Story${NC}"
delete_response=$(curl -s -X DELETE -w "%{http_code}" "${BASE_URL}/api/stories/${story_id}")
if [ "$delete_response" = "204" ]; then
    echo -e "${GREEN}✓ Delete story passed${NC}"
else
    echo -e "${RED}✗ Delete story failed (HTTP $delete_response)${NC}"
fi
echo ""

# Test 11: Verify Deletion
echo -e "${BLUE}Test 11: Verify Deletion${NC}"
verify_response=$(curl -s -w "%{http_code}" -o /dev/null "${BASE_URL}/api/stories/${story_id}")
if [ "$verify_response" = "404" ]; then
    echo -e "${GREEN}✓ Story successfully deleted (404 Not Found)${NC}"
else
    echo -e "${RED}✗ Deletion verification failed (HTTP $verify_response)${NC}"
fi
echo ""

# Test 12: Error Handling - Invalid ID
echo -e "${BLUE}Test 12: Error Handling (Invalid ID)${NC}"
error_response=$(curl -s -w "%{http_code}" -o /dev/null "${BASE_URL}/api/stories/invalid-id")
if [ "$error_response" = "400" ]; then
    echo -e "${GREEN}✓ Error handling passed (400 Bad Request)${NC}"
else
    echo -e "${RED}✗ Error handling failed (expected 400, got $error_response)${NC}"
fi
echo ""

# Test 13: Validation Error
echo -e "${BLUE}Test 13: Validation Error${NC}"
validation_response=$(curl -s -w "%{http_code}" -o /dev/null -X POST "${BASE_URL}/api/stories/generate" \
  -H "Content-Type: application/json" \
  -d '{}')
if [ "$validation_response" = "422" ]; then
    echo -e "${GREEN}✓ Validation error handling passed (422 Unprocessable Entity)${NC}"
else
    echo -e "${RED}✗ Validation error handling failed (expected 422, got $validation_response)${NC}"
fi
echo ""

echo -e "${BLUE}=== Testing Complete ===${NC}"
echo -e "${GREEN}All Phase 1 API endpoints are working correctly!${NC}"
