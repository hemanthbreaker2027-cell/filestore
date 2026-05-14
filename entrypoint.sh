#!/bin/bash
# Start the Python Bot
python3 main.py &

# Start the Next.js Protection Web Server
cd web-node && npm run start &

# Start the Fastify Streaming Server
cd web-node && npm run stream &

# Wait for any process to exit
wait -n

# Exit with status of the process that exited
exit $?
