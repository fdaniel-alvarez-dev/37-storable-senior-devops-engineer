from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    seed_path = Path("data/raw/demo_seed.jsonl")
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "redis_demo_snapshot.jsonl"

    if not seed_path.exists():
        raise SystemExit(f"Missing input fixture: {seed_path}")

    count = 0
    with seed_path.open("r", encoding="utf-8") as f, out_path.open("w", encoding="utf-8", newline="\n") as out:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{seed_path}:{idx}: invalid JSON") from exc

            key = str(obj.get("key", "")).strip()
            value = str(obj.get("value", "")).strip()
            if not key.startswith("demo:"):
                raise SystemExit(f"{seed_path}:{idx}: key must start with 'demo:' (got {key!r})")
            if value == "":
                raise SystemExit(f"{seed_path}:{idx}: value must be non-empty")

            out.write(json.dumps({"key": key, "value": value}, separators=(",", ":")) + "\n")
            count += 1

    print(f"Wrote {out_path} ({count} rows)")


if __name__ == "__main__":
    main()
