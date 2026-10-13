"""Disc golf towel quick-detach v2 - funnel holster + grab paddle. Units: mm.

Receiver (bag side): closed-sided pocket with a wide 45-degree funnel mouth, so the paddle drops in without
aiming. Walls on all four sides mean the paddle can only leave straight UP. Two magnet pairs in the floor
seat it and hold it against lift-out. Tongue (towel side): paddle + wide grab head with finger scallops and a
strap slot. Magnet pockets are sealed voids for a print-pause insert.
"""
import os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
PAD_W, PAD_T = 28.0, 10.0         # paddle width (X) and thickness (Y)
CLEAR = 0.3                       # pocket clearance per side
POCKET_DEPTH = 34.0               # pocket depth from the block top
FLOOR = 6.0                       # floor thickness under the pocket (cover + magnet void + skin)
FLARE = 5.0                       # funnel flare per side (45 deg, so also 5 mm tall)
RX, RY = 44.0, 28.0               # receiver block footprint; Y=0 is the bag side
PY = 15.0                         # pocket/paddle centerline in Y
HEAD_W, HEAD_T, HEAD_H = 36.0, 14.0, 24.0   # grab head
HEAD_TAPER = 4.0                  # 45 deg under-head taper (no overhang)
HEAD_GAP = 1.2                    # head clearance above receiver top when seated
STRAP_W, STRAP_H = 22.0, 4.0      # strap slot (through Y), chamfered top
MAG_D, MAG_T, MAG_X = 8.0, 4.0, 6.0   # two N52 discs at x = +/-MAG_X
MAG_FIT, SKIN, END_GAP = 0.2, 0.4, 0.2
WEB_Y0, WEB_Y1, WEB_Z0, WEB_Z1 = 2.5, 6.0, 7.5, 32.5   # strap / carabiner cross slot (through X)
DRAIN_W, DRAIN_H = 20.0, 3.0

# --- Derived ---
RZ = FLOOR + POCKET_DEPTH
PXH, PYH = PAD_W / 2 + CLEAR, PAD_T / 2 + CLEAR          # pocket half sizes
Z_T0 = FLOOR + END_GAP
SHAFT_LEN = POCKET_DEPTH - END_GAP + HEAD_GAP            # shaft top clears receiver by HEAD_GAP
Z_T1 = Z_T0 + SHAFT_LEN
POCKET_D, POCKET_H = MAG_D + MAG_FIT, MAG_T + MAG_FIT

def rect(cx, cy, hw, hd, z):
    return Part.makePolygon([V(cx - hw, cy - hd, z), V(cx + hw, cy - hd, z), V(cx + hw, cy + hd, z),
                             V(cx - hw, cy + hd, z), V(cx - hw, cy - hd, z)])
def prism(cx, cy, hw, hd, z0, z1):
    return Part.Face(rect(cx, cy, hw, hd, z0)).extrude(V(0, 0, z1 - z0))
