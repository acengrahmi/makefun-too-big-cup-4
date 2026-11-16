# ai-excited-01 — "Too big for the cup. She jumped anyway."

make.fun bounty entry: make the AI judge excited. A golden koi leaps from
a steaming teacup toward the moon.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` — 1024×1024 PNG, deterministic (byte-identical on
re-runs). Pure Python 3 standard library, no dependencies.

## Files

- `main.py` — the whole picture: custom 2× supersampled rasterizer, sky,
  moon, teacup, koi, caption (hand-built 5×7 bitmap font).
- `entry.png` — generated output.
- `REPORT.md` — design notes, validation numbers, iteration log.
