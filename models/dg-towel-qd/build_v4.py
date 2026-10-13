"""Disc golf towel quick-detach v4 - velcro base with a tilted funnel-ramp catcher for a 1" steel grommet. Units: mm.

Model orientation = print orientation: back (velcro) face on the bed at z=0, +Z outward from the bag, +Y UP on the bag.
A ramp (seat plane tilted ANGLE from the plate normal, facing up and outward) carries a smooth flared tray. A grommet
swung in anywhere on the wide mouth slides down the ramp under gravity, is pulled flat by the magnets, and is centred by
the U-shaped bottom, where a small bullet peg enters its hole. The lanyard leaves through a notch at the bottom.
Release: pull the lanyard up and outward - the ring lifts off the magnets and rides up the flared walls and out.
"""
import math, os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
PLATE_T, PLATE_R, MARGIN = 4.0, 8.0, 6.0
VEL_DEPTH, VEL_RIM = 1.2, 4.0                    # velcro recess on the back, rim left around it
ANGLE = 25.0                                     # seat plane tilt from the plate normal (toward up)
RU = 22.0                                        # U-bottom radius (grommet OD 38 -> r 19, 3 mm slack)
U_STRAIGHT, V_FLARE0, V_FLARE1, V_TOP = 8.0, 8.0, 34.0, 38.0   # tray outline along the ramp (v)
W_TOP = 36.0                                     # half-width of the tray at the top (flared mouth)
WALL, RIM_H, FLARE = 3.0, 7.0, 5.0               # wall thickness, wall height, extra flare at the wall top
H_TOP = 2.0                                      # ramp height above the plate at its top end
PEG_BASE_R, PEG_TIP_R, PEG_LEN, PEG_V = 5.5, 2.8, 16.0, 2.5   # bullet peg (offset up so the lanyard has room below)
NOTCH_W = 12.0                                   # lanyard notch through the bottom wall
GROM_ID, GROM_OD, GROM_T = 25.4, 38.0, 2.5       # reference ring (OD/thickness assumed - measure yours)
MAG_N, MAG_D, MAG_T, MAG_R = 4, 6.0, 3.0, 15.5
MAG_FIT, MAG_RECESS = 0.1, 0.2

# --- Frame: local (u,v,w) -> global; u=X, v=up the ramp, w=seat normal ---
th = math.radians(ANGLE)
e1, e2, a = V(1, 0, 0), V(0, math.cos(th), -math.sin(th)), V(0, math.sin(th), math.cos(th))
C = V(0, 0, PLATE_T + H_TOP + V_TOP * math.sin(th))          # seat centre (y shifted later)

def to_global(shape, origin):
    M = App.Matrix(e1.x, e2.x, a.x, origin.x, e1.y, e2.y, a.y, origin.y, e1.z, e2.z, a.z, origin.z, 0, 0, 0, 1)
    s = shape.copy()
    s.transformShape(M)
    return s

# --- Tray outline (local, w=0) ---
def outline():
    r, w = RU, W_TOP
    pts = [V(r, 0, 0), V(r, U_STRAIGHT, 0), V(w, V_FLARE1, 0), V(w, V_TOP, 0), V(-w, V_TOP, 0), V(-w, V_FLARE1, 0),
           V(-r, U_STRAIGHT, 0), V(-r, 0, 0)]
    edges = [Part.LineSegment(pts[i], pts[i + 1]).toShape() for i in range(len(pts) - 1)]
    edges.append(Part.Arc(V(-r, 0, 0), V(0, -r, 0), V(r, 0, 0)).toShape())
    return Part.Wire(edges)

base_w = outline()
def offs(d, w):
    o = base_w.makeOffset2D(d, join=0, fill=False, openResult=False, intersection=False) if d != 0 else base_w.copy()
    o.translate(V(0, 0, w))
    return o

block = Part.Face(offs(FLARE + WALL, -70.0)).extrude(V(0, 0, 70.0 + RIM_H))
try:
    cavity = Part.makeLoft([offs(0.0, 0.0), offs(FLARE, RIM_H + 1.0)], True, False)
    if not cavity.isValid() or cavity.Volume < 1:
        raise ValueError("bad loft")
except Exception as ex:
    print("WARN loft failed, straight walls:", ex)
    cavity = Part.Face(offs(0.0, 0.0)).extrude(V(0, 0, RIM_H + 1.0))
notch = Part.makeBox(NOTCH_W, 14.0, RIM_H + 2.0, V(-NOTCH_W / 2, -(RU + 12.0), 0.0))

