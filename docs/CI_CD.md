# CI/CD Pipeline Documentation

Automated testing and deployment workflows for StorAI-Booker using GitHub Actions.

## Overview

The project includes comprehensive CI/CD pipelines that automatically test, build, and validate code changes on every push and pull request.

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers:** Pull requests to `main` branch

**Purpose:** Comprehensive pre-merge validation gate

**Jobs:**
- ✅ Backend tests with coverage (45% minimum)
- ✅ Backend code quality (Black, Ruff)
- ✅ Frontend build and lint
- ✅ Frontend TypeScript type checking
- ✅ Docker image builds (both backend and frontend)
- ✅ Summary report

**Services:**
- MongoDB 7.0 (for backend tests)
- Redis 7 (for backend tests)

**Status:** Must pass before merging to main

---

### 2. Backend Tests (`backend-tests.yml`)

**Triggers:**
- Push to `main`, `develop`, `phase-*` branches
- Pull requests to `main`, `develop`
- Changes to `backend/**` or workflow file

**What it does:**
1. Sets up Python 3.10 environment
2. Installs Poetry and dependencies (with caching)
3. Spins up MongoDB and Redis services
4. Runs pytest with coverage
5. Uploads coverage to Codecov
6. Fails if coverage drops below 45%

**Environment Variables:**
```yaml
MONGODB_URL: mongodb://localhost:27017
REDIS_URL: redis://localhost:6379/0
ENV: test
SECRET_KEY: test-secret-key-for-ci
```

**Coverage Reports:**
- Terminal output (in job logs)
- XML report (uploaded to Codecov)
- Minimum threshold: 45%

**Cache Strategy:**
- Python virtual environment cached
- Key: OS + poetry.lock hash
- Significantly speeds up subsequent runs

---

### 3. Frontend Build (`frontend-build.yml`)

**Triggers:**
- Push to `main`, `develop`, `phase-*` branches
- Pull requests to `main`, `develop`
- Changes to `frontend/**` or workflow file

**What it does:**
1. Sets up Node.js 18 environment
2. Installs npm dependencies (with caching)
3. Runs ESLint
4. Builds production bundle
5. Verifies build artifacts exist
6. Uploads build artifacts (7 day retention)

**Build Verification:**
- Checks `dist/` directory exists
- Lists build output
- Fails if build produces no output

**Artifacts:**
- Name: `frontend-build`
- Location: `frontend/dist/`
- Retention: 7 days

---

### 4. Code Quality (`code-quality.yml`)

**Triggers:**
- Push to `main`, `develop`, `phase-*` branches
- Pull requests to `main`, `develop`

**Backend Quality Checks:**
1. **Ruff** - Fast Python linter
   - Checks code style violations
   - Detects common bugs
   - Enforces best practices

2. **Black** - Code formatter
   - Ensures consistent formatting
   - Runs in check mode (no changes)

3. **MyPy** - Static type checker
   - Type checks with `--ignore-missing-imports`
   - Non-blocking (warnings only)

**Frontend Quality Checks:**
1. **ESLint** - JavaScript/TypeScript linter
   - Enforces code style
   - Detects potential bugs

2. **TypeScript Compiler** - Type checking
   - Runs `tsc --noEmit`
   - Ensures type safety

---

### 5. Docker Build (`docker-build.yml`)

**Triggers:**
- Push to `main`, `phase-5/*` branches
- Pull requests to `main`
- Changes to Dockerfiles or docker-compose

**What it does:**
1. Sets up Docker Buildx for caching
2. Builds backend Docker image
3. Tests backend image (poetry version check)
4. Builds frontend Docker image
5. Tests frontend image (nginx version check)

**Images Built:**
- Backend: `storai-backend:ci-{sha}`
- Frontend: `storai-frontend:ci-{sha}`

**Build Cache:**
- Uses GitHub Actions cache
- Mode: `max` (cache all layers)
- Speeds up subsequent builds

