#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"

echo "GET ${API_BASE_URL}/movies?limit=3"
echo "GET is curl's default method; -i includes status and response headers."
curl -i "${API_BASE_URL}/movies?limit=3"
