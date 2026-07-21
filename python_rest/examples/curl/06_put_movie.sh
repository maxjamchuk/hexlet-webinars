#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"
MOVIE_ID="${1:?Usage: $0 MOVIE_ID}"

echo "Full replacement of movie ${MOVIE_ID}"
curl -i -X PUT "${API_BASE_URL}/movies/${MOVIE_ID}" \
    -H "Content-Type: application/json" \
    --data '{"title":"Workshop Movie: Updated","original_title":"Workshop Movie: Updated","overview":"The entire editable representation was replaced.","release_date":"2026-07-20","vote_average":8.0,"vote_count":2,"poster_path":null,"genres":["Drama"],"original_language":"en"}'

echo
echo "Validation error: PUT is missing the required overview field"
curl -i -X PUT "${API_BASE_URL}/movies/${MOVIE_ID}" \
    -H "Content-Type: application/json" \
    --data '{"title":"Incomplete PUT","original_title":null,"release_date":null,"vote_average":0,"vote_count":0,"poster_path":null,"genres":[],"original_language":null}'
