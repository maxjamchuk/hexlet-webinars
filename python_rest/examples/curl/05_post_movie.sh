#!/usr/bin/env sh
set -eu
API_BASE_URL="${API_BASE_URL:-http://localhost:8080}"
API_BASE_URL="${API_BASE_URL%/}"
MODE="${1:-minimal}"

case "$MODE" in
    minimal)
        PAYLOAD='{"title":"Workshop Movie"}'
        ;;
    full)
        PAYLOAD='{"title":"Workshop Movie","original_title":"Workshop Movie","overview":"A movie created during the REST API workshop.","release_date":"2026-07-19","vote_average":7.5,"vote_count":1,"poster_path":null,"genres":["Comedy"],"original_language":"en"}'
        ;;
    *)
        echo "Usage: $0 [minimal|full]" >&2
        exit 2
        ;;
esac

echo "POST ${API_BASE_URL}/movies (${MODE} payload)"
echo "Copy the actual id from JSON or the Location header."
curl -i -X POST "${API_BASE_URL}/movies" \
    -H "Content-Type: application/json" \
    --data "$PAYLOAD"

echo
echo "Validation error: an empty title returns 422"
curl -i -X POST "${API_BASE_URL}/movies" \
    -H "Content-Type: application/json" \
    --data '{"title":"   "}'
