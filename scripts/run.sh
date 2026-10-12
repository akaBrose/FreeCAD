#!/bin/zsh
# Run a FreeCAD Python script headless. Usage: scripts/run.sh path/to/build.py
exec /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd "$@"
