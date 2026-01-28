FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
# Install system dependencies required for Prisma and general usage
ENV TERM=xterm
RUN apt-get update && apt-get install -y \
    openssl \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Fix Prisma Schema for Docker: Remove custom output path to use default (site-packages)
# The local setup uses a venv path which isn't valid here
RUN sed -i '/output *= *"\.\.\/venv\/lib\/python3.11\/site-packages\/prisma"/d' artilaries_prisma/schema.prisma
RUN sed -i '/output *= *"\.\.\/venv\/lib\/python3.11\/site-packages\/prisma"/d' compex-db_prisma/schema.prisma

# Generate Prisma Clients
RUN prisma generate --schema=artilaries_prisma/schema.prisma
RUN prisma generate --schema=compex-db_prisma/schema.prisma

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Environment variables should be passed via docker run or docker-compose
# Expose port not needed really as this is a worker, but good practice if it had an API
# EXPOSE 8000

CMD ["./entrypoint.sh"]
