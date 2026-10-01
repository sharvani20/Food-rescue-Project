# Multi-Stage Dockerfile for AI Food Rescue Platform

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI Backend + Served Frontend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for OR-Tools & C libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements & install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir pydantic-settings email-validator httpx

# Copy backend source code
COPY backend ./backend

# Copy built frontend dist from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Seed database and run server
CMD ["sh", "-c", "python backend/seed.py && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