def cyl(d, h, x, y, z): return Part.makeCylinder(d / 2, h, V(x, y, z))
def box(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def loft(w0, w1):
    return Part.makeLoft([w0, w1], True, True)

# --- Receiver ---
rec = box(-RX / 2, RX / 2, 0, RY, 0, RZ)
try:
    rec = rec.makeFillet(3.0, [e for e in rec.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6])
except Exception as ex:
    print("WARN receiver fillet skipped:", ex)
rec = rec.cut(prism(0, PY, PXH, PYH, FLOOR, RZ + 1))
rec = rec.cut(loft(rect(0, PY, PXH, PYH, RZ - FLARE), rect(0, PY, PXH + FLARE + 1, PYH + FLARE + 1, RZ + 1)))
rec = rec.cut(box(-RX, RX, WEB_Y0, WEB_Y1, WEB_Z0, WEB_Z1))
rec = rec.cut(box(-DRAIN_W / 2, DRAIN_W / 2, PY, RY + 1, FLOOR, FLOOR + DRAIN_H))
mz_r = FLOOR - SKIN - POCKET_H
for sx in (-MAG_X, MAG_X):
    rec = rec.cut(cyl(POCKET_D, POCKET_H, sx, PY, mz_r))

# --- Tongue (seated) ---
shaft = prism(0, PY, PAD_W / 2, PAD_T / 2, Z_T0, Z_T1)
try:
    shaft = shaft.makeChamfer(1.5, [e for e in shaft.Edges if all(abs(v.Z - Z_T0) < 1e-6 for v in e.Vertexes)])
except Exception as ex:
    print("WARN tongue chamfer skipped:", ex)
taper = loft(rect(0, PY, PAD_W / 2, PAD_T / 2, Z_T1), rect(0, PY, HEAD_W / 2, HEAD_T / 2, Z_T1 + HEAD_TAPER))
head = prism(0, PY, HEAD_W / 2, HEAD_T / 2, Z_T1 + HEAD_TAPER, Z_T1 + HEAD_H)
try:
    head = head.makeFillet(2.5, [e for e in head.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6])
except Exception as ex:
    print("WARN head fillet skipped:", ex)
sz = Z_T1 + HEAD_H - 8.0                                    # strap slot centre, near the top
hx, ho, y0 = STRAP_W / 2, STRAP_H / 2, PY - HEAD_T
pts = [V(-hx, y0, sz), V(-hx + ho, y0, sz + ho), V(hx - ho, y0, sz + ho), V(hx, y0, sz),
       V(hx - ho, y0, sz - ho), V(-hx + ho, y0, sz - ho), V(-hx, y0, sz)]
head = head.cut(Part.Face(Part.makePolygon(pts)).extrude(V(0, 2 * HEAD_T, 0)))
for sy in (-1, 1):   # finger scallops on both faces, below the slot
    head = head.cut(Part.makeCylinder(9.0, HEAD_W + 2, V(-HEAD_W / 2 - 1, PY + sy * (HEAD_T / 2 + 6.0), Z_T1 + HEAD_TAPER + 7.0),
                                      V(1, 0, 0)))
tongue = shaft.fuse(taper).fuse(head).removeSplitter()
for sx in (-MAG_X, MAG_X):
    tongue = tongue.cut(cyl(POCKET_D, POCKET_H, sx, PY, Z_T0 + SKIN))
tongue_print = tongue.copy()
tongue_print.translate(V(0, 0, -Z_T0))

mags = [cyl(MAG_D, MAG_T, sx, PY, mz_r + 0.1) for sx in (-MAG_X, MAG_X)] + \
       [cyl(MAG_D, MAG_T, sx, PY, Z_T0 + SKIN + 0.1) for sx in (-MAG_X, MAG_X)]

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
doc = App.newDocument("DGTowelQDv2")
objs = {}
items = [("Receiver", rec), ("Tongue", tongue)] + [("Magnet%d" % i, m) for i, m in enumerate(mags)]
for name, shp in items:
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    objs[name] = o
doc.recompute()
fc = os.path.join(here, "dg-towel-qd-v2.FCStd")
doc.saveAs(fc)
show_on_open(fc, list(objs))
import MeshPart, Mesh
def stl(shp, fn):
    Mesh.Mesh(MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.03, AngularDeflection=0.15)).write(os.path.join(here, fn))
stl(rec, "dg-towel-qd-v2-receiver.stl")
stl(tongue_print, "dg-towel-qd-v2-tongue.stl")
for n in ("Receiver", "Tongue"):
    Part.export([objs[n]], os.path.join(here, "dg-towel-qd-v2-%s.step" % n.lower()))

print("RESULT receiver valid=%s solids=%d vol=%.0f bbox=%s" % (rec.isValid(), len(rec.Solids), rec.Volume, rec.BoundBox))
print("RESULT tongue valid=%s solids=%d vol=%.0f bbox=%s" % (tongue.isValid(), len(tongue.Solids), tongue.Volume, tongue.BoundBox))
print("RESULT interference=%.4f  magnet-in-solid: %s" % (rec.common(tongue).Volume, [round(m.common(s).Volume, 3) for m, s in zip(mags, [rec, rec, tongue, tongue])]))
print("RESULT mouth %.1f x %.1f vs paddle %.1f x %.1f; head gap %.2f; magnet gap %.2f; funnel front wall at mouth %.2f" % (
    2 * (PXH + FLARE), 2 * (PYH + FLARE), PAD_W, PAD_T, Z_T1 - RZ, 2 * SKIN + END_GAP, RY - (PY + PYH + FLARE)))
