"""Проверка настоящих Docker-контейнеров; только стандартная библиотека."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "demo-token-for-build"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class SmokeCheck:
    def __init__(self):
        self.prefix = f"hexlet-ac-smoke-{uuid.uuid4().hex[:10]}"
        self.containers = []
        self.images = []
        self.log_dir = ROOT / ".smoke-logs" / self.prefix
        self.log_dir.mkdir(parents=True)
        self.command_number = 0

    def command(self, args, *, cwd=ROOT, env=None, timeout=120, expected=0):
        self.command_number += 1
        started = time.monotonic()
        result = subprocess.run(
            [str(arg) for arg in args], cwd=cwd, env=env, timeout=timeout,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        log = self.log_dir / f"{self.command_number:03d}.log"
        log.write_text(
            f"{args}\nseconds: {time.monotonic() - started:.2f}\n"
            f"exit: {result.returncode}\n{result.stdout}\n{result.stderr}",
            encoding="utf-8",
        )
        if expected is not None and result.returncode != expected:
            raise RuntimeError(
                f"Command failed ({result.returncode}): {args}\n"
                f"{result.stdout}\n{result.stderr}\nLog: {log}"
            )
        return result

    def build(self, stage, *options, suffix=""):
        image = f"{self.prefix}-{stage.replace('/', '-')}{suffix}"
        self.images.append(image)
        started = time.monotonic()
        print(f"[BUILD] {stage}{suffix}", flush=True)
        self.command(
            ["docker", "build", "--progress=plain", "-t", image, *options, "."],
            cwd=ROOT / stage, timeout=600,
        )
        print(f"[OK] {stage}{suffix}: build {time.monotonic() - started:.1f}s", flush=True)
        return image

    def create(self, image, *command, options=()):
        name = f"{self.prefix}-{len(self.containers)}"
        # Зарегистрировать имя до create: даже частично успешный вызов будет очищен.
        self.containers.append(name)
        self.command(["docker", "create", "--name", name, *options, image, *command])
        return name

    def once(self, image, *command, expected=0):
        name = self.create(image, *command)
        return self.command(["docker", "start", "-a", name], expected=expected)

    def serve(self, image):
        name = self.create(image, options=("-p", "127.0.0.1::8000"))
        self.command(["docker", "start", name])
        address = self.command(["docker", "port", name, "8000/tcp"]).stdout.strip()
        return name, f"http://{address}"

    def inspect(self, name):
        return json.loads(self.command(["docker", "inspect", name]).stdout)[0]

    def http(self, url, status=200, method="GET", timeout=30):
        deadline = time.monotonic() + timeout
        last = "no response"
        while time.monotonic() < deadline:
            try:
                request = urllib.request.Request(url, method=method)
                try:
                    response = urllib.request.urlopen(request, timeout=2)
                except urllib.error.HTTPError as error:
                    response = error
                with response:
                    body = response.read().decode()
                    last = f"HTTP {response.status}: {body}"
                    if response.status == status:
                        return json.loads(body)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
                last = str(error)
            time.sleep(0.2)
        raise RuntimeError(f"{url}: expected HTTP {status}; {last}")

    def health(self, name, expected):
        started = time.monotonic()
        while time.monotonic() - started < 30:
            state = self.inspect(name)["State"]
            require(state["Running"], f"{name} stopped while waiting for health")
            if state["Health"]["Status"] == expected:
                return time.monotonic() - started
            time.sleep(0.5)
        raise RuntimeError(f"{name}: health did not become {expected}")

    def cleanup(self):
        ok = True
        for name in reversed(self.containers):
            try:
                exists = self.command(["docker", "inspect", name], expected=None)
                if exists.returncode == 0:
                    self.command(["docker", "rm", "-f", name])
            except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
                print(f"[FAIL] cleanup {name}: {error}", flush=True)
                ok = False
        # Удаляем только уникальные теги этого запуска. Build cache сохраняется.
        for image in self.images:
            try:
                result = self.command(["docker", "image", "rm", image], expected=None)
                if result.returncode and "No such image" not in result.stderr:
                    print(f"[FAIL] image cleanup: {result.stderr}", flush=True)
                    ok = False
            except (OSError, subprocess.TimeoutExpired) as error:
                print(f"[FAIL] image cleanup: {error}", flush=True)
                ok = False
        return ok


def check_build(check):
    for name in ("00-naive", "01-cache-friendly", "02-multi-stage", "03-buildkit-cache"):
        stage = f"01-build/{name}"
        image = check.build(stage)
        if name == "02-multi-stage":
            _, url = check.serve(image)
            require(check.http(url)["message"] == "Hello, Docker!", "Wrong response")
            check.once(image, "python", "-c", "import fastapi; print(fastapi.__version__)")
            result = check.once(image, "sh", "-c", "command -v uv", expected=None)
            require(result.returncode in (1, 127) and not result.stdout.strip()
                    and not result.stderr.strip(), "Unexpected uv lookup result")
            print(f"[OK] {stage}: HTTP 200, FastAPI import, uv absent", flush=True)
        if name == "03-buildkit-cache":
            check.build(stage, "--build-arg", "CACHE_BUST=2", suffix="-rebuild")


def check_secrets(check):
    bad = check.build("02-secrets/00-bad", "--build-arg", f"DEMO_TOKEN={TOKEN}")
    require(f"DEMO_TOKEN={TOKEN}" in check.inspect(bad)["Config"]["Env"], "Token missing")
    require(TOKEN in check.once(bad, "env").stdout, "Runtime token missing")
    print("[OK] 02-secrets/00-bad: demo token is visible as expected", flush=True)
    with tempfile.TemporaryDirectory(prefix=check.prefix) as temporary:
        secret = Path(temporary) / ".demo-secret"
        secret.write_text(TOKEN, encoding="utf-8")
        good = check.build("02-secrets/01-build-secret", "--secret", f"id=demo_token,src={secret}")
    result = check.once(good, "cat", "/app/build-result.txt")
    require(result.stdout.strip() == "private resource fetched", "Build result missing")
    require(TOKEN not in json.dumps(check.inspect(good)), "Token persisted in metadata")
    require(TOKEN not in check.once(good, "env").stdout, "Token persisted in env")
    check.once(good, "sh", "-c", "test ! -e /run/secrets/demo_token")
    history = check.command(["docker", "history", "--no-trunc", good]).stdout
    require(TOKEN not in history, "Token persisted in history")
    # Secret presence is not a layer-cache key: force RUN to execute again.
    failure = check.command(
        ["docker", "build", "--no-cache", "--progress=plain", "."],
        cwd=ROOT / "02-secrets/01-build-secret", timeout=600, expected=None,
    )
    require(failure.returncode != 0, "Build without a required secret unexpectedly passed")
    require("demo_token" in failure.stderr and "not found" in failure.stderr,
            "Build failed for a reason other than missing secret")
    print("[OK] 02-secrets/01-build-secret: secret not persisted; missing secret fails", flush=True)


def check_lifecycle(check):
    for stage in ("00-shell-form", "01-exec-graceful"):
        image = check.build(f"03-lifecycle/{stage}")
        name, url = check.serve(image)
        check.http(url)
        processes = check.command(["docker", "top", name]).stdout
        require("uvicorn" in processes, "Application process missing")
        started = time.monotonic()
        check.command(["docker", "stop", "-t", "2", name])
        logs = check.command(["docker", "logs", name])
        shutdown = "APP shutdown: cleanup complete" in logs.stdout
        state = check.inspect(name)["State"]
        require(not state["Running"], "Container did not stop")
        if stage == "01-exec-graceful":
            require(shutdown and state["ExitCode"] == 0, "Graceful shutdown failed")
        print(f"[OK] 03-lifecycle/{stage}: shutdown hook={shutdown}, "
              f"exit={state['ExitCode']}, stop {time.monotonic() - started:.1f}s", flush=True)
    image = check.build("03-lifecycle/02-healthcheck")
    name, url = check.serve(image)
    check.http(url + "/health")
    check.health(name, "healthy")
    check.command(["docker", "exec", name, "touch", "/tmp/unhealthy"])
    check.http(url + "/health", status=503)
    unhealthy = check.health(name, "unhealthy")
    check.command(["docker", "exec", name, "rm", "/tmp/unhealthy"])
    healthy = check.health(name, "healthy")
    check.http(url + "/health")
    print(f"[OK] 03-lifecycle/02-healthcheck: running; healthy -> unhealthy ({unhealthy:.1f}s) "
          f"-> healthy ({healthy:.1f}s)", flush=True)


def check_security(check):
    for stage, uid, status in (("00-root", 0, 200), ("01-non-root-broken", 10001, 500),
                               ("02-non-root-fixed", 10001, 200)):
        image = check.build(f"04-security/{stage}")
        _, url = check.serve(image)
        require(check.http(url + "/identity")["uid"] == uid, "Unexpected runtime UID")
        body = check.http(url + "/write", status=status, method="POST")
        if status == 500:
            require(body["error"] == "permission denied", "Unexpected write failure")
        else:
            require(body["status"] == "written", "Write did not succeed")
        print(f"[OK] 04-security/{stage}: uid {uid}, write {status}", flush=True)


def check_networking(check):
    for index, stage in enumerate(("00-broken-localhost", "01-service-dns")):
        path = ROOT / "05-networking" / stage
        env = {**os.environ, "API_PORT": "0", "CLIENT_PORT": "0"}
        compose = ["docker", "compose", "-p", f"{check.prefix}-net-{index}"]

        def run(*args, **kwargs):
            return check.command([*compose, *args], cwd=path, env=env, **kwargs)

        try:
            print(f"[BUILD] 05-networking/{stage}", flush=True)
            run("build", timeout=600)
            started = time.monotonic()
            run("up", "-d", "--wait", "--wait-timeout", "40")
            startup = time.monotonic() - started
            api = run("port", "api", "8000").stdout.strip()
            client = run("port", "client", "8000").stdout.strip()
            require(check.http(f"http://{api}/message")["message"] == "Hello from api", "API failed")
            status = 502 if index == 0 else 200
            body = check.http(f"http://{client}/proxy", status=status)
            if status == 200:
                require(body["upstream"]["message"] == "Hello from api", "Proxy response wrong")
            else:
                require(body["error"] == "upstream unavailable", "Unexpected proxy failure")
            for service in ("api", "client"):
                name = run("ps", "-q", service).stdout.strip()
                require(check.inspect(name)["State"]["Running"], f"{service} not running")
                run("logs", service)
            run("ps")
            run("exec", "-T", "client", "python", "-c",
                "import socket, urllib.request; print(socket.gethostbyname('api')); "
                "print(urllib.request.urlopen('http://api:8000/message').read().decode())")
            print(f"[OK] 05-networking/{stage}: API 200, proxy {status}, "
                  f"internal DNS/HTTP OK, startup {startup:.1f}s", flush=True)
        finally:
            run("down", "-v", "--remove-orphans", "--rmi", "local")


def check_bonus(check):
    info = json.loads(check.command(["docker", "info", "--format", "{{json .}}"]).stdout)
    if not info.get("MemoryLimit") or not info.get("SwapLimit"):
        print("[SKIP] 06-resources: daemon reports unsupported memory/swap limits", flush=True)
    else:
        image = check.build("06-resources")
        name = check.create(image, options=("--memory=64m", "--memory-swap=64m"))
        started = time.monotonic()
        check.command(["docker", "start", name])
        check.command(["docker", "stats", "--no-stream", name])
        check.command(["docker", "wait", name], timeout=60)
        state = check.inspect(name)["State"]
        require(state["OOMKilled"] and state["ExitCode"] == 137,
                f"Expected OOMKilled=true, ExitCode=137; got {state}")
        check.command(["docker", "logs", name])
        print(f"[OK] 06-resources: OOMKilled=true, ExitCode=137, "
              f"{time.monotonic() - started:.1f}s", flush=True)
    for kind in ("tag", "digest"):
        image = check.build("07-reproducibility", "-f", f"Dockerfile.{kind}", suffix=f"-{kind}")
        _, url = check.serve(image)
        check.http(url)
        print(f"[OK] 07-reproducibility/{kind}: HTTP 200", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-bonus", action="store_true")
    args = parser.parse_args()
    if not shutil.which("docker"):
        print("[FAIL] docker not found in PATH")
        return 1
    check = SmokeCheck()
    passed = False
    try:
        check.command(["docker", "version"], timeout=30)
        check.command(["docker", "info"], timeout=30)
        check.command(["docker", "compose", "version"], timeout=30)
        check_build(check)
        check_secrets(check)
        check_lifecycle(check)
        check_security(check)
        check_networking(check)
        if args.include_bonus:
            check_bonus(check)
        passed = True
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        print(f"[FAIL] {error}", flush=True)
    except KeyboardInterrupt:
        print("[FAIL] interrupted; cleaning up", flush=True)
    finally:
        cleaned = check.cleanup()
        print(f"Logs: {check.log_dir}", flush=True)
    if passed and cleaned:
        print("All required demos behave as expected.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
