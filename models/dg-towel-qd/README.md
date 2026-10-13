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

---

# v2 - funnel holster + grab paddle (replaces the v1 dovetail; v1 files kept)

**Rebuild:** `scripts/run.sh models/dg-towel-qd/build_v2.py` -> `dg-towel-qd-v2.FCStd`, `dg-towel-qd-v2-{receiver,tongue}.{stl,step}` (tongue STL in print orientation).

Why: v1 needed aiming into a narrow dovetail mouth and had a small, awkward handle. v2 is easier to stow one-handed and releases in exactly one direction (up).

- **Receiver** 44 x 28 x 40: 28.6 x 10.6 pocket (0.3 mm clearance/side), 34 deep, closed on all four sides, with a 45-degree funnel mouth (38.6 x 20.6 at the top) so the paddle drops in without aiming. Cross slot 3.5 x 25 (through X) for velcro strap / carabiner; drain slot through the front wall at floor level.
- **Tongue**: 28 x 10 paddle (34 long, chamfered tip) + 36 x 14 x 24 grab head with finger scallops on both faces, 45-degree under-head taper (prints without supports), and a 22 x 4 strap slot near the top.
- **Magnets**: 2 pairs of Ø8 x 4 N52 (x = +/-6), 1.0 mm total gap. Sealed voids, pause-print insert, mark polarity.
  - Receiver upright: pause just below z = 5.6 (void z 1.4-5.6).
  - Tongue (end face down): pause just below z = 4.6 (void z 0.4-4.6).
- Head clears the receiver top by 1.2 mm when seated. Print PETG/nylon, 4-6 walls.
