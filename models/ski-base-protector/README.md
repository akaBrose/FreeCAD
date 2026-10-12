# Ski Pair Base Protector (air travel) - v2

Same thin, rollable scale-shell + liner system as the snowboard protector, sized for a pair of skis side by side, bases facing the same way, tips aligned, with removable tip/tail caps and straps over both skis. Units: mm. Skis modelled flat at 170 cm, 125 / 85 / 105 mm, centre-lines 133 mm apart.

**Rebuild:** `scripts/run.sh models/ski-base-protector/build.py` (repo root). Parameters at the top of `build.py`; geometry in `protector_lib.py` (identical copy in `snowboard-base-protector/`). Preview: `render_preview.py` (env `PREVIEW_NAME=ski-base-protector PREVIEW_Y=66.5 PREVIEW_TIPX=780`).

Objects, layers, rolling, caps and straps work as described in the snowboard README. Differences:
- Liner has two pockets joined by a divider rib (6 mm at the widest point, ~45 mm at the waist) so the two skis never touch; the rib is cut by the same V-notches as the lip so it rolls. 8 mm lip, 8 mm edge shelf, GEAR_T = 12 mm.
- 706 scales; caps are 100 mm long, each one covers both ski ends (floor bridge between the cups at the tail); straps at x = 0, +-300, +-600 pass over both skis.
- Estimated mass: body ~1.5 kg, caps ~0.3 kg. Rolled body (1.5 m) about 130 mm diameter.

Assumptions and limits are as in the snowboard README (flat skis, 0.6 mm scale slits, webbing only, parts too long to print whole).
