# ==============================================================================
# Stage 1: Base Image (Python + uv)
# ==============================================================================
FROM ghcr.io/bare-devcontainer/uv:trixie AS base

WORKDIR /app

# Configure uv default linking mode
ENV UV_LINK_MODE=copy

# ==============================================================================
# Stage 2: Development Stage (Used by .devcontainer/devcontainer.json)
# ==============================================================================
FROM base AS development

# Ensure user permissions and cache directories exist for the non-root 'dev' user
USER dev

# ==============================================================================
# Stage 3: Production Stage (Standalone Product Container)
# ==============================================================================
FROM base AS production

# Switch to non-root user for security
USER dev

# Copy dependency files first to leverage Docker layer caching
COPY --chown=dev:dev pyproject.toml uv.lock* ./

# Sync production dependencies using uv (creates /app/.venv)
RUN uv sync --frozen --no-dev

# Copy application source code into the image
COPY --chown=dev:dev . .

# Expose production port
EXPOSE 3002

# Run your application using virtual environment python executable
CMD ["uv", "run", "python", "-m", "main"]