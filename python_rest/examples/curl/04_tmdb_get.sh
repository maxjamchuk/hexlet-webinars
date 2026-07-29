#!/usr/bin/env sh
set -eu

if [ -z "${TMDB_API_KEY:-}" ]; then
    echo "TMDB_API_KEY is not set. Export a TMDB API Key v3 first." >&2
    exit 1
fi

TMDB_BASE_URL="https://api.themoviedb.org/3"

echo "Search TMDB for Interstellar"
curl -i -G "${TMDB_BASE_URL}/search/movie" \
    -H "Accept: application/json" \
    --data-urlencode "api_key=${TMDB_API_KEY}" \
    --data-urlencode "query=Interstellar" \
    --data-urlencode "language=en-US" \
    --data-urlencode "page=1"

TMDB_MOVIE_ID="${TMDB_MOVIE_ID:-157336}"

echo
echo "Get TMDB movie details for ID ${TMDB_MOVIE_ID}"
curl -i -G "${TMDB_BASE_URL}/movie/${TMDB_MOVIE_ID}" \
    -H "Accept: application/json" \
    --data-urlencode "api_key=${TMDB_API_KEY}" \
    --data-urlencode "language=en-US"
