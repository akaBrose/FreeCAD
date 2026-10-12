"""<Project name> - parametric FreeCAD build script. Units: mm."""
import os
import FreeCAD as App
import Part

# --- Parameters ---
LENGTH = 50.0
WIDTH = 30.0
HEIGHT = 10.0

# --- Build ---
here = os.path.dirname(os.path.abspath(__file__))
doc = App.newDocument("Part")
body = doc.addObject("Part::Box", "Body")
body.Length, body.Width, body.Height = LENGTH, WIDTH, HEIGHT
doc.recompute()

# --- Save / export ---
doc.saveAs(os.path.join(here, "part.FCStd"))
Part.export([body], os.path.join(here, "part.step"))
