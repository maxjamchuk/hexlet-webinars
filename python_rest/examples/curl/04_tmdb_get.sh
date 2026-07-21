#!/usr/bin/env sh
set -eu

if [ -z "${TMDB_API_TOKEN:-}" ]; then
    echo "TMDB_API_TOKEN is not set. Export a TMDB API Read Access Token first." >&2
    exit 1
fi

TMDB_BASE_URL="https://api.themoviedb.org/3"

echo "Search TMDB for Interstellar"
curl -i -G "${TMDB_BASE_URL}/search/movie" \
    -H "Authorization: Bearer ${TMDB_API_TOKEN}" \
    -H "Accept: application/json" \
    --data-urlencode "query=Interstellar" \
    --data-urlencode "language=en-US" \
    --data-urlencode "page=1"

# 157336 is Interstellar's public TMDB movie ID. Set TMDB_MOVIE_ID to inspect
# another ID copied from the search response without requiring jq.
TMDB_MOVIE_ID="${TMDB_MOVIE_ID:-157336}"

echo
echo "Get TMDB movie details for ID ${TMDB_MOVIE_ID}"
curl -i -G "${TMDB_BASE_URL}/movie/${TMDB_MOVIE_ID}" \
    -H "Authorization: Bearer ${TMDB_API_TOKEN}" \
    -H "Accept: application/json" \
    --data-urlencode "language=en-US"
