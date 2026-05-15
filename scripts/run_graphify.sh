#!/usr/bin/env bash

set -euo pipefail

export PATH="$HOME/Library/Python/3.11/bin:$HOME/.local/bin:$PATH"

GRAPHIFY_BIN=$(command -v graphify 2>/dev/null || true)
if [ -n "${GRAPHIFY_BIN}" ]; then
    PYTHON=$(head -1 "${GRAPHIFY_BIN}" | tr -d '#!')
    case "${PYTHON}" in
        *[!a-zA-Z0-9/@_.-]*|"") PYTHON="python3" ;;
    esac
else
    PYTHON="python3"
fi

needs_install=0
if ! "${PYTHON}" - <<'PY'
from importlib.metadata import PackageNotFoundError, version

def parse(v: str) -> tuple[int, ...]:
    parts = []
    for raw in v.split("."):
        digits = "".join(ch for ch in raw if ch.isdigit())
        if digits:
            parts.append(int(digits))
        else:
            break
    return tuple(parts)

try:
    installed = version("graphifyy")
except PackageNotFoundError:
    raise SystemExit(1)

parsed = parse(installed)
if parsed < (0, 7, 13) or parsed >= (0, 8, 0):
    raise SystemExit(1)
PY
then
    needs_install=1
fi

if [ "${needs_install}" -eq 1 ]; then
    echo "[graphify] Installing compatible graphifyy>=0.7.13,<0.8.0" >&2
    "${PYTHON}" -m pip install --user "graphifyy>=0.7.13,<0.8.0" >/dev/null
fi

if [ "${1:-}" = "extract" ]; then
    has_backend_arg=0
    for arg in "$@"; do
        if [ "${arg}" = "--backend" ]; then
            has_backend_arg=1
            break
        fi
    done
    if [ "${has_backend_arg}" -eq 0 ] && \
       [ -z "${GOOGLE_API_KEY:-}" ] && \
       [ -z "${GEMINI_API_KEY:-}" ] && \
       [ -z "${ANTHROPIC_API_KEY:-}" ] && \
       [ -z "${OPENAI_API_KEY:-}" ] && \
       [ -z "${KIMI_API_KEY:-}" ] && \
       [ -z "${OLLAMA_HOST:-}" ]; then
        echo "[graphify] No backend configured. Set GRAPHIFY_BACKEND=gemini|claude|openai|ollama|kimi and provide the corresponding API key or local Ollama endpoint." >&2
        exit 2
    fi
fi

GRAPHIFY_BIN=$(command -v graphify 2>/dev/null || true)
if [ -z "${GRAPHIFY_BIN}" ]; then
    echo "[graphify] graphify CLI is not on PATH after installation." >&2
    exit 2
fi

exec graphify "$@"
