# Backup & restore drill

Goal: make recovery predictable by practicing it.

## Drill steps
```bash
make up
make seed
make backup
make restore
```

## What “good” looks like
- You can restore without guessing commands.
- The backup artifact is versioned *out of band* (`artifacts/` is ignored).
- The process is documented and repeatable.

## Notes

- The included `make backup` / `make restore` flow is a **demo-key drill** (keys matching `demo:*`) to keep the lab deterministic.
- In production, prefer RDB/AOF backups plus periodic restore verification, and keep credentials out of the repository.
