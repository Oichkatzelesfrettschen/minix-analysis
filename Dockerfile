# Multi-stage Dockerfile for OS Analysis Toolkit
# Stage 1: Builder
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy source code
COPY setup.py .
COPY src/ ./src/
COPY tools/ ./tools/

# Build the package
RUN python setup.py bdist_wheel

# Stage 2: LaTeX environment for diagram generation
FROM texlive/texlive:latest as latex

# Install ImageMagick for PNG conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    imagemagick \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy TikZ templates
COPY diagrams/tikz/ /app/diagrams/tikz/

# Stage 3: Runtime
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-pictures \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Remove ImageMagick PDF restrictions
RUN sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml || true

# Create non-root user
RUN useradd -m -u 1000 analyst && \
    mkdir -p /app /data /output && \
    chown -R analyst:analyst /app /data /output

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder --chown=analyst:analyst /root/.local /home/analyst/.local

# Copy application
COPY --chown=analyst:analyst . /app/

# Install the package
RUN pip install -e .

# Switch to non-root user
USER analyst

# Add local bin to PATH
ENV PATH=/home/analyst/.local/bin:$PATH

# Expose dashboard port
EXPOSE 8050

# Volume mounts
VOLUME ["/data", "/output", "/minix-source"]

# Default command
CMD ["os-analyze", "--help"]

# Labels
LABEL maintainer="MINIX Analysis Team"
LABEL version="1.0.0"
LABEL description="Comprehensive OS Analysis Toolkit"