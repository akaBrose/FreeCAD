"""Render a preview PNG (3D views + sections) from skull-ashtray.FCStd. Run with freecadcmd."""
import os
import numpy as np
import FreeCAD as App
from FreeCAD import Vector
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

here = os.path.dirname(os.path.abspath(__file__))
doc = App.openDocument(os.path.join(here, "skull-ashtray.FCStd"))
sh = {o.Name: o.Shape for o in doc.Objects}
COL = {"Body_White": np.array([0.93, 0.92, 0.89]), "Inlay_Black": np.array([0.13, 0.13, 0.13])}
LIGHT = np.array([-0.4, -0.6, 1.0]); LIGHT /= np.linalg.norm(LIGHT)


def tris(shape, lift=0.0):
    import MeshPart
    m = MeshPart.meshFromShape(Shape=shape, MaxLength=2.5)          # small, even triangles so depth sorting works
    m.harmonizeNormals()
    if m.Volume < 0:
        m.flipNormals()
    t = np.array([[p for p in f.Points] for f in m.Facets]) + np.array([0, 0, lift])
    n = np.array([f.Normal for f in m.Facets])
    return t, n


meshes = {k: tris(s, 0.15 if k == "Inlay_Black" else 0.0) for k, s in sh.items()}


def view3d(ax, elev, azim, title):
    """Orthographic painter's-algorithm render: back faces culled, all triangles of both bodies depth-sorted together."""
    e, a = np.radians(elev), np.radians(azim)
    view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])       # towards the viewer
    right = np.array([-np.sin(a), np.cos(a), 0.0])
    up = np.cross(view, right)
    polys, cols, depth = [], [], []
    for k, (t, n) in meshes.items():
        vis = n @ view > 0
        tv, nv = t[vis], n[vis]
        shade = 0.35 + 0.65 * np.clip(nv @ LIGHT, 0, 1)
        polys.append(np.stack([tv @ right, tv @ up], axis=-1))
        cols.append(np.clip(COL[k][None, :] * shade[:, None] + (0.06 if k == "Inlay_Black" else 0), 0, 1))
        depth.append((tv @ view).mean(axis=1))
    polys, cols, depth = np.concatenate(polys), np.concatenate(cols), np.concatenate(depth)
    order = np.argsort(depth)
    ax.add_collection(PolyCollection(polys[order], facecolors=cols[order], edgecolors=cols[order], linewidths=0.2))
    ax.autoscale_view(); ax.set_aspect("equal"); ax.set_axis_off(); ax.set_title(title)


fig = plt.figure(figsize=(15, 12))
view3d(fig.add_subplot(2, 2, 1, ), 38, -62, "Isometric (white body, black face inlay)")
view3d(fig.add_subplot(2, 2, 2, ), 90, -90, "Top view (as seen on the table)")


def section(ax, normal, d, proj, title, xlim):
    for k, s in sh.items():
        for w in s.slice(normal, d):
            pts = w.discretize(Deflection=0.05)
            xy = np.array([proj(p) for p in pts])
            ax.fill(xy[:, 0], xy[:, 1], color=COL[k] * 0.9 if k == "Body_White" else COL[k], ec="k", lw=0.6)
    ax.set_aspect("equal"); ax.set_xlim(*xlim); ax.set_ylim(-2, 42); ax.grid(alpha=0.3); ax.set_title(title)
    ax.set_ylabel("Z mm")


section(fig.add_subplot(4, 2, 6), Vector(1, 0, 0), 0.0, lambda p: (p.y, p.z),
        "Section X=0 (chin left, crown right): teeth/nose inlay, cigar rest", (-3, 153))
section(fig.add_subplot(4, 2, 8), Vector(0, 1, 0), 100.0, lambda p: (p.x, p.z),
        "Section Y=100 (through the joint rests): R10 floor fillet, 3 deg draft", (-53, 53))
view3d(fig.add_subplot(2, 2, 3, ), 20, -125, "Rear three-quarter (crown cigar rest, cigarette rests)")
plt.tight_layout()
out = os.path.join(here, "skull-ashtray-preview.png")
plt.savefig(out, dpi=80)
print("wrote", out)
