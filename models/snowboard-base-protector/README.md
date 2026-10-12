# Snowboard Base Protector (air travel)

Flexible hard-scale shell + soft liner that covers the base and wraps the edges of a snowboard. Units: mm. Board modelled flat (no camber / nose kick) at 156 cm, 300 / 250 / 300 mm.

**Rebuild:** `scripts/run.sh models/snowboard-base-protector/build.py` (repo root). Parameters are at the top of `build.py`; the shared geometry code is `protector_lib.py` (identical copy in `ski-base-protector/`). Preview: `render_preview.py` (freecadcmd, env `PREVIEW_NAME`, `PREVIEW_Y`).

Outputs: `snowboard-base-protector.FCStd` (Liner, Skin, Scales visible; Gear_Reference hidden), per-part `.step`/`.stl`, `-assembled.step`, `-preview.png`.

## How it works (layers, outside to inside)
| Layer | Design |
|---|---|
| **Scales** (hard) | 704 pentagon plates, 34 x 21.4 x 2.5 mm, chamfered outer edge, in a staggered (hex-packed) pattern, tips toward the tail. Each is tilted 8 deg so the trailing end stands off the skin and the next scale nests under it: pitch 24 mm gives 10 mm overlap, 0.84 mm clearance between neighbours (checked in the build). One 4.4 mm stud per scale rivets/over-moulds into the skin. Scales slide over each other, so the shell bends with the board. |
| **Skin** (flexible TPU/TPE) | 1.5 mm backing under the liner that also wraps up the outside of the lip wall; carries the scales. |
| **Liner** (soft, shock absorbing) | 6 mm floor + 4 mm lip wall 12 mm high (covers steel edge and sidewall). 1 mm clearance pocket. 12 mm edge shelf: the steel edges rest on it while the P-tex base sits 1.5 mm above the recessed centre, so the base never touches anything. Transverse 3 x 3 mm relief grooves every 40 mm (sealed by the skin = air cushions, and easier bending). |

## Assumptions / limits to confirm
- Scale slits: neighbouring scales have a 0.6 mm gap; the skin and liner sit behind it. The outer scale row is not thicker and the lip wall is covered by skin only, not hard scales.
- Flat reference; the real board's camber/kick will be followed by the flexible shell, but the pocket is not cambered.
- No closures yet (straps, buckles, end caps, handle).
- Too long to print as one piece: print the 704 scales in batches, and mould or segment the liner and skin.
