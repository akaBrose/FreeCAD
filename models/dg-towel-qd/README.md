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

---

# v3 - velcro base + angled magnetic peg for a 1" steel grommet (restart; v1/v2 kept)

**Rebuild:** `scripts/run.sh models/dg-towel-qd/build_v3.py` -> `dg-towel-qd-v3.FCStd` (base + reference grommet + magnets), `dg-towel-qd-v3-base.{stl,step}`. Model orientation = print orientation: back face on the bed, +Z outward, +Y up on the bag.

- **Base**: 70 x 75 x 4 plate, R6 corners. Back has a 64 x 69 x 1.2 recess (3 mm rim) for a self-adhesive velcro pad; the rim also protects the pad edges from peeling.
- **Peg**: Ø18 x 17 stem on a Ø42 seat pedestal, tilted 35 deg from the plate normal toward UP, so it points up and outward on the bag. Gravity slides the grommet down onto the seat; release = lift the grommet up and out along the peg. Plain stem (no head) so it prints without supports; a 0.8 mm bead gives a click.
- **Magnets**: 4 x Ø5 x 3 N52 on a r = 16 circle, in open pockets (Ø5.1 x 3.2) in the seat face. Press-fit/glue, magnet recessed 0.2 mm. Same polarity facing out. Magnets touch the grommet (no plastic skin), so seal with a drop of epoxy over the face if rust is a concern.
- Total height off the bag 32 mm at the low side of the seat.

## To confirm / tune
- Measure the grommet: model assumes 25.4 ID, 38 OD, 2.5 thick (magnet circle r=16 should sit on metal, between r=12.7 and the OD edge).
- Hold vs. release: add/remove magnets (`MAG_N`) or change `ANGLE` (more tilt = more gravity seating).
- Velcro recess depth (`VEL_DEPTH`) vs. your velcro pad thickness.
- Peel: releasing out-and-up peels the velcro; if the base lifts, increase plate size or lower the magnet count.

---

# v4 - velcro base with a funnel-ramp catcher (swing-in / pull-out, no aiming)

**Rebuild:** `scripts/run.sh models/dg-towel-qd/build_v4.py` -> `dg-towel-qd-v4.FCStd` (base + reference grommet + magnets), `dg-towel-qd-v4-base.{stl,step}`. Model orientation = print orientation: back face on the bed, +Z outward, +Y up on the bag.

How it works (towel has a 1" steel grommet in the corner with a lanyard through it):
- **Stow**: swing the grommet at the base. The mouth is 72 mm wide with 5 mm flared walls, so it lands anywhere on the ramp. The ramp (seat tilted 25 deg from the plate, facing up/out) lets the ring slide down under gravity; the magnets pull it flat; the U-shaped bottom (R22, 3 mm slack around a Ø38 grommet) centres it; a short bullet peg (Ø11 base, Ø5.6 tip, 16 long) drops into the hole as it settles so it cannot ride sideways out.
- **Grab**: pull the lanyard up and outward. The ring lifts off the magnets, clears the peg tip, and rides up the flared walls and out. The lanyard runs out through a 12 mm notch in the bottom wall.
- **Base**: 100 x 100 x 4 plate, R8 corners, 1.2 mm velcro recess on the back with a 4 mm rim. Catcher block is 41 mm proud of the bag at its tallest (bottom wall), ~9 mm at the top of the ramp.
- **Magnets**: 4 x Ø6 x 3 N52 on r=15.5 in open pockets in the seat (Ø6.1 x 3.2, 0.2 recessed). Press-fit + glue, same pole out.

## To confirm / tune
- Grommet OD/thickness (assumed 38 / 2.5): `RU` should be OD/2 + ~3; magnet circle `MAG_R` must land on metal.
- Peg: if the ring hangs on the tip during release, shorten `PEG_LEN` or lower `ANGLE`.
- Hold vs release: `MAG_N`, `ANGLE`.
- Lanyard notch `NOTCH_W` vs. your cord thickness.
- The 100 mm plate is large; shrink `MARGIN` / `W_TOP` if it crowds the bag.

---

# v5 - flat 45 x 65 x 3 velcro plate with a short curved horn

**Rebuild:** `scripts/run.sh models/dg-towel-qd/build_v5.py` -> `dg-towel-qd-v5.FCStd` (base + reference grommet + magnets), `dg-towel-qd-v5-base.{stl,step}`. Model orientation = print orientation: flat back on the bed, +Z outward, +Y up on the bag.

- **Plate**: 45 x 65 x 3, R4 corners, plain flat back for adhesive velcro (no recess: the plate is too thin for one plus the magnet pockets).
- **Horn**: round section lofted along a circular arc. Ø23 where it meets the plate (sits inside the 25.4 grommet hole), tapering to a Ø7 blunt rounded tip over 22 mm of arc. It leaves the plate at 20 deg from the plate normal (tilted up) and curves a further 40 deg, so the tip points 60 deg from the normal = 30 deg above the bag surface, up and out. Tip is 23 mm off the bag, 40 mm up the plate. An 8 mm straight extension behind the plate front buries the foot; the back is clipped flat.
- **Ring**: hangs around the horn base, flat on the plate face, centred 26 mm up (a Ø38 grommet spans y 7..45 on the 65 plate, 3.5 mm side margins).
- **Magnets**: 4 x Ø6 x 2 N52 on r=15.8 around the horn, open pockets Ø6.1 x 2.2 in the plate front (0.8 mm floor), press-fit + glue, same pole out.
- **Printing**: no supports needed; the worst underside overhang (tip region) is about 40 deg from vertical. PETG, 4+ walls.

## To confirm / tune
- Grommet OD/thickness (assumed 38 / 2.5): `MAG_R` must land on metal between r=12.7 and the OD.
- Base fit: tilted Ø23 presents a ~24.5 mm footprint through the 25.4 hole. If it binds, drop `R_BASE`; if it rattles, raise it.
- Horn angle/curve (`PHI0`, `SWEEP`, `L`): more sweep = more hook (harder to shake off, needs a more upward pull); longer `L` = more keeper, more protrusion.
- Hold: `MAG_N`, or Ø8 magnets if the grommet outer rim is wide enough.
