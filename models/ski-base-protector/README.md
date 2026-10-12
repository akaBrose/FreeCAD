# Ski Pair Base Protector (air travel)

Same scale-shell + liner system as the snowboard protector, sized for a pair of skis side by side, bases facing the same way, tips aligned. Units: mm. Skis modelled flat at 170 cm, 125 / 85 / 105 mm (tip / waist / tail), centre-lines 133 mm apart.

**Rebuild:** `scripts/run.sh models/ski-base-protector/build.py` (repo root). Parameters at the top of `build.py`; geometry code in `protector_lib.py` (identical copy in `snowboard-base-protector/`). Preview: `render_preview.py` (env `PREVIEW_NAME=ski-base-protector PREVIEW_Y=66.5`).

Outputs: `ski-base-protector.FCStd` (Liner, Skin, Scales visible; Gear_Reference hidden), per-part `.step`/`.stl`, `-assembled.step`, `-preview.png`.

## Differences from the snowboard version
- Liner has two pockets joined by a divider rib (6 mm at the widest point, about 45 mm at the waist) so the two skis' edges and bases never touch each other; the rib is as tall as the lip (14 mm). The outline follows the skis' sidecut; the tail end has an open slot between the pockets.
- Lip 14 mm, edge shelf 10 mm; 647 scales cover the whole shell including over the divider.

Layers, scale geometry and limits are as in the snowboard README (scale slits 0.6 mm, flat reference, no closures, parts too long for one print).
