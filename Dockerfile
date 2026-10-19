# ==============================================================================
# Chronos-Prove v2.0: Two-Tier Hybrid Architecture (Symbolic Core + AMD ROCm)
# Dual-Stage / Dual-Target Base Image Configuration:
# - Default: python:3.11-slim (Ultra-lightweight, zero-bloat Tier 1 Symbolic Core)
# - AMD ROCm Build: Pass --build-arg BASE_IMAGE=rocm/pytorch:rocm6.2_ubuntu22.04_py3.10_pytorch_release_2.3.0
# ==============================================================================

ARG BASE_IMAGE=python:3.11-slim

FROM ${BASE_IMAGE} AS base

# Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install minimal system dependencies for lxml and SSL certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight core dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, server, static cockpit, and tests
COPY app.py /app/app.py
COPY server.py /app/server.py
COPY static/ /app/static/
COPY tests/ /app/tests/

# Prepare dedicated output directory with permissive access for evaluation harnesses
RUN mkdir -p /app/output && chmod 777 /app/output

# Expose Web Cockpit Port
EXPOSE 8000

# Default entrypoint executes the official headless CLI evaluation contract:
# python3 /app/app.py --query-id <id> --query "<question>"
#
# Interactive Web Cockpit command:
# uvicorn server:app --host 0.0.0.0 --port 8000
ENTRYPOINT ["python3", "/app/app.py"]
