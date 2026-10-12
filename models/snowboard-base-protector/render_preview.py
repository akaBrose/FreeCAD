"""Render preview PNG (plan + sections) from the built .FCStd. Run with freecadcmd: render_preview.py <name> <section_y>.
Uses the same env: set PREVIEW_NAME / PREVIEW_Y as env vars."""
import os
import FreeCAD as App
from FreeCAD import Vector
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
name = os.environ.get("PREVIEW_NAME", "snowboard-base-protector")
sec_y = float(os.environ.get("PREVIEW_Y", "0"))
sec_x = float(os.environ.get("PREVIEW_X", "0"))
doc = App.openDocument(os.path.join(here, name + ".FCStd"))
sh = {o.Name: o.Shape for o in doc.Objects}
col = {"Liner": "#3b82c4", "Skin": "#e0a030", "Scales": "#222222", "Gear_Reference": "#999999"}


def draw(ax, shape, normal, d, c, project, lw=0.7):
    for w in shape.slice(normal, d):
        pts = w.discretize(Deflection=0.2)
        ax.plot([project(p)[0] for p in pts], [project(p)[1] for p in pts], color=c, lw=lw)


fig, axs = plt.subplots(4, 1, figsize=(13, 15), gridspec_kw={"height_ratios": [1.1, 0.7, 0.9, 0.9]})
# plan view from below: scales footprint (slice 11 mm below the base plane) + liner outline
ax = axs[0]
draw(ax, sh["Liner"], Vector(0, 0, 1), 0.5, col["Liner"], lambda p: (p.x, p.y), 1.2)
draw(ax, sh["Scales"], Vector(0, 0, 1), -11.0, col["Scales"], lambda p: (p.x, p.y), 0.5)
ax.set_aspect("equal"); ax.set_title(name + " - plan (liner pocket outline blue, scales cut at z=-11 black)")
# longitudinal section, zoomed near the waist
ax = axs[1]
for n in ("Liner", "Skin", "Scales", "Gear_Reference"):
    draw(ax, sh[n], Vector(0, 1, 0), sec_y, col[n], lambda p: (p.x, p.z), 0.9)
ax.set_xlim(-90, 90); ax.set_aspect("equal")
ax.set_title("longitudinal section at y=%g, x -90..90 (liner blue, skin orange, scales black, gear grey)" % sec_y)
# full-length longitudinal section (z exaggerated x4)
ax = axs[2]
for n in ("Liner", "Skin", "Scales", "Gear_Reference"):
    draw(ax, sh[n], Vector(0, 1, 0), sec_y, col[n], lambda p: (p.x, p.z * 4), 0.6)
ax.set_title("full-length section at y=%g (z exaggerated x4) - flex-relief grooves visible" % sec_y)
# cross section
ax = axs[3]
for n in ("Liner", "Skin", "Scales", "Gear_Reference"):
    draw(ax, sh[n], Vector(1, 0, 0), sec_x, col[n], lambda p: (p.y, p.z), 0.9)
ax.set_aspect("equal"); ax.set_title("cross section at x=%g (looking along the length)" % sec_x)
plt.tight_layout()
out = os.path.join(here, name + "-preview.png")
plt.savefig(out, dpi=90)
print("wrote", out)
