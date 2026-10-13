"""Disc golf towel quick-detach - shear-locked, magnet-assisted slide latch. Units: mm.

Receiver (bag side): block with a vertical dovetail channel open at the top and front, plus a
cross slot for a velcro strap / carabiner. Tongue (towel side): dovetail shaft + head plate with a
strap slot. The dovetail carries swing and snag loads; the magnet pair only seats and retains the
tongue along the open (upward) direction. One magnet pocket per part is a sealed void for a
print-pause magnet insert.
"""
import os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
RX, RY, RZ = 38.0, 24.0, 36.0     # receiver block (X width, Y depth, Z height); Y=0 is the bag side
FLOOR = 7.0                       # channel floor height (holds magnet pocket)
DT_FRONT = 16.0                   # tongue dovetail width at the front (narrow, open side)
DT_BACK = 24.0                    # tongue dovetail width at the back (wide, deep side)
DT_DEPTH = 12.0                   # tongue dovetail depth in Y
SLIDE_CLEAR = 0.25                # sliding clearance per side
END_GAP = 0.2                     # gap between tongue end and channel floor when seated
SHAFT_LEN = 30.0                  # tongue length inside the channel
HEAD_Z, HEAD_Y0, HEAD_Y1 = 14.0, 14.0, 26.0   # head plate height, and Y span (front protrudes 2 mm)
STRAP_W, STRAP_H = 22.0, 4.0      # strap slot (hex-shaped top so it prints without bridging 22 mm)
MAG_D, MAG_T = 10.0, 5.0          # magnet disc (N52); pocket adds MAG_FIT
MAG_FIT = 0.2
SKIN = 0.4                        # plastic over each magnet face
WEB_Y0, WEB_Y1 = 3.0, 6.5         # webbing / carabiner cross slot (Y span)
WEB_Z0, WEB_Z1 = 10.0, 32.0       # and Z span
DRAIN_Y0, DRAIN_Y1, DRAIN_H = 15.0, 21.0, 3.0   # grit/water drain through the side walls
LEAD_CHAMFER = 1.5

# --- Derived ---
YF = RY                                   # receiver front face
Y_INNER = YF - DT_DEPTH - SLIDE_CLEAR     # inner end of channel
MAG_CY = YF - DT_DEPTH / 2.0              # magnet center in Y
Z_T0 = FLOOR + END_GAP                    # tongue bottom, seated
Z_T1 = Z_T0 + SHAFT_LEN                   # tongue shaft top, seated
POCKET_D, POCKET_H = MAG_D + MAG_FIT, MAG_T + MAG_FIT

def trap(wf, wb, yf, yb, z0, z1):
    """Dovetail prism: width wf at y=yf (front), wb at y=yb (back), extruded z0..z1."""
    pts = [V(-wf / 2, yf, z0), V(wf / 2, yf, z0), V(wb / 2, yb, z0), V(-wb / 2, yb, z0), V(-wf / 2, yf, z0)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, z1 - z0))

def cyl(d, h, x, y, z):
    return Part.makeCylinder(d / 2, h, V(x, y, z))

def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

# --- Receiver ---
rec = box(-RX / 2, RX / 2, 0, RY, 0, RZ)
try:
    rec = rec.makeFillet(2.0, [e for e in rec.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6])
except Exception as ex:
    print("WARN receiver fillet skipped:", ex)
chan = trap(DT_FRONT + 2 * SLIDE_CLEAR, DT_BACK + 2 * SLIDE_CLEAR, YF + 1, Y_INNER, FLOOR, RZ + 1)
rec = rec.cut(chan)
try:   # lead-in chamfer around the channel mouth
    mouth = [e for e in rec.Edges if all(abs(v.Z - RZ) < 1e-6 and abs(v.X) < DT_BACK / 2 + 1 and v.Y > Y_INNER - 0.1 for v in e.Vertexes)]
    rec = rec.makeChamfer(LEAD_CHAMFER, mouth)
except Exception as ex:
    print("WARN lead-in chamfer skipped:", ex)
