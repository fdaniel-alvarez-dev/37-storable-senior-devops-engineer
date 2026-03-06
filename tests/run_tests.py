#!/usr/bin/env python3
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        env=os.environ.copy(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def fail(message: str, *, output: str | None = None, code: int = 1) -> None:
    print(f"FAIL: {message}")
    if output:
        print(output.rstrip())
    raise SystemExit(code)


def require_file(path: Path, description: str) -> None:
    if not path.exists():
        fail(f"Missing {description}: {path}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path}", output=str(exc))
    return {}


def demo_mode() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    report_path = ARTIFACTS_DIR / "redis_guardrails.json"
    guard = run([sys.executable, "tools/redis_guardrails.py", "--format", "json", "--out", str(report_path)])
    if guard.returncode != 0:
        fail("Redis guardrails failed (demo mode must be offline).", output=guard.stdout)

    report = load_json(report_path)
    if report.get("summary", {}).get("errors", 0) != 0:
        fail("Redis guardrails reported errors.", output=json.dumps(report.get("findings", []), indent=2))

    demo = run([sys.executable, "pipelines/pipeline_demo.py"])
    if demo.returncode != 0:
        fail("Offline demo pipeline failed.", output=demo.stdout)

    out_path = REPO_ROOT / "data" / "processed" / "redis_demo_snapshot.jsonl"
    require_file(out_path, "offline demo output")
    if out_path.stat().st_size == 0:
        fail("Offline demo output is empty.", output=str(out_path))

    for required in ["NOTICE.md", "COMMERCIAL_LICENSE.md", "GOVERNANCE.md"]:
        require_file(REPO_ROOT / required, required)

    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8", errors="replace")
    if "it.freddy.alvarez@gmail.com" not in license_text:
        fail("LICENSE must include the commercial licensing contact email.")

    print("OK: demo-mode tests passed (offline).")


def _send_resp(sock: socket.socket, payload: bytes) -> bytes:
    sock.sendall(payload)
    sock.settimeout(5)
    return sock.recv(4096)


def redis_ping(host: str, port: int, password: str | None) -> None:
    with socket.create_connection((host, port), timeout=5) as sock:
        if password:
            auth = f"*2\r\n$4\r\nAUTH\r\n${len(password)}\r\n{password}\r\n".encode("utf-8")
            resp = _send_resp(sock, auth)
            if not resp.startswith(b"+OK"):
                raise RuntimeError(f"AUTH failed: {resp!r}")
        resp = _send_resp(sock, b"*1\r\n$4\r\nPING\r\n")
        if not resp.startswith(b"+PONG"):
            raise RuntimeError(f"PING failed: {resp!r}")


def production_mode() -> None:
    if os.environ.get("PRODUCTION_TESTS_CONFIRM") != "1":
        fail(
            "Production-mode tests require an explicit opt-in.",
            output=(
                "Set `PRODUCTION_TESTS_CONFIRM=1` and rerun:\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
            ),
            code=2,
        )

    ran_external_integration = False

    url = os.environ.get("REDIS_TEST_URL", "").strip()
    host = os.environ.get("REDIS_TEST_HOST", "").strip()
    port_raw = os.environ.get("REDIS_TEST_PORT", "").strip()
    password = os.environ.get("REDIS_TEST_PASSWORD", "").strip() or None

    if url:
        parsed = urlparse(url)
        if parsed.scheme not in {"redis", "rediss"}:
            fail("REDIS_TEST_URL must be a redis:// or rediss:// URL.", code=2)
        host = parsed.hostname or ""
        port = parsed.port or 6379
        password = parsed.password or password
    else:
        port = int(port_raw) if port_raw else 6379

    if host:
        try:
            redis_ping(host, port, password)
        except Exception as exc:
            fail(
                "Redis PING integration failed.",
                output=(
                    "Verify connectivity and credentials.\n"
                    "Tip: set REDIS_TEST_URL=redis://:password@host:6379 (or set host/port/password vars).\n\n"
                    f"{type(exc).__name__}: {exc}\n"
                ),
            )
        ran_external_integration = True

    if os.environ.get("TERRAFORM_VALIDATE") == "1":
        tf = shutil.which("terraform")
        if tf is None:
            fail(
                "TERRAFORM_VALIDATE=1 requires terraform.",
                output="Install Terraform and rerun production mode, or unset TERRAFORM_VALIDATE.",
                code=2,
            )
        ran_external_integration = True
        example_dir = REPO_ROOT / "infra" / "examples" / "dev"
        init = run([tf, "init", "-backend=false"], cwd=example_dir)
        if init.returncode != 0:
            fail("terraform init failed.", output=init.stdout, code=2)
        validate = run([tf, "validate"], cwd=example_dir)
        if validate.returncode != 0:
            fail("terraform validate failed.", output=validate.stdout)

    if not ran_external_integration:
        fail(
            "No external integration checks were executed in production mode.",
            output=(
                "Enable at least one real integration:\n"
                "- Set `REDIS_TEST_URL` (or `REDIS_TEST_HOST`/`REDIS_TEST_PORT`) to run a real Redis PING, and/or\n"
                "- Set `TERRAFORM_VALIDATE=1` to run Terraform validate.\n\n"
                "Then rerun:\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
            ),
            code=2,
        )

    print("OK: production-mode tests passed (integrations executed).")


def main() -> None:
    mode = os.environ.get("TEST_MODE", "demo").strip().lower()
    if mode not in {"demo", "production"}:
        fail("Invalid TEST_MODE. Expected 'demo' or 'production'.", code=2)

    if mode == "demo":
        demo_mode()
        return

    production_mode()


if __name__ == "__main__":
    main()
