FROM python:3.11-slim

# Install system dependencies and UV
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Create app directory
WORKDIR /opt/custos

# Copy pyproject.toml and install Python dependencies with UV
COPY pyproject.toml .
RUN uv pip install --system Flask==2.3.3 gunicorn==21.2.0

# Copy application files
COPY custos_server.py .
COPY setup_custos.py .

# Create custos user
RUN useradd -m -u 1000 custos

# Run initial setup as root to create config
RUN python setup_custos.py

# Copy tokens to accessible location
RUN cp /root/custos-tokens.txt /opt/custos/custos-tokens.txt

# Fix ownership after setup
RUN chown -R custos:custos /opt/custos

# Expose port
EXPOSE 5555

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5555/health || exit 1

# Run as non-root user
USER custos

# Start server with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5555", "--workers", "2", "--timeout", "30", "--access-logfile", "-", "custos_server:app"]