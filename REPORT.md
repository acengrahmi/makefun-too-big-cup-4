# REPORT — ai-excited-01 (rebuild round 4, v4)

**Bounty:** make.fun `ai-excited-01` — "Make the AI judge excited" ($250, top 20 paid, 1st $50)
**Deadline:** 17 Nov 2026 06:00 WIB
**Entry:** `main.py` (Python 3 stdlib only, no external dependencies) → `entry.png`

## Design

A golden koi leaps from a steaming porcelain teacup toward a big glowing
moon — a single bold diagonal of motion across a deep indigo night sky.
Caption, top-left, in a hand-built 5×7 bitmap font:

> **TOO BIG FOR THE CUP. SHE JUMPED ANYWAY.**

Why it should excite an AI judge: surprise (a fish in a teacup, jumping at
the moon), momentum (the fish's arc, three gold speed lines, water droplets
trailing behind it), warm-vs-cool contrast (gold/orange koi + moon against
deep blue dusk), and craft (cratered moon with halo, patterned cup with
gold rim and red band, steam curls, splash crown, moonlight pool on the
wooden table, 150 seeded stars + sparkles).

## How it is drawn (all from scratch in this session)

- Custom supersampled rasterizer (2×) with scanline polygon fill, circles,
  ellipses and alpha blending — no image libraries, no copied assets.
- Sky: 5-stop dusk gradient; moon: radial halo + disc + 6 craters + rim light.
- Koi: quadratic Bézier spine, tapered body outline (dark rim, gold body,
  warm back stripe, cream belly, white patches, black spots, red head patch),
  3 swept dorsal fins, pectoral fin, forked tail fin, eye + whiskers.
- Teacup: saucer, tapered body, red/gold diamond band, tea surface, handle,
  two steam curls; splash crown + hero droplets where the koi left the cup.
- Caption: bitmap font rendered at scale 6 with dark outline and a soft
  per-line dark panel for legibility over the stars.

## Validation

| Check | Result |
|---|---|
| `MAKEFUN_OUTPUT_DIR=out python3 main.py` | `out/entry.png` created, ~4 s |
| Dimensions | 1024 × 1024 (verified from PNG IHDR) |
| File size | **87,748 bytes** (limit 1 MiB = 1,048,576) ✓ |
| Determinism | 3 consecutive runs → identical sha256 |
| sha256 | `5f2ddb94f35b4f326a40a95fb49a8ad3075e77ed05ddd1332c301bbd376f8f71` |
| Visual check | Image viewed directly, iterated twice (see below) |

## Iterations (visual review, this session)

1. **v1 → v2:** caption overlapped the moon; back-stripe and belly polygons
   zigzagged (alternating outer/inner points); tail fin read as two flat
   wooden planks over the cup; motion streaks were dotted; steam too grey.
   Fixed: moon moved right/down, text scale 7→6, stripe/belly rebuilt as
   proper outer+inner outlines, tail redrawn as curved forked lobes along
   the arc tangent, streaks drawn from a 200-point Bézier, steam softened.
2. **v2 → v3 (final):** dorsal fins sat on the wrong (belly) side; the
   caption's dark panel clipped a grey notch out of the moon's edge; tail
   lobes still too wide. Fixed: fins flipped to the sky-facing side,
   per-line caption panels (panel now ends before the moon), tail lobes
   narrowed and tapered. Final image re-viewed: clean diagonal composition,
   readable caption, moon intact, koi clearly leaping cup → moon.

## Reproduce

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — byte-identical on every run
```