# --- Assemble in global, find the footprint, size the plate ---
blk = to_global(block, C).common(Part.makeBox(300, 300, 300, V(-150, -150, 0)))
bb = blk.BoundBox
PLATE_W = 2 * (max(abs(bb.XMin), abs(bb.XMax)) + MARGIN)
PLATE_H = (bb.YMax - bb.YMin) + 2 * MARGIN
dy = MARGIN - bb.YMin
plate = Part.makeBox(PLATE_W, PLATE_H, PLATE_T, V(-PLATE_W / 2, 0, 0))
plate = plate.makeFillet(PLATE_R, [e for e in plate.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6])
Cs = C + V(0, dy, 0)
blk.translate(V(0, dy, 0))
body = plate.fuse(blk)
body = body.cut(to_global(cavity, Cs)).cut(to_global(notch, Cs))

# --- Bullet peg ---
pb = Cs + e2 * PEG_V
peg = Part.makeCone(PEG_BASE_R, PEG_TIP_R, PEG_LEN, pb - a * 1.0, a)
peg = peg.fuse(Part.makeSphere(PEG_TIP_R, pb + a * PEG_LEN, a))
body = body.fuse(peg).removeSplitter()

# --- Magnet pockets (open to the floor; press-fit + glue, recessed) ---
pk_d, pk_h = MAG_D + MAG_FIT, MAG_T + MAG_RECESS
pos = [Cs + (e1 * math.cos(math.radians(360.0 / MAG_N * i + 45)) + e2 * math.sin(math.radians(360.0 / MAG_N * i + 45))) * MAG_R
       for i in range(MAG_N)]
for p in pos:
    body = body.cut(Part.makeCylinder(pk_d / 2, pk_h + 2, p - a * pk_h, a))

# --- Velcro recess on the back ---
body = body.cut(Part.makeBox(PLATE_W - 2 * VEL_RIM, PLATE_H - 2 * VEL_RIM, VEL_DEPTH, V(-PLATE_W / 2 + VEL_RIM, VEL_RIM, 0)))

# --- Reference parts (not printed) ---
ring = Part.makeCylinder(GROM_OD / 2, GROM_T, Cs, a).cut(Part.makeCylinder(GROM_ID / 2, GROM_T + 2, Cs - a, a))
mags = [Part.makeCylinder(MAG_D / 2, MAG_T, p - a * pk_h + a * 0.1, a) for p in pos]

# --- Save / export ---
def show_on_open(path, names):
    import zipfile, shutil
    vp = "".join('<ViewProvider name="%s" expanded="0"><Properties Count="1" TransientCount="0">'
                 '<Property name="Visibility" type="App::PropertyBool" status="1"><Bool value="true"/></Property>'
                 '</Properties></ViewProvider>' % n for n in names)
    xml = ('<?xml version="1.0" encoding="utf-8"?><Document SchemaVersion="1" HasExpansion="1"><Expand />'
           '<ViewProviderData Count="%d">%s</ViewProviderData></Document>' % (len(names), vp))
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename != "GuiDocument.xml":
                zout.writestr(item, zin.read(item.filename))
        zout.writestr("GuiDocument.xml", xml)
    shutil.move(tmp, path)

here = os.path.dirname(os.path.abspath(__file__))
doc = App.newDocument("DGTowelQDv4")
objs = {}
for n, s in [("Base", body), ("Grommet_ref", ring)] + [("Magnet%d" % i, m) for i, m in enumerate(mags)]:
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    objs[n] = o
doc.recompute()
fc = os.path.join(here, "dg-towel-qd-v4.FCStd")
doc.saveAs(fc)
show_on_open(fc, list(objs))
import MeshPart, Mesh
Mesh.Mesh(MeshPart.meshFromShape(Shape=body, LinearDeflection=0.03, AngularDeflection=0.15)).write(os.path.join(here, "dg-towel-qd-v4-base.stl"))
Part.export([objs["Base"]], os.path.join(here, "dg-towel-qd-v4-base.step"))

b2 = body.BoundBox
print("RESULT base valid=%s solids=%d vol=%.0f bbox=%s" % (body.isValid(), len(body.Solids), body.Volume, b2))
print("RESULT plate %.0f x %.0f; ring/base interference=%.3f mm3; magnets in solid=%s" % (
    PLATE_W, PLATE_H, ring.common(body).Volume, [round(m.common(body).Volume, 3) for m in mags]))
print("RESULT ring sits in U: slack %.1f mm; peg base dia %.1f vs hole %.1f" % (RU - GROM_OD / 2, 2 * PEG_BASE_R, GROM_ID))
