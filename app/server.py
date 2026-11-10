#!/usr/bin/env python3
"""Servidor HTTP pequeno y sin dependencias para el portal del laboratorio."""

from __future__ import annotations

import json
import os
import socket
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

APP_VERSION = "week-1"
MAX_WORK_MS = 2_000


def clamp_work_ms(raw_value: str | None) -> int:
    """Convierte el retardo solicitado a un rango seguro."""
    if raw_value is None:
        return 0
    try:
        value = int(raw_value)
    except ValueError:
        return 0
    return max(0, min(value, MAX_WORK_MS))


def response_payload(path: str, work_ms: int = 0) -> dict[str, object]:
    """Construye la respuesta observable que identifica a cada replica."""
    return {
        "service": "ucab-enrollment-portal",
        "version": APP_VERSION,
        "instance": socket.gethostname(),
        "path": path,
        "work_ms": work_ms,
        "request_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
    }


class PortalHandler(BaseHTTPRequestHandler):
    server_version = "UcabPortal/1.0"

    def _write_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Request-Id", str(payload.get("request_id", "")))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - API de BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._write_json(HTTPStatus.OK, {"status": "healthy"})
            return

        if parsed.path not in {"/", "/work"}:
            self._write_json(
                HTTPStatus.NOT_FOUND,
                {"error": "not_found", "request_id": str(uuid.uuid4())},
            )
            return

        values = parse_qs(parsed.query)
        work_ms = clamp_work_ms(values.get("ms", [None])[0])
        if parsed.path == "/work" and work_ms:
            time.sleep(work_ms / 1_000)
        self._write_json(HTTPStatus.OK, response_payload(parsed.path, work_ms))

    def log_message(self, message_format: str, *args: object) -> None:
        event = {
            "event": "http_access",
            "client": self.client_address[0],
            "message": message_format % args,
            "timestamp": int(time.time()),
        }
        print(json.dumps(event, separators=(",", ":")), flush=True)


def create_server(host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), PortalHandler)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = create_server(port=port)
    print(f"portal listo en el puerto {port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