**Testing:**
- Backend: Verifies Poetry installation
- Frontend: Verifies Nginx installation

---

## Badge Status

Add these badges to your README for CI status visibility:

```markdown
![CI](https://github.com/yourusername/storai-booker/workflows/CI/badge.svg)
![Backend Tests](https://github.com/yourusername/storai-booker/workflows/Backend%20Tests/badge.svg)
![Frontend Build](https://github.com/yourusername/storai-booker/workflows/Frontend%20Build/badge.svg)
![Code Quality](https://github.com/yourusername/storai-booker/workflows/Code%20Quality/badge.svg)
```

---

## Local Testing

Before pushing, you can run the same checks locally:

### Backend

```bash
cd backend

# Run tests
poetry run pytest --cov=app --cov-fail-under=45

# Check formatting
poetry run black --check .

# Run linting
poetry run ruff check .

# Type checking
poetry run mypy . --ignore-missing-imports
```

### Frontend

```bash
cd frontend

# Run linting
npm run lint

# Type checking
npx tsc --noEmit

# Build
npm run build
```

### Docker

```bash
# Build backend image
docker build -f backend/Dockerfile.prod -t storai-backend:local backend/

# Build frontend image
docker build -f frontend/Dockerfile.prod -t storai-frontend:local frontend/

# Test images
docker run --rm storai-backend:local poetry --version
docker run --rm storai-frontend:local nginx -v
```

---

## Workflow Triggers

### Branch Patterns

