# Snowboard Base Protector (air travel) - v2

Thin, light, **rollable** protector for the base and edges of a snowboard: flexible hard-scale shell over a soft liner, removable hard **tip and tail caps**, and **straps** to hold the board to the protector. Units: mm. Board modelled flat at 156 cm, 300 / 250 / 300 mm.

**Rebuild:** `scripts/run.sh models/snowboard-base-protector/build.py` (repo root). Parameters are at the top of `build.py`; geometry is in `protector_lib.py` (identical copy in `ski-base-protector/`). Preview: `render_preview.py` (env `PREVIEW_NAME`, `PREVIEW_Y`, `PREVIEW_TIPX`).

Objects in `snowboard-base-protector.FCStd`: `Liner`, `Skin` (incl. strap tabs), `Scales`, `Tip_Cap_Shell`, `Tip_Cap_Liner`, `Tail_Cap_Shell`, `Tail_Cap_Liner`, `Straps` (webbing, reference only), `Gear_Reference` (the board, hidden). Per-part `.step`/`.stl`, `-assembled.step` (product parts, no straps) and `-preview.png` are exported.

## Rollable body = Liner + Skin + Scales
| Layer | Design |
|---|---|
| Scales (hard) | 727 pentagon plates 30 x 19.4 x 2.0 mm, tilted 7 deg, pitch 22 mm, staggered; neighbours nest with 0.68 mm clearance (checked by the build). One stud each into the skin. **Not** on the lip walls (soft lip only). |
| Skin (flexible TPU) | 1.0 mm, wraps the outside of the lip, carries the scales and the strap tabs |
| Liner (soft) | 3 mm floor, 2.5 mm lip wall 8 mm high covering the steel edge; 10 mm edge shelf with the base recessed 1 mm so the P-tex never touches; 1.5 mm floor grooves every 30 mm |

Total body thickness below the base plane: 9.5 mm (scale stack included). Estimated mass (assumed densities in `DENSITY`; liner as a ~20% TPU lattice): body ~1.4 kg, caps ~0.3 kg.

**Rolling:** roll along the length with the scales on the OUTSIDE and the gear side inside. The scales fan open when bent that way (build checks them down to a 10 mm radius with no collision). The lip has V-notches every 25 mm (8 mm wide at the top) so it compresses; they limit the inner roll to ~25 mm radius, giving a roll of about 120 mm diameter for the 1.32 m body.

## Tip and tail protectors
Separate caps (remove them before rolling). Each is a 2.5 mm hard shell cup with a 2 mm soft lining, open at the back so the board slides in. It reaches 120 mm back from the end, with a 60 mm roof over the nose/tail and low side walls. The body stops 1 mm short of each cap.

## Straps
Slotted tabs (soft skin tabs on the body, hard tabs on the caps) at 5 body stations (x = 0, +-260, +-520) and one on each cap roof. 25 mm webbing passes through the slot on each side and over the gear (modelled as `Straps`).

## Assumptions to confirm
- Flat reference (no camber / nose kick); GEAR_T = 11 mm. Strap tabs stick out 24 mm per side (body width incl. tabs 345 mm).
- Scale slits 0.6 mm; the shell relies on the skin and liner behind them.
- No buckles/cams modelled, only webbing; tabs are plain slots.
- Too long to print whole: print scales/caps in batches, mould or segment skin and liner.
