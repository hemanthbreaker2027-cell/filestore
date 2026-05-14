# Build stage for Node.js
FROM node:20 AS node-build
WORKDIR /app/web-node
COPY web-node/package*.json ./
RUN npm install
COPY web-node/ ./
RUN npm run build

# Final stage
FROM python:3.10-slim

# Install Node.js runtime
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy node app from build stage
COPY --from=node-build /app/web-node /app/web-node

# Copy the rest of the application
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Expose ports
EXPOSE 3000 8080 8001

CMD ["./entrypoint.sh"]