| Workflow | main | develop | phase-* | Pull Requests |
|----------|------|---------|---------|---------------|
| CI | ❌ | ❌ | ❌ | ✅ (to main) |
| Backend Tests | ✅ | ✅ | ✅ | ✅ |
| Frontend Build | ✅ | ✅ | ✅ | ✅ |
| Code Quality | ✅ | ✅ | ✅ | ✅ |
| Docker Build | ✅ | ❌ | ✅ (phase-5/*) | ✅ (to main) |

### Path Filters

Workflows only run when relevant files change:

**Backend Tests:**
- `backend/**`
- `.github/workflows/backend-tests.yml`

**Frontend Build:**
- `frontend/**`
- `.github/workflows/frontend-build.yml`

**Docker Build:**
- `backend/**`
- `frontend/**`
- `docker-compose.yml`
- `Dockerfile.*`

---

## Caching Strategy

### Python Dependencies

```yaml
cache:
  path: backend/.venv
  key: venv-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
```

**Benefits:**
- Speeds up workflow by ~2-3 minutes
- Cache invalidates when dependencies change
- Separate cache per OS

### Node Dependencies

```yaml
cache: 'npm'
cache-dependency-path: frontend/package-lock.json
```

**Benefits:**
- Automatic npm cache management
- Faster npm ci execution
- Cache invalidates when package-lock.json changes

### Docker Build Cache

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

**Benefits:**
- Reuses Docker layers between builds
- Significantly faster rebuilds
- Shared across workflow runs

---

## Secrets Configuration

Some workflows may require secrets (not currently used):

### Codecov (Optional)

If you want private Codecov integration:

1. Go to repository Settings → Secrets
2. Add `CODECOV_TOKEN`
3. Update `backend-tests.yml`:
   ```yaml
   - name: Upload coverage to Codecov
     env:
       CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
   ```

### Docker Registry (Optional)

For pushing images to Docker Hub/GHCR:

1. Add secrets:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`

2. Update `docker-build.yml`:
   ```yaml
   - name: Login to Docker Hub
     uses: docker/login-action@v3
     with:
       username: ${{ secrets.DOCKER_USERNAME }}
       password: ${{ secrets.DOCKER_PASSWORD }}

   - name: Build and Push
     uses: docker/build-push-action@v5
     with:
       push: true
       tags: username/storai-backend:latest
   ```

---

## Troubleshooting

### Workflow Fails: "poetry: command not found"

**Cause:** Poetry installation step failed

**Solution:**
- Check Poetry version in workflow matches your local version
- Verify `snok/install-poetry@v1` action is working
- Check GitHub Actions status page for outages

---

### Workflow Fails: MongoDB connection refused

**Cause:** MongoDB service not ready

**Solution:**
- Health checks should prevent this
- Increase health check intervals if needed
- Verify MongoDB version compatibility

---

### Workflow Fails: Coverage below threshold

**Cause:** Test coverage dropped below 45%

**Solution:**
- Add tests for new code
- Check coverage report in job logs
- Run `pytest --cov=app --cov-report=term` locally

---

### Docker Build Fails: "failed to solve with frontend dockerfile.v0"

**Cause:** Dockerfile syntax error or missing file

**Solution:**
- Verify Dockerfile exists at specified path
- Check Dockerfile syntax locally
- Ensure all COPY paths are correct

---

### Cache Not Working

**Cause:** Cache key changed or cache evicted

**Solution:**
- GitHub Actions caches are time-limited (7 days)
- Cache is evicted if total cache size exceeds 10 GB
- First run after eviction will be slower

---

## Performance Metrics

Typical workflow execution times (with cache):

| Workflow | Duration | Without Cache |
|----------|----------|---------------|
| CI | ~8-10 min | ~15 min |
| Backend Tests | ~3-4 min | ~8 min |
| Frontend Build | ~2-3 min | ~5 min |
| Code Quality | ~2-3 min | ~7 min |
| Docker Build | ~4-5 min | ~10 min |

**Bottlenecks:**
- Backend: Test execution (~2 min)
- Frontend: npm install (~1.5 min with cache)
- Docker: Layer builds (~3 min first time)

**Optimization Tips:**
- Keep dependencies up to date (reduces install time)
- Add more focused tests (reduce test execution time)
- Use matrix builds for parallel testing (future improvement)

---

## Future Enhancements

### Phase 6 Improvements

- [ ] E2E tests with Playwright
- [ ] Visual regression testing
- [ ] Performance benchmarking
- [ ] Automated dependency updates (Dependabot)
- [ ] Automated releases (semantic-release)
- [ ] Deploy previews for PRs
- [ ] Integration with Sentry for error tracking

### Matrix Testing

Run tests across multiple versions:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    node-version: ['18', '20']
```

### Parallel Test Execution

Split test suite for faster execution:

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
```

---

## Continuous Deployment

### Automated Deployment (Future)

When ready for CD:

1. **Staging Deployment:**
   - Trigger: Push to `develop`
   - Deploy to staging environment
   - Run smoke tests

2. **Production Deployment:**
   - Trigger: Push to `main` (after CI passes)
   - Build and tag Docker images
   - Deploy to production
   - Run health checks
   - Rollback on failure

3. **Environment-Specific Secrets:**
   - `STAGING_DEPLOY_KEY`
   - `PROD_DEPLOY_KEY`
   - `AWS_CREDENTIALS`

---

## Best Practices

### Before Committing

1. Run tests locally
2. Check code formatting
3. Run linting
4. Verify Docker builds (if changed)

### Pull Request Workflow

1. Create feature branch from `develop`
2. Make changes and commit
3. Push branch and create PR to `main`
4. Wait for CI to pass (all checks green)
5. Request review
6. Merge when approved and CI passes

### Handling CI Failures

1. Check which job failed
2. Read job logs for errors
3. Reproduce locally
4. Fix and push new commit
5. CI automatically re-runs

### Breaking Changes

If making breaking changes:

1. Update tests first
2. Update CI configuration if needed
3. Document changes in PR description
4. Update minimum coverage threshold if appropriate

---

**Last Updated**: 2025-12-17
**Version**: Phase 5.6
**Status**: Production-Ready CI/CD Pipeline
