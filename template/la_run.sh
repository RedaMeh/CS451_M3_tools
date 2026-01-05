#!/usr/bin/env bash
set -euo pipefail
set -m

# Run from inside template_java (or template_cpp) directory.
# It will:
#  1) build the project
#  2) start N processes (each with its own lattice-agreement-i.config)
#  3) keep them running until you Ctrl+C, then send SIGINT to all

# ---- Config (edit if your paths differ) ----
HOSTS_FILE="../example/hosts"
OUT_DIR="../example/output"
CONFIG_DIR="../example/configs"
CONFIG_PREFIX="lattice-agreement-"
CONFIG_SUFFIX=".config"

# Number of processes to start (default: count lines in HOSTS file)
N="${1:-}"

# ---- Sanity checks ----
if [[ ! -f "$HOSTS_FILE" ]]; then
  echo "HOSTS file not found: $HOSTS_FILE" >&2
  exit 1
fi

if [[ -z "${N}" ]]; then
  # Count processes from HOSTS file (first column per line)
  N="$(grep -c '^[[:space:]]*[0-9]\+' "$HOSTS_FILE" || true)"
fi

mkdir -p "$OUT_DIR"

echo "Building..."
./build.sh

pids=()

cleanup() {
  echo
  echo "Stopping processes..."

  # 1) Try graceful stop
  for pid in "${pids[@]:-}"; do
    kill -INT "$pid" 2>/dev/null || true
  done

  # 2) Wait up to 2s
  for _ in {1..20}; do
    alive=0
    for pid in "${pids[@]:-}"; do
      if kill -0 "$pid" 2>/dev/null; then alive=1; break; fi
    done
    [[ "$alive" -eq 0 ]] && break
    sleep 0.1
  done

  # 3) Escalate if needed
  for pid in "${pids[@]:-}"; do
    kill -TERM "$pid" 2>/dev/null || true
  done
  sleep 0.3
  for pid in "${pids[@]:-}"; do
    kill -KILL "$pid" 2>/dev/null || true
  done

  wait 2>/dev/null || true
  echo "Done."
}
trap cleanup INT TERM


echo "Starting $N processes..."
for id in $(seq 1 "$N"); do
  cfg="$CONFIG_DIR/${CONFIG_PREFIX}${id}${CONFIG_SUFFIX}"
  out="$OUT_DIR/${id}.output"

  if [[ ! -f "$cfg" ]]; then
    echo "Config file not found for id=$id: $cfg" >&2
    echo "Expected files like: $CONFIG_DIR/${CONFIG_PREFIX}1${CONFIG_SUFFIX}, ..., ${CONFIG_PREFIX}${N}${CONFIG_SUFFIX}" >&2
    exit 1
  fi

  echo "  -> id=$id"
  ./run.sh --id "$id" --hosts "$HOSTS_FILE" --output "$out" "$cfg" &
  pids+=("$!")
done

echo "All started. Ctrl+C to stop and flush logs."
wait
