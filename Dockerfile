# syntax=docker/dockerfile:1

# Use a slim Python base image for both builder and final stages
FROM python:3.11-slim AS base

# Builder stage: install dependencies into a virtual environment
FROM base AS builder
WORKDIR /app

# Copy only requirements files first for better cache utilization
COPY --link requirements*.txt ./

# Create virtual environment and install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m venv .venv && \
    .venv/bin/pip install --upgrade pip setuptools && \
    if [ -f requirements.txt ]; then .venv/bin/pip install -r requirements.txt; fi

# Copy the rest of the application code
COPY --link . .

# Final stage: minimal image with only runtime needs
FROM base AS final
WORKDIR /app

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
# Copy application code
COPY --from=builder /app /app

# Set environment to use the venv
ENV PATH="/app/.venv/bin:$PATH"

# Use non-root user
USER appuser

# Default command (update as needed based on your app's entrypoint)
CMD ["python", "main.py"]
