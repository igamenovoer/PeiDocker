# LiteLLM + Claude Code Bridge (system)

This folder provides reusable building blocks so that **Claude Code** (Anthropic API)
can talk to a local OpenAI-compatible server (e.g. `llama.cpp/llama-server`) via **LiteLLM**.

It consists of:
- `install-litellm.sh`: installs `litellm[proxy]` (via `uv tool`).
- `proxy.py`: an HTTP proxy that:
  - returns `200 OK` for `POST /api/event_logging/batch` (Claude Code telemetry), and
  - forwards everything else to LiteLLM.

Projects can provide their own launcher under `installation/stage-2/custom/` while reusing
these system scripts.

## Proxy environment variables (`proxy.py`)

- `PORT` (default: `11899`)
- `LITELLM_URL` (default: `http://127.0.0.1:8000`)
- `UPSTREAM_TIMEOUT` (default: `120`)

## Usage (manual, inside container)

```bash
# Start LiteLLM (requires x-api-key)
litellm --host 0.0.0.0 --port 8000 --config /path/to/config.yaml &

# Start Claude telemetry proxy
PORT=11899 LITELLM_URL=http://127.0.0.1:8000 python3 proxy.py &
```

