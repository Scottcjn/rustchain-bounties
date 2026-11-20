FROM python:3.9-slim

LABEL maintainer="Xiaomili 🌾 <xiaomili@sjykj.com>"
LABEL description="RustChain Miner Status Notification System"

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests

# Copy application files
COPY miner_monitor.py .
COPY config.example.json config.json

# Create log directory
RUN mkdir -p /app/logs

# Run the monitor
CMD ["python3", "miner_monitor.py"]
