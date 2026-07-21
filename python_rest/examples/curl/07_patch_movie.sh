#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"
MOVIE_ID="${1:?Usage: $0 MOVIE_ID}"

echo "PATCH sends only fields that need to change"
curl -i -X PATCH "${API_BASE_URL}/movies/${MOVIE_ID}" \
    -H "Content-Type: application/json" \
    --data '{"vote_average":9.0,"genres":["Drama","Comedy"]}'

echo
echo "Explicit null clears a nullable field"
curl -i -X PATCH "${API_BASE_URL}/movies/${MOVIE_ID}" \
    -H "Content-Type: application/json" \
    --data '{"overview":null}'

echo
echo "Validation error: an empty PATCH body returns 422"
curl -i -X PATCH "${API_BASE_URL}/movies/${MOVIE_ID}" \
    -H "Content-Type: application/json" \
    --data '{}'
