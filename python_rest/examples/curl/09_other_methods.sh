#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"
MOVIE_ID="${1:-1}"

echo "HEAD: status and X-Total-Count/X-Limit/X-Offset, but no body"
curl -I "${API_BASE_URL}/movies?limit=5&offset=2"

echo
echo "OPTIONS for the collection"
curl -i -X OPTIONS "${API_BASE_URL}/movies"

echo
echo "OPTIONS for one resource path"
curl -i -X OPTIONS "${API_BASE_URL}/movies/${MOVIE_ID}"

echo
echo "TRACE exists in HTTP but is not supported by this API"
curl -i -X TRACE "${API_BASE_URL}/movies"
