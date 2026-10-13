# DG Towel Quick-Detach (v1)

One-handed, shear-locked, magnet-assisted slide latch for hanging a wet disc golf towel on a backpack/bag. Units: mm.

**Rebuild:** `scripts/run.sh models/dg-towel-qd/build.py`. Outputs `dg-towel-qd.FCStd` (receiver, tongue seated, two reference magnets), per-part `.step`/`.stl` (tongue STL is in print orientation).

## How it works
- **Receiver (bag side)**, 38 x 24 x 36: dovetail channel open at the top and front. Cross slot (3.5 x 22, through X) takes a velcro strap or a carabiner clipped over the 3 mm back bar. Drain slot through the side walls at floor level.
- **Tongue (towel side)**: dovetail shaft (30 long) + head plate with a 22 x 4 strap slot for webbing/paracord/towel loop.
- The **dovetail** (16 front / 24 back, 12 deep, 0.25 mm slide clearance per side) carries swing and snag loads; it only lets the tongue leave straight up. The **magnet pair** (Ø10 x 5 N52, one per part) seats the tongue and resists lift-out. Release: pull the towel up with one hand.

## Magnets
- 1.0 mm total gap between magnets (0.4 skin each + 0.2 end gap). Pockets Ø10.2 x 5.2 are **sealed voids**: pause the print when the void is exposed, drop the magnet in, resume.
  - Receiver (prints upright): pause just below z = 6.6 mm (void spans z 1.4-6.6).
  - Tongue (print end-face down, STL already oriented): pause just below z = 5.6 mm (void spans z 0.4-5.6).
- **Mark polarity** so they attract before sealing (stick the two magnets together and mark the faces).

## To confirm / tune after test print
- Magnet pull vs. strength needed (add a second pair or go thicker if it lifts out under snags).
- Slide clearance (0.25/side) and whether the fit binds when wet or gritty.
- Strap slot size for your towel loop; webbing slot for your bag's velcro strap width.
- Material: PETG (or nylon), 4-6 walls; dovetail layers lie in-plane so side loads run along the layers.
