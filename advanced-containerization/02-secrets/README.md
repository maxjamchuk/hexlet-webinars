# Секреты сборки

[00-bad](00-bad/) сохраняет фальшивый токен в ENV.
[01-build-secret](01-build-secret/) получает его только на время RUN через BuildKit.
Оба примера независимы и используют только базовый Python image, без Python-зависимостей.

Токен `demo-token-for-build` — учебная строка. `.demo-secret` игнорируется Git и
Docker, `demo-secret.example` тоже исключён из build context. Никаких внешних
закрытых ресурсов пример не запрашивает: результат получения ресурса имитируется.

При проверке отсутствующего секрета нужен `--no-cache`: наличие и содержимое
секрета не проверяются повторно, если RUN взят из layer cache.
См. [правила кеширования Docker](https://docs.docker.com/build/cache/invalidation/)
и [Build secrets](https://docs.docker.com/build/building/secrets/).
