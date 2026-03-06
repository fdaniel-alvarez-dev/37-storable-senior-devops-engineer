#!/usr/bin/env bash
set -euo pipefail

primary_id="$(docker compose ps -q redis-primary)"
if [[ -z "${primary_id}" ]]; then
  echo "redis-primary is not running. Run: make up"
  exit 1
fi

echo "Seeding demo keys into redis-primary..."
docker exec -i "${primary_id}" bash -lc 'set -euo pipefail; export REDISCLI_AUTH="${REDIS_PASSWORD}"; redis-cli set demo:user:1 "alice" >/dev/null; redis-cli set demo:user:2 "bob" >/dev/null; redis-cli set demo:order:1001 "paid" >/dev/null'
echo "Seed complete."
