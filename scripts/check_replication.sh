#!/usr/bin/env bash
set -euo pipefail

primary_id="$(docker compose ps -q redis-primary)"
replica_id="$(docker compose ps -q redis-replica)"
if [[ -z "${primary_id}" || -z "${replica_id}" ]]; then
  echo "Redis lab is not running. Run: make up"
  exit 1
fi

echo "Primary replication info:"
docker exec -i "${primary_id}" bash -lc 'set -euo pipefail; export REDISCLI_AUTH="${REDIS_PASSWORD}"; redis-cli INFO replication | egrep "^(role|connected_slaves|master_replid|master_repl_offset):"'

echo
echo "Replica replication info:"
docker exec -i "${replica_id}" bash -lc 'set -euo pipefail; export REDISCLI_AUTH="${REDIS_PASSWORD}"; redis-cli INFO replication | egrep "^(role|master_host|master_link_status|master_last_io_seconds_ago|slave_repl_offset):"'
