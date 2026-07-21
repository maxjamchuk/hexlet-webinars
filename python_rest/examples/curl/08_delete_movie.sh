#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"
MOVIE_ID="${1:?Usage: $0 MOVIE_ID}"

echo "DELETE returns 204 with no response body"
curl -i -X DELETE "${API_BASE_URL}/movies/${MOVIE_ID}"

echo
echo "GET after deletion returns 404"
curl -i "${API_BASE_URL}/movies/${MOVIE_ID}"

echo
echo "Repeated DELETE also returns 404"
curl -i -X DELETE "${API_BASE_URL}/movies/${MOVIE_ID}"
