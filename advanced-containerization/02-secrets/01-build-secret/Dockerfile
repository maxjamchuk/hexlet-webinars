# syntax=docker/dockerfile:1
FROM python:3.12-slim
WORKDIR /app
RUN --mount=type=secret,id=demo_token,required=true \
    token="$(cat /run/secrets/demo_token)" && test -n "$token" \
    && printf 'private resource fetched\n' > /app/build-result.txt
CMD ["cat", "/app/build-result.txt"]
