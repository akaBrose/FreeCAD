# Plant Spike

Hollow plant/watering spike: straight shaft, then a curved section that tapers to a blunt tip, with drain holes through the curved section. Units: mm.

**Rebuild:** `scripts/run.sh models/plant-spike/build.py` (from the repo root). Outputs `plant-spike.FCStd`, `.step`, `.stl` next to the script.

## Key dimensions (parameters at top of `build.py`)

| Parameter | Value |
|---|---|
| Straight shaft length | 150 |
| Shaft OD (also the curve at its start) | 38 |
| OD at end of taper (dome starts here) | 15 |
| Wall thickness | 2 |
| Path | Tangent arc from (0,150) to (120, 424.95), R ≈ 375, sweep ≈ 47.2° (from the original `Plant Spike.FCStd` sketch) |
| Holes | 72 × Ø2, 12 staggered rings of 6, spread around the curved section |

The shaft is open at the origin end. The cavity stops where the taper ends, so the dome tip is solid.

## Assumptions to confirm
- Taper is linear from 38 to 15 over the arc.
- Tip is a hemispherical dome of Ø15.
- Holes go all the way round; `HOLE_ARC_DEG` limits them to one side.
