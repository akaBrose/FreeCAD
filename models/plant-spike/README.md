# Plant Spike

Hollow plant/watering spike: straight shaft, then a curved section that tapers to a blunt tip, with drain holes through the curved section. Units: mm.

**Rebuild:** `scripts/run.sh models/plant-spike/build.py` (from the repo root). Outputs `plant-spike.FCStd` (both print pieces), per-piece `.step`/`.stl`, and `plant-spike-assembled.step` (whole spike, reference).

## Key dimensions (parameters at top of `build.py`)

| Parameter | Value |
|---|---|
| Straight shaft length | 150 |
| Shaft OD (also the curve at its start) | 38 |
| OD at end of taper (dome starts here) | 15 |
| Wall thickness | 2 |
| Path | Tangent arc from (0,150) to (120, 424.95), R ≈ 375, sweep ≈ 47.2° (from the original `Plant Spike.FCStd` sketch) |
| Holes | 84 rounded-square holes (turned 45° so corners point along the path and around the spike), 14 staggered rings of 6. Side 9 at the start of the curve, scaled by local diameter (≈8.6 at the first ring, ≈4.0 at the last). Corner radius = 0.2 × side |

The shaft is open at the origin end. The cavity stops where the taper ends, so the dome tip is solid.

## Assumptions to confirm
- Taper is linear from 38 to 15 over the arc.
- Tip is a hemispherical dome of Ø15.
- Holes go all the way round; `HOLE_ARC_DEG` limits them to one side.

## 3D printing: Bambu H2D, ABS, 0.6 mm nozzle

Too long for the bed in one piece (~432 mm; H2D plate 350 x 320 x 325), so it is two pieces joined by a lap joint. Both print **upright** (open/seam end on the bed), so no supports are needed. Files: `plant-spike.stl` (both pieces together, as laid out for printing), or individually `plant-spike-shaft.stl` (38 x 38 x 150) and `plant-spike-curve.stl` (100 x 38 x 317, printed tilted back 10 deg).

| Feature | Design |
|---|---|
| Split | Cut plane tilted 10 deg (`CUT_ANGLE_DEG`) through the axis at y = 131.6, so the curve piece sits on the bed leaning back 10 deg. Tip lean drops from 47 deg to 37 deg (+2 deg taper). Shaft piece carries a spigot, curve piece a matching socket, both ending at y = 150 (15 mm minimum overlap, ~22 mm on the long side) |
| Why only 10 deg | Tilting makes the curve piece taller: 10 deg = 317 mm, 12 deg = 325 mm (the H2D limit). A full 23.6 deg (lean balanced +/-23.6) would be 333 mm and doesn't fit |
| Joint | ~0.9 mm wall each side, 0.2 mm radial bond gap (spigot r 17.9, socket r 18.1). Bond with ABS/acetone slurry or epoxy. Pieces checked in the build: 0 mm3 interference |
| Wall | 2.0 mm = 3 perimeters at 0.66 mm line width |
| Holes | Diamond edges are 45 deg from the path, so each hole's edges sit at 45 deg +/- the local lean; with the tilt, the lean now spans -10 to +37 deg instead of 0 to +47. Holes are small (4-8.5 mm sides), so even the steepest edges bridge. Min web > 3 mm, corner radius >= 0.8 mm |
| Cavity end | Flat ceiling is tilted ~47 deg when the curve piece stands up, so it prints without supports |

Suggested slicer settings (starting points, tune to your filament):
- 0.6 mm nozzle, 0.66 mm line width, 0.30 mm layers, 3 walls, 0-5% infill (it is all walls anyway), no supports.
- ABS: enclosed chamber, bed ~100 C, nozzle ~255-265 C, part fan off or <= 20%.
- A 2 mm wall ring gives very little bed contact for a 300 mm tall part: use a **brim of 10-15 mm** (or mouse ears) and keep the chamber closed until cooled to avoid warping.
- ABS shrinks ~0.7%: scale 100.7% if the joint fit matters, or print a short test ring first and adjust `JOINT_CLEAR`.
- With the tilted cut the curve piece leans at most ~39 deg from vertical (37 deg + taper) at the tip, inside the ~45 deg ABS limit, so no supports. The piece is 317 mm tall, so leave the plate clear and avoid a tall skirt.