rec = rec.cut(box(-RX, RX, WEB_Y0, WEB_Y1, WEB_Z0, WEB_Z1))                       # webbing slot
rec = rec.cut(box(-RX, RX, DRAIN_Y0, DRAIN_Y1, FLOOR, FLOOR + DRAIN_H))           # drain
rec_pocket_z0 = FLOOR - SKIN - POCKET_H
rec = rec.cut(cyl(POCKET_D, POCKET_H, 0, MAG_CY, rec_pocket_z0))                   # sealed void

# --- Tongue (seated position) ---
shaft = trap(DT_FRONT, DT_BACK, YF, YF - DT_DEPTH, Z_T0, Z_T1)
try:
    shaft = shaft.makeChamfer(1.0, [e for e in shaft.Edges if all(abs(v.Z - Z_T0) < 1e-6 for v in e.Vertexes)])
except Exception as ex:
    print("WARN tongue bottom chamfer skipped:", ex)
head = box(-RX / 2, RX / 2, HEAD_Y0, HEAD_Y1, Z_T1, Z_T1 + HEAD_Z)
hz = Z_T1 + HEAD_Z / 2
hx, ho = STRAP_W / 2, STRAP_H / 2
hexpts = [V(-hx, HEAD_Y0 - 1, hz), V(-hx + ho, HEAD_Y0 - 1, hz + ho), V(hx - ho, HEAD_Y0 - 1, hz + ho), V(hx, HEAD_Y0 - 1, hz),
          V(hx - ho, HEAD_Y0 - 1, hz - ho), V(-hx + ho, HEAD_Y0 - 1, hz - ho), V(-hx, HEAD_Y0 - 1, hz)]
slot = Part.Face(Part.makePolygon(hexpts)).extrude(V(0, HEAD_Y1 - HEAD_Y0 + 2, 0))
head = head.cut(slot)
tongue = shaft.fuse(head).removeSplitter()
tongue = tongue.cut(cyl(POCKET_D, POCKET_H, 0, MAG_CY, Z_T0 + SKIN))               # sealed void

# --- Reference magnets (not printed) ---
mag_r = cyl(MAG_D, MAG_T, 0, MAG_CY, rec_pocket_z0 + 0.1)
mag_t = cyl(MAG_D, MAG_T, 0, MAG_CY, Z_T0 + SKIN + 0.1)

# --- Print-orientation tongue (end face on bed) ---
tongue_print = tongue.copy()
tongue_print.translate(V(0, 0, -Z_T0))

# --- Save / export ---
def show_on_open(path, names):
    """Headless saves have no GUI data, so objects open hidden. Add GuiDocument.xml with Visibility on."""
    import zipfile, shutil
    vp = "".join(
        '<ViewProvider name="%s" expanded="0"><Properties Count="1" TransientCount="0">'
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
doc = App.newDocument("DGTowelQD")
objs = {}
for name, shp in [("Receiver", rec), ("Tongue", tongue), ("Magnet_Receiver", mag_r), ("Magnet_Tongue", mag_t)]:
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    objs[name] = o
doc.recompute()
fc = os.path.join(here, "dg-towel-qd.FCStd")
doc.saveAs(fc)
show_on_open(fc, list(objs))

import MeshPart, Mesh
def stl(shp, fn):
    Mesh.Mesh(MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.03, AngularDeflection=0.15)).write(os.path.join(here, fn))
stl(rec, "dg-towel-qd-receiver.stl")
stl(tongue_print, "dg-towel-qd-tongue.stl")
for n in ("Receiver", "Tongue"):
    Part.export([objs[n]], os.path.join(here, "dg-towel-qd-%s.step" % n.lower()))

print("RESULT receiver valid=%s solids=%d vol=%.0f bbox=%s" % (rec.isValid(), len(rec.Solids), rec.Volume, rec.BoundBox))
print("RESULT tongue valid=%s solids=%d vol=%.0f bbox=%s" % (tongue.isValid(), len(tongue.Solids), tongue.Volume, tongue.BoundBox))
print("RESULT interference tongue/receiver = %.4f mm3" % rec.common(tongue).Volume)
print("RESULT magnet/solid overlap: rec %.4f  tongue %.4f" % (mag_r.common(rec).Volume, mag_t.common(tongue).Volume))
print("RESULT magnet gap (plastic+air) = %.2f mm; tongue head clears receiver top by %.2f mm" % (2 * SKIN + END_GAP, Z_T1 - RZ))
