# Use Python 3.14 slim image
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy pyproject.toml and uv.lock first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install Python dependencies (including dev dependencies for Ruff)
RUN uv sync --frozen --group dev

# Copy project
COPY . .

# Create static files directory
RUN mkdir -p /app/staticfiles

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
