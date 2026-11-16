# makefun-too-big-cup-4

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/acengrahmi/makefun-too-big-cup-4/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/acengrahmi/makefun-too-big-cup-4/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

make.fun bounty entry: make the AI judge excited. A golden koi leaps from a steaming teacup toward the full moon — "TOO BIG FOR THE CUP. SHE JUMPED ANYWAY." One bold diagonal of motion across an indigo night sky: cratered moon with halo, porcelain teacup with red-and-gold band, steam, splashes, gold speed lines, and a moonlit pool on a wooden table.

The image is drawn entirely in code by `main.py` (Python 3 standard library only — custom 2× supersampled rasterizer, scanline polygon fill, hand-built 5×7 bitmap font; no dependencies, no photos, no stock art). Output is deterministic: repeated runs produce a byte-identical `entry.png` (1024×1024, 87,748 bytes). See `REPORT.md` for design notes, validation numbers, and the iteration log.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` — 1024×1024 PNG, deterministic (byte-identical on re-runs). Pure Python 3 standard library, no dependencies.

## Files

- `main.py` — the whole picture: custom 2× supersampled rasterizer, sky, moon, teacup, koi, caption (hand-built 5×7 bitmap font).
- `entry.png` — generated output.
- `REPORT.md` — design notes, validation numbers, iteration log.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards</sub>
