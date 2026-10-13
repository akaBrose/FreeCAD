# Plant Spike

Hollow plant/watering spike: straight shaft, then a curved section that tapers to a blunt tip, with drain holes through the curved section. Units: mm.

**Version:** v2 = v1 scaled to 70% (`SCALE = 0.70` in `build.py`; wall thickness, joint gap and joint overlap are not scaled). v1 (full size) is archived locally in `FreeCAD Project Files 2/Plant Spike/archive/v1-full-size/` and in git history (commit `43f16b0`). Set `SCALE = 1.0` to rebuild v1.

**Rebuild:** `scripts/run.sh models/plant-spike/build.py` (from the repo root). Outputs `plant-spike.FCStd` (both print pieces), per-piece `.step`/`.stl`, and `plant-spike-assembled.step` (whole spike, reference).

## Key dimensions (parameters at top of `build.py`)

| Parameter | Value |
|---|---|
| Straight shaft length | 105 (150 x 0.7) |
| Shaft OD (also the curve at its start) | 26.6 (38 x 0.7) |
| OD at end of taper (point starts here) | 10.5 (15 x 0.7) |
| Tip | One smooth revolved curve (cubic Bezier), 16.8 mm long, starting exactly tangent to the taper (no kink) and rounding into a blunt nose of ~1.75 mm radius (`TIP_LEN`, `TIP_NOSE_R`) |
| Wall thickness | 2 (unchanged from v1) |
| Path | Tangent arc from (0,105) to (84, 297.5), R ≈ 262.5, sweep ≈ 47.2° (same angle as v1) (from the original `Plant Spike.FCStd` sketch) |
| Holes | 78 rounded-square holes (turned 45° so corners point along the path and around the spike), 13 staggered rings of 6. Side 6.3 at the start of the curve, scaled by local diameter (≈5.7 at the first ring, ≈2.8 at the last). Corner radius = 0.2 × side |

The shaft is open at the origin end. The cavity stops where the taper ends, so the point (cone and blunt end) is solid.

## Assumptions to confirm
- Taper is linear from 26.6 to 10.5 over the arc.
- Tip is a smooth tangent curve to a ~Ø5 blunt nose (was a Ø15 dome, then a cone with a visible kink).
- Holes go all the way round; `HOLE_ARC_DEG` limits them to one side.

## 3D printing: Bambu H2D, ABS, 0.6 mm nozzle

At 70% the whole spike would just fit standing up in one piece (~303 mm tall) but the tip would lean 47 deg, so it is still two pieces joined by a lap joint (v1 was too long for the bed at ~432 mm; H2D plate 350 x 320 x 325). Both print **upright** on the bed, so no supports are needed. Files: `plant-spike.stl` (both pieces together, as laid out for printing), or individually `plant-spike-shaft.stl` (26.6 x 26.6 x 124) and `plant-spike-curve.stl` (46 x 26.6 x 225.5, printed tilted back 23.6 deg).

| Feature | Design |
|---|---|
| Split | Cut plane through the **start of the curve**, tilted 23.6 deg (`CUT_ANGLE_DEG` = half the 47.2 deg sweep). The curve piece sits with that plane on the bed leaning back, so its lean runs from -23.6 deg at the base to +23.6 deg at the tip (+2.1 deg taper): balanced, no overhang worse than ~26 deg |
| Joint | Spigot (shaft piece) / socket (curve piece) that follows the path from the cut plane to 17.8 mm along the arc: 12 mm minimum overlap, ~24 mm on the long side. ~0.9 mm wall each side, 0.2 mm radial bond gap. Bond with ABS/acetone slurry or epoxy. Checked in the build: 0 mm3 interference |
| Holes | Bottom row dropped to clear the joint: 13 staggered rings of 6 = 78 holes. With balanced lean the diamond edges average 45 deg from vertical (range ~21-69 deg). Min web ~2.3 mm at the last ring, corner radius 0.56 mm there (below the 0.6 mm nozzle, so it prints as a slightly sharper corner) |
| Wall | 2.0 mm = 3 perimeters at 0.66 mm line width |
| Cavity end | Flat ceiling is tilted when the curve piece stands up, so it prints without supports |

Suggested slicer settings (starting points, tune to your filament):
- 0.6 mm nozzle, 0.66 mm line width, 0.30 mm layers, 3 walls, 0-5% infill (it is all walls anyway), no supports.
- ABS: enclosed chamber, bed ~100 C, nozzle ~255-265 C, part fan off or <= 20%.
- A 2 mm wall ring gives very little bed contact for a 225 mm tall part: use a **brim of 10-15 mm** (or mouse ears) and keep the chamber closed until cooled to avoid warping.
- ABS shrinks ~0.7%: scale 100.7% if the joint fit matters, or print a short test ring first and adjust `JOINT_CLEAR`.
- The curve piece is 225.5 mm tall (limit 325), so there is plenty of Z headroom again.
