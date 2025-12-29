# Networth Tracker Backend

Django REST API for tracking net worth across multiple asset types.

## Development Setup

1. Install dependencies:
   ```bash
   uv sync --group dev
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Run migrations:
   ```bash
   uv run python manage.py migrate
   ```

4. Start development server:
   ```bash
   uv run python manage.py runserver
   ```

## Code Quality with Ruff

This project uses Ruff for Python linting and formatting.

### Manual Usage

- **Check for issues**: `uv run ruff check .`
- **Fix issues automatically**: `uv run ruff check --fix .`
- **Format code**: `uv run ruff format .`

### Pre-commit Hooks

Pre-commit hooks are configured to automatically run Ruff before each commit:

```bash
# Install hooks (one-time setup)
uv run pre-commit install

# Run hooks manually on all files
uv run pre-commit run --all-files

# Run hooks on staged files
uv run pre-commit run
```

### Configuration

Ruff is configured in `pyproject.toml`:

- **Line length**: 79 characters
- **Target Python**: 3.13
- **Excluded**: Migration files
- **Rules**: pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade

## Testing

Run tests with pytest:
```bash
uv run pytest
```

Run with coverage:
```bash
uv run pytest --cov=api --cov-report=html
```
