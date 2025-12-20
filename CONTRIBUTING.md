# Contributing to StorAI-Booker

Thank you for your interest in contributing to StorAI-Booker! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

Please be respectful and constructive in all interactions. We're building something together, and a positive environment helps everyone contribute their best work.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment** (see below)
4. **Create a branch** for your changes
5. **Make your changes** with appropriate tests
6. **Submit a pull request**

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.10+ with Poetry
- Node.js 18+ with npm
- Google API Key (for testing story generation)

### Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Start infrastructure
docker compose up -d

# Run the API server
poetry run python main.py

# In another terminal, run Celery worker
poetry run celery -A app.services.celery_app.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Verify Setup

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-story-templates` - New features
- `fix/story-generation-timeout` - Bug fixes
- `docs/update-api-reference` - Documentation
- `refactor/cleanup-auth-service` - Code refactoring

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add story template selection to generation form

- Add TemplatePicker component with category filters
- Create useTemplates hook for fetching templates
- Update GeneratePage to support template pre-fill
```

Use conventional commit prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Code Style

### Backend (Python)

We use the following tools for code quality:

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy .
```

**Guidelines:**
- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Keep functions focused and small
- Use meaningful variable names

**Example:**

```python
async def get_story_by_id(story_id: str, user_id: str) -> Story:
    """
    Retrieve a story by ID for a specific user.

    Args:
        story_id: The unique story identifier
        user_id: The owner's user ID

    Returns:
        The Story document if found

    Raises:
        HTTPException: If story not found or user doesn't have access
    """
    story = await Storybook.get(story_id)
    if not story or story.user_id != user_id:
        raise HTTPException(status_code=404, detail="Story not found")
    return story
```

### Frontend (TypeScript)

```bash
# Lint code
npm run lint

# Type checking
npm run typecheck

# Format code (if configured)
npm run format
```

**Guidelines:**
- Use TypeScript strictly (avoid `any`)
- Define interfaces for all props and state
- Use functional components with hooks
- Keep components focused and reusable
- Use meaningful component and variable names

**Example:**

```typescript
interface StoryCardProps {
  story: Story;
  onDelete: (id: string) => void;
}

export function StoryCard({ story, onDelete }: StoryCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(story.id);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    // ...component JSX
  );
}
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_api_stories.py

# Run tests matching a pattern
poetry run pytest -k "test_create"
```

**Guidelines:**
- Write tests for new features and bug fixes
- Use fixtures for common test data
- Mock external services (LLM, storage)
- Test both success and error cases

### Frontend Tests

```bash
cd frontend

# Run tests (if configured)
npm run test
```

## Submitting Changes

### Pull Request Process

1. **Update your branch** with the latest main:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all checks** before submitting:
   ```bash
   # Backend
   cd backend
   poetry run black .
   poetry run ruff check .
   poetry run pytest

   # Frontend
   cd frontend
   npm run lint
   npm run build
   ```

3. **Create a pull request** with:
   - Clear title describing the change
   - Description of what and why
   - Link to related issue (if any)
   - Screenshots for UI changes

### PR Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
Describe how you tested the changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No console errors or warnings
```

### Review Process

- PRs require at least one approval before merging
- Address review feedback promptly
- Keep PRs focused and reasonably sized
- Large changes should be discussed in an issue first

## Issue Guidelines

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, etc.)
- Screenshots or error logs if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case / motivation
- Proposed implementation (if you have ideas)
- Any alternatives considered

### Questions

For questions about the codebase or implementation:
- Check existing documentation first
- Search closed issues for similar questions
- Provide context about what you're trying to do

## Project Structure

Understanding the project structure helps you find where to make changes:

```
backend/
├── app/
│   ├── api/           # REST endpoints - add new routes here
│   ├── models/        # Database models - add new collections here
│   ├── schemas/       # Request/response schemas
│   ├── services/      # Business logic
│   │   ├── agents/    # LLM agents for story generation
│   │   ├── export/    # PDF, EPUB, etc. exporters
│   │   └── ...
│   └── middleware/    # Request processing

frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page-level components
│   ├── lib/
│   │   ├── api/       # API client functions
│   │   ├── hooks/     # Custom React hooks
│   │   └── stores/    # Zustand state stores
│   └── types/         # TypeScript types
```

## Getting Help

- Check the [documentation](docs/)
- Look at existing code for patterns
- Open an issue for questions
- Review the [troubleshooting guide](docs/TROUBLESHOOTING.md)

## License

By contributing to StorAI-Booker, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing!
