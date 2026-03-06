#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts/backups
ts="$(date -u +%Y%m%dT%H%M%SZ)"
out="artifacts/backups/redis-demo-${ts}.jsonl"

primary_id="$(docker compose ps -q redis-primary)"
if [[ -z "${primary_id}" ]]; then
  echo "redis-primary is not running. Run: make up"
  exit 1
fi

echo "Creating demo backup to ${out}..."

docker exec -i "${primary_id}" bash -lc 'set -euo pipefail; export REDISCLI_AUTH="${REDIS_PASSWORD}"; redis-cli --scan --pattern "demo:*" | while read -r k; do v="$(redis-cli --raw get "$k" || true)"; if [[ -n "$v" ]]; then printf "%s\t%s\n" "$k" "$v"; fi; done' \
  | python3 - <<'PY'\nimport json,sys\nfor line in sys.stdin:\n    line=line.rstrip(\"\\n\")\n    if not line:\n        continue\n    key, value = line.split(\"\\t\", 1)\n    print(json.dumps({\"key\": key, \"value\": value}, separators=(\",\",\":\")))\nPY\n+  > "${out}"

echo "Backup created: ${out}"
