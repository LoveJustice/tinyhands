FROM python:3.9-bookworm

# Disable Python output buffering to ensure real-time logging in Docker
ENV PYTHONUNBUFFERED 1

# Update the CA certificates to ensure the system has the latest trusted certificates
RUN update-ca-certificates

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/

# Copy and install dependencies from pyproject.toml
COPY pyproject.toml .
RUN uv pip install --system -e .

RUN mkdir -p /data /log

# Copy application code
COPY application/ /data/
WORKDIR /data/

CMD /bin/sh /data/bin/run.sh > /log/python.log 2>&1
