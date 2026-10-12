"""Render preview PNG (plan + sections) from the built .FCStd with freecadcmd.
Env: PREVIEW_NAME (project name), PREVIEW_Y (y of the longitudinal sections), PREVIEW_TIPX (x of the tip-end zoom)."""
import os
import FreeCAD as App
from FreeCAD import Vector
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
name = os.environ.get("PREVIEW_NAME", "snowboard-base-protector")
sec_y = float(os.environ.get("PREVIEW_Y", "0"))
tip_x = float(os.environ.get("PREVIEW_TIPX", "700"))
doc = App.openDocument(os.path.join(here, name + ".FCStd"))
sh = {o.Name: o.Shape for o in doc.Objects}
COL = {"Liner": "#3b82c4", "Skin": "#e0a030", "Scales": "#222222", "Gear_Reference": "#9a9a9a",
       "Tip_Cap_Shell": "#c0392b", "Tail_Cap_Shell": "#c0392b", "Tip_Cap_Liner": "#e67e22",
       "Tail_Cap_Liner": "#e67e22", "Straps": "#27ae60"}


def draw(ax, n, normal, d, project, lw=0.8):
    for w in sh[n].slice(normal, d):
        pts = w.discretize(Deflection=0.2)
        ax.plot([project(p)[0] for p in pts], [project(p)[1] for p in pts], color=COL[n], lw=lw)


fig, axs = plt.subplots(4, 1, figsize=(13, 17), gridspec_kw={"height_ratios": [1.1, 0.8, 0.8, 1.0]})
ax = axs[0]
for n, z, lw in [("Liner", 0.5, 1.0), ("Skin", -3.0, 0.8), ("Scales", -8.0, 0.4), ("Tip_Cap_Shell", 0.5, 1.0),
                 ("Tail_Cap_Shell", 0.5, 1.0), ("Tip_Cap_Liner", 0.5, 0.6), ("Tail_Cap_Liner", 0.5, 0.6),
                 ("Straps", sh["Straps"].BoundBox.ZMax - 0.5, 1.0)]:
    draw(ax, n, Vector(0, 0, 1), z, lambda p: (p.x, p.y), lw)
ax.set_aspect("equal")
ax.set_title(name + " - plan: liner blue, skin+tabs orange, scales black, caps red/orange, straps green")
ax = axs[1]
for n in COL:
    draw(ax, n, Vector(0, 1, 0), sec_y, lambda p: (p.x, p.z), 0.9)
ax.set_xlim(tip_x - 130, tip_x + 130); ax.set_ylim(-14, 24); ax.set_aspect("equal")
ax.set_title("tip end, longitudinal section at y=%g: shell red, cap lining orange, body gap 1 mm at left" % sec_y)
ax = axs[2]
for n in COL:
    draw(ax, n, Vector(0, 1, 0), sec_y, lambda p: (p.x, p.z), 0.9)
ax.set_xlim(-60, 120); ax.set_ylim(-14, 20); ax.set_aspect("equal")
ax.set_title("body at y=%g: lip V-notches, floor grooves, nested scales" % sec_y)
ax = axs[3]
for n in COL:
    draw(ax, n, Vector(1, 0, 0), 0.0, lambda p: (p.y, p.z), 0.9)
ax.set_aspect("equal"); ax.set_title("cross section at x=0 (strap station): tabs with slots, strap over the gear")
plt.tight_layout()
out = os.path.join(here, name + "-preview.png")
plt.savefig(out, dpi=85)
print("wrote", out)
