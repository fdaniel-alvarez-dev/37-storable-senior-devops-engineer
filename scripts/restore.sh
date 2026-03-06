#!/usr/bin/env bash
set -euo pipefail

latest="$(ls -1 artifacts/backups/redis-demo-*.jsonl 2>/dev/null | tail -n 1 || true)"
if [[ -z "${latest}" ]]; then
  echo "No demo backups found under artifacts/backups/. Run: make backup"
  exit 1
fi

primary_id="$(docker compose ps -q redis-primary)"
if [[ -z "${primary_id}" ]]; then
  echo "redis-primary is not running. Run: make up"
  exit 1
fi

echo "Restoring latest demo backup: ${latest}"
docker exec -i "${primary_id}" bash -lc 'set -euo pipefail; export REDISCLI_AUTH="${REDIS_PASSWORD}"; redis-cli --scan --pattern "demo:*" | xargs -r -n 50 redis-cli del >/dev/null'

python3 - <<'PY' "${latest}" | docker exec -i "${primary_id}" bash -lc 'set -euo pipefail; export REDISCLI_AUTH="${REDIS_PASSWORD}"; redis-cli --pipe'\nimport json,sys\npath=sys.argv[1]\nwith open(path,'r',encoding='utf-8') as f:\n    for line in f:\n        line=line.strip()\n        if not line:\n            continue\n        obj=json.loads(line)\n        k=obj['key']\n        v=obj['value']\n        sys.stdout.write(f\"*3\\r\\n$3\\r\\nSET\\r\\n${len(k)}\\r\\n{k}\\r\\n${len(v)}\\r\\n{v}\\r\\n\")\nPY

echo "Restore complete (demo keys)."
