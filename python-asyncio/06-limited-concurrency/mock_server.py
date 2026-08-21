import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse


HOST = "127.0.0.1"
PORT = 8001


class DemoHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        if not parsed_url.path.startswith("/health/"):
            self.send_json(404, {"error": "route not found"})
            return

        service_name = unquote(parsed_url.path.removeprefix("/health/"))
        if not service_name:
            self.send_json(404, {"error": "service name is required"})
            return

        query = parse_qs(parsed_url.query)
        try:
            delay = max(0.0, float(query.get("delay", ["0"])[0]))
            status_code = int(query.get("status", ["200"])[0])
            if not 100 <= status_code <= 599:
                raise ValueError
        except ValueError:
            self.send_json(400, {"error": "invalid delay or status"})
            return

        # Локальный симулятор задержек: каждый запрос обслуживает отдельный поток.
        time.sleep(delay)
        payload: dict[str, object] = {
            "service": service_name,
            "status": "ok" if 200 <= status_code < 400 else "error",
            "delay": delay,
        }
        self.send_json(status_code, payload)

    def send_json(self, status_code: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            print(f"Клиент отключился до отправки ответа: {self.path}")

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.command} {self.path} -> {format % args}")


def main() -> None:
    server = DemoHTTPServer((HOST, PORT), HealthHandler)
    print(f"Mock-сервер запущен: http://{HOST}:{PORT}")
    print("Для остановки нажмите Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMock-сервер остановлен")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
