# Build stage for Node.js
FROM node:20 AS node-build
WORKDIR /app/web-node

# Copy package files and install dependencies
COPY web-node/package*.json ./
RUN npm install

# Copy source code and build
COPY web-node/ ./
RUN npm run build

# Final stage
FROM python:3.10-slim

# Set non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js runtime and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    procps \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy built node application from build stage
COPY --from=node-build /app/web-node /app/web-node

# Copy the rest of the application
COPY . .

# Ensure scripts are executable
RUN chmod +x entrypoint.sh

# Set environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV STREAM_PORT=8080

# Expose ports
EXPOSE 3000 8080 8001

# Use entrypoint to run bot and web processes
CMD ["./entrypoint.sh"]
