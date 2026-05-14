# =========================
# STAGE 1 — BUILD NEXT.JS
# =========================
FROM node:20-alpine AS node-build

WORKDIR /app

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# Copy package files first
COPY web-node/package*.json ./

# Install dependencies
RUN npm install

# Copy source
COPY web-node/ ./

# Build Next.js app
RUN npm run build


# =========================
# STAGE 2 — FINAL IMAGE
# =========================
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV STREAM_PORT=8080

WORKDIR /app

# Install system packages + Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    procps \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire Next.js app
COPY --from=node-build /app /app/web-node

# Copy Python files
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose ports
EXPOSE 3000
EXPOSE 8080
EXPOSE 8001

# Start services
CMD ["./entrypoint.sh"]
