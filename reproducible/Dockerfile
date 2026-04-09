# Dockerfile
FROM python:3.11-slim

# Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WALLET=my-wallet \
    NODE_URL=http://localhost:3030

# Create working directory
WORKDIR /app

# Copy RustChain Miner script into the image
COPY rustchain_universal_miner.py .

# Start the miner script
CMD ["python", "rustchain_universal_miner.py"]