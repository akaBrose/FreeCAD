# FreeCAD

Models, scripts, and notes from working with FreeCAD (target: 1.1.x on macOS).

## Layout

| Folder | Contents |
|---|---|
| `models/<project>/` | One folder per project: `build.py` (parametric script), `.FCStd` file, exports (STEP/STL), and a short `README.md` with dimensions and purpose |
| `notes/` | Q&A write-ups, how-tos, gotchas |
| `templates/` | Reusable script skeletons |
| `scripts/` | Helper scripts (e.g. the headless runner) |

## Building a model headless

```bash
scripts/run.sh models/<project>/build.py
```

This runs the script with FreeCAD's bundled `freecadcmd`. Each `build.py` defines its dimensions as variables at the top, builds the part, and saves the `.FCStd` and exports next to itself.

## Conventions

- Units are mm unless stated.
- Parameters sit at the top of each script so models are easy to tweak.
- Each project folder documents its purpose, key dimensions, and how to rebuild.
