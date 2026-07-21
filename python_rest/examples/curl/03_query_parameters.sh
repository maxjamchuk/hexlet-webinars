#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"

echo "Filter by title"
curl -i "${API_BASE_URL}/movies?title=whiplash"

echo
echo "Filter by release year"
curl -i "${API_BASE_URL}/movies?year=2013"

echo
echo "Pagination"
curl -i "${API_BASE_URL}/movies?limit=5&offset=10"

echo
echo "Combined filters"
curl -i "${API_BASE_URL}/movies?title=whiplash&year=2013"

echo
echo "Validation error: limit must be at least 1"
curl -i "${API_BASE_URL}/movies?limit=0"
