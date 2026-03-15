#!/bin/bash
# quick setup — built to run entirely via Docker

set -e

echo "=== GovScheme AI Setup ==="
echo "Building and starting everything via Docker Compose..."
docker-compose up --build -d

echo ""
echo "Done! The app is starting up."
echo "It may take 10-15 seconds for the database and ingestion to complete."
echo ""
echo "Open your browser at:"
echo "  http://localhost:8501"
