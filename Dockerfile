FROM python:3.10-slim

# Install system dependencies for Node.js
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy and install Node.js dependencies
COPY web-node/package*.json ./web-node/
RUN cd web-node && npm install

# Copy the rest of the application
COPY . .

# Build Next.js
RUN cd web-node && npm run build

# Use a shell script to run both processes
RUN echo "#!/bin/bash\npython3 main.py & (cd web-node && npm run start) & (cd web-node && npm run stream)\nwait -n\nexit \$?" > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
