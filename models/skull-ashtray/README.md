# Skull Ashtray (concept A, "open skull")

Ashtray shaped like a human skull seen face-on: from above you look straight into the skull's face. A single bowl follows the outline inside an even 8 mm rim. The face (eye sockets, nasal opening, teeth) is a black inlay set flush into the bowl floor, and the body is white. Five U-notches in the rim hold a cigar, two cigarettes and two joints, with the lit end over the bowl. Units: mm.

**Rebuild:** `scripts/run.sh models/skull-ashtray/build.py`, then `scripts/run.sh models/skull-ashtray/render_preview.py` (both from the repo root).

## Key dimensions (parameters at top of `build.py`)

| Item | Value |
|---|---|
| Footprint | 100.0 x 150.1 mm (3.94 x 5.91 in), limit 4 x 6 in |
| Height | 38.0 mm (1.496 in), limit 1.5 in |
| Rim | 8.0 mm wide at the top, the same all the way round (2D offset of the outline). Grows to ~9.6 mm at the floor because of the draft |
| Cavity depth | 30.0 mm (1.18 in) from rim top to floor (spec 1.00-1.25 in) |
| Floor | 8 mm solid, which adds weight so it doesn't tip |
| Bowl wall | 3 deg draft (wider at the top) so ash tips out |
| Floor-to-wall fillet | R10, so there are no internal corners anywhere |
| Rim edges | R2 outer, R1.5 inner. 0.8 mm 45 deg chamfer on the bottom outer edge (elephant-foot relief) |
| Bowl capacity | ~248 ml |
| Rests (U-notches, R1 edges) | Cigar Ø22 at the crown (bottom 11 mm below rim). Cigarette Ø9 x2 on the upper cranium (7 mm deep). Joint Ø11 x2 at the widest point of the cranium (8 mm deep) |
| Face inlay | Black, 1.5 mm thick, flush with the bowl surface: two eye sockets (~23 x 22), nasal opening, teeth band (32 x 14) drawn as 1.6 mm lines |
| Weight | ~212 g ABS / ~258 g PETG at 100% infill (less at normal infill) |

## Files

| File | Use |
|---|---|
| `skull-ashtray-white.stl` + `skull-ashtray-black.stl` | **Two-colour print.** Import both together in Bambu Studio and answer **Yes** to "load as a single object with multiple parts". Then set the white body to filament 1 and the inlay to filament 2 (black) |
| `skull-ashtray.3mf` | Both bodies in one file (arrives as two objects; group them if the slicer doesn't) |
| `skull-ashtray-single-color.stl` | One-colour version (no inlay split) |
| `skull-ashtray.step` | Both bodies as solids (CAD exchange) |
| `skull-ashtray.FCStd` | FreeCAD document (`Body_White`, `Inlay_Black`) |

## 3D printing

- **Orientation:** print as modelled, flat base down. No supports. The build checks the mesh, and no surface faces down at more than 45 deg except the base itself. The bowl only widens going up, the notches open upward, and the inlay is flat on the floor and the lower fillet.
- **Two colours:** the black face sits between z = 6.5 and 8 mm (and slightly higher where it runs up the fillet). On the H2D's two nozzles that is only ~8 layers of colour changes, so the purge waste is small.
- **Material:** don't use PLA (it softens at ~60 C). **ABS or ASA** is the minimum (heat deflection ~95 C). PETG works but marks sooner. Any plastic will scorch if a cigarette burns down to the notch or someone stubs out on the floor.
- **Suggested settings:** 0.2 mm layers, 4 walls, 4-5 top/bottom layers, 15-25% gyroid infill (raise it for more weight), no supports, brim optional. ABS/ASA: enclosure closed, bed ~100 C.

## Assumptions to confirm

- The face sits on the bowl floor, so ash hides it when the tray is full (this was concept A's trade-off).
- Rest sizes: Ø9 cigarette, Ø11 joint, Ø22 cigar. Edit `RESTS` to move, add or resize them.
- The outline is a stylised frontal skull: domed cranium, pinched temples, flared cheekbones, mandible and chin.
