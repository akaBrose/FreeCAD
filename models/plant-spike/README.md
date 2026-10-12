# Plant Spike

Hollow plant/watering spike: straight shaft, then a curved section that tapers to a blunt tip, with drain holes through the curved section. Units: mm.

**Rebuild:** `scripts/run.sh models/plant-spike/build.py` (from the repo root). Outputs `plant-spike.FCStd` (both print pieces), per-piece `.step`/`.stl`, and `plant-spike-assembled.step` (whole spike, reference).

## Key dimensions (parameters at top of `build.py`)

| Parameter | Value |
|---|---|
| Straight shaft length | 150 |
| Shaft OD (also the curve at its start) | 38 |
| OD at end of taper (point starts here) | 15 |
| Tip | 14° half-angle cone, 22 mm long, blending tangentially into a rounded blunt end Ø5 (`TIP_HALF_ANGLE_DEG`, `TIP_RADIUS`) |
| Wall thickness | 2 |
| Path | Tangent arc from (0,150) to (120, 424.95), R ≈ 375, sweep ≈ 47.2° (from the original `Plant Spike.FCStd` sketch) |
| Holes | 78 rounded-square holes (turned 45° so corners point along the path and around the spike), 13 staggered rings of 6. Side 9 at the start of the curve, scaled by local diameter (≈8.2 at the first ring, ≈4.0 at the last). Corner radius = 0.2 × side |

The shaft is open at the origin end. The cavity stops where the taper ends, so the point (cone and blunt end) is solid.

## Assumptions to confirm
- Taper is linear from 38 to 15 over the arc.
- Tip is a cone to a Ø5 rounded end (was a Ø15 dome).
- Holes go all the way round; `HOLE_ARC_DEG` limits them to one side.

## 3D printing: Bambu H2D, ABS, 0.6 mm nozzle

Too long for the bed in one piece (~432 mm; H2D plate 350 x 320 x 325), so it is two pieces joined by a lap joint. Both print **upright** on the bed, so no supports are needed. Files: `plant-spike.stl` (both pieces together, as laid out for printing), or individually `plant-spike-shaft.stl` (38 x 38 x 174) and `plant-spike-curve.stl` (66 x 38 x 320.6, printed tilted back 23.6 deg).

| Feature | Design |
|---|---|
| Split | Cut plane through the **start of the curve**, tilted 23.6 deg (`CUT_ANGLE_DEG` = half the 47.2 deg sweep). The curve piece sits with that plane on the bed leaning back, so its lean runs from -23.6 deg at the base to +23.6 deg at the tip (+2.1 deg taper): balanced, no overhang worse than ~26 deg |
| Joint | Spigot (shaft piece) / socket (curve piece) that follows the path from the cut plane to 23.3 mm along the arc: 15 mm minimum overlap, ~31 mm on the long side. ~0.9 mm wall each side, 0.2 mm radial bond gap. Bond with ABS/acetone slurry or epoxy. Checked in the build: 0 mm3 interference |
| Holes | Bottom row dropped to clear the joint: 13 staggered rings of 6 = 78 holes. With balanced lean the diamond edges average 45 deg from vertical (range ~21-69 deg). Min web > 3 mm, corner radius >= 0.8 mm |
| Wall | 2.0 mm = 3 perimeters at 0.66 mm line width |
| Cavity end | Flat ceiling is tilted when the curve piece stands up, so it prints without supports |

Suggested slicer settings (starting points, tune to your filament):
- 0.6 mm nozzle, 0.66 mm line width, 0.30 mm layers, 3 walls, 0-5% infill (it is all walls anyway), no supports.
- ABS: enclosed chamber, bed ~100 C, nozzle ~255-265 C, part fan off or <= 20%.
- A 2 mm wall ring gives very little bed contact for a 300 mm tall part: use a **brim of 10-15 mm** (or mouse ears) and keep the chamber closed until cooled to avoid warping.
- ABS shrinks ~0.7%: scale 100.7% if the joint fit matters, or print a short test ring first and adjust `JOINT_CLEAR`.
- The curve piece is 320.6 mm tall (limit 325), so only ~4 mm of Z headroom: no raft, no tall skirt. A longer tip would not fit.
