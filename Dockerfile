# ── Stage 1: Build Vue.js frontend ─────────────────────────────────────────
FROM node:20-slim AS frontend-builder

# src/i18n/index.js imports ../../../locales/ (project root), so mirror the
# same directory structure that the dev environment provides.
WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN npm ci --prefix frontend

COPY frontend/ ./frontend/
COPY locales/  ./locales/

# Vite inlines VITE_* variables into the static bundle at build time, not at
# container runtime — they must be supplied as build args, not via .env/env_file.
ARG VITE_API_BASE_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY

RUN npm run build --prefix frontend

# ── Stage 2: Production image ───────────────────────────────────────────────
FROM python:3.11

# Install Nginx and Supervisor
RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx supervisor \
  && rm -rf /var/lib/apt/lists/* \
  && rm /etc/nginx/sites-enabled/default

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /app

# Install Python dependencies (cached layer — only rebuilds when deps change)
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN cd backend && uv sync --no-dev

# Copy backend source
COPY backend/ ./backend/

# Copy shared locales (backend/app/utils/locale.py reads ../../../locales/)
COPY locales/ ./locales/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy Nginx and Supervisor configs
COPY nginx.conf /etc/nginx/sites-enabled/mirofish.conf
COPY supervisord.conf /etc/supervisor/conf.d/mirofish.conf

EXPOSE 3000 5001

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
