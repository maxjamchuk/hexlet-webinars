#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"

echo "Successful path parameter: movie_id=1"
curl -i "${API_BASE_URL}/movies/1"

echo
echo "Unknown path parameter: movie_id=999999"
curl -i "${API_BASE_URL}/movies/999999"
