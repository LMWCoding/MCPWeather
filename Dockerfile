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

# Expose development port (same as production for consistency)
EXPOSE 3002

# ==============================================================================
# Stage 3: Production Stage (Standalone Product Container)
# ==============================================================================
FROM base AS production

# Switch to non-root user for security
USER dev

# Copy dependency files and source code
COPY --chown=dev:dev . .

# Sync production dependencies using uv (creates /app/.venv)
RUN uv sync --frozen --no-dev

# Expose production port
EXPOSE 3002

# Run your application using virtual environment python executable
CMD ["uv", "run", "python", "-m", "combinedserver"]