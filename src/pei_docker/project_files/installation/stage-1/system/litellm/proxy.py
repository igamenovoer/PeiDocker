import http.client
import http.server
import os
import sys
import urllib.parse

LITELLM_URL = os.environ.get("LITELLM_URL", "http://127.0.0.1:8000")
PORT = int(os.environ.get("PORT", "11899"))

UPSTREAM = urllib.parse.urlparse(LITELLM_URL)
UPSTREAM_SCHEME = UPSTREAM.scheme or "http"
UPSTREAM_HOST = UPSTREAM.hostname or "127.0.0.1"
UPSTREAM_PORT = UPSTREAM.port or (443 if UPSTREAM_SCHEME == "https" else 80)


class RequestHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _read_body(self) -> bytes:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            return b""
        return self.rfile.read(content_length)

    @staticmethod
    def _filter_hop_by_hop_headers(headers: list[tuple[str, str]]) -> list[tuple[str, str]]:
        hop_by_hop = {
            "connection",
            "proxy-connection",
            "keep-alive",
            "transfer-encoding",
            "te",
            "trailer",
            "upgrade",
            "content-length",
            "content-encoding",
        }
        return [(k, v) for (k, v) in headers if k.lower() not in hop_by_hop]

    def _forward_headers(self) -> dict[str, str]:
        hop_by_hop = {"host", "connection", "proxy-connection", "keep-alive", "transfer-encoding"}
        return {k: v for k, v in self.headers.items() if k.lower() not in hop_by_hop}

    def _make_conn(self) -> http.client.HTTPConnection:
        timeout_s = float(os.environ.get("UPSTREAM_TIMEOUT", "120"))
        if UPSTREAM_SCHEME == "https":
            return http.client.HTTPSConnection(UPSTREAM_HOST, UPSTREAM_PORT, timeout=timeout_s)
        return http.client.HTTPConnection(UPSTREAM_HOST, UPSTREAM_PORT, timeout=timeout_s)

    def _proxy(self) -> None:
        body = self._read_body()
        headers = self._forward_headers()

        headers["Host"] = f"{UPSTREAM_HOST}:{UPSTREAM_PORT}" if UPSTREAM_PORT else UPSTREAM_HOST

        conn = self._make_conn()
        try:
            conn.request(self.command, self.path, body=body if body else None, headers=headers)
            resp = conn.getresponse()

            self.send_response(resp.status, resp.reason)
            for k, v in self._filter_hop_by_hop_headers(resp.getheaders()):
                self.send_header(k, v)
            self.end_headers()

            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                self.wfile.write(chunk)
        finally:
            conn.close()
            self.close_connection = True

    def do_POST(self) -> None:
        if self.path == "/api/event_logging/batch":
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()
            self.close_connection = True
            return

        try:
            print(f"[proxy] {self.command} {self.path} -> LiteLLM", file=sys.stderr)
            self._proxy()
        except Exception as e:
            print(f"[proxy] Error: {e}", file=sys.stderr)
            self.send_error(500, str(e))

    def do_GET(self) -> None:
        try:
            self._proxy()
        except Exception as e:
            print(f"[proxy] Error: {e}", file=sys.stderr)
            self.send_error(500, str(e))


def main() -> None:
    http.server.HTTPServer.allow_reuse_address = True
    print(f"Proxy running on port {PORT} -> LiteLLM {LITELLM_URL}", file=sys.stderr)
    http.server.HTTPServer(("", PORT), RequestHandler).serve_forever()


if __name__ == "__main__":
    main()

