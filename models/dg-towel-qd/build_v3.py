"""Disc golf towel quick-detach v3 - velcro base with an angled magnetic peg for a 1" steel grommet. Units: mm.

Print orientation = model orientation: back (velcro) face on the bed at z=0, +Z is outward from the bag,
+Y is UP on the bag. The peg axis tilts from the plate normal toward +Y, so on the bag it points up and
outward: gravity slides the grommet down the peg onto the magnet seat; release = lift the grommet up and out
along the peg axis. A plain round stem (no head) keeps it printable without supports; a small bead adds a click.
"""
import math, os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
PLATE_W, PLATE_H, PLATE_T = 70.0, 75.0, 4.0     # X width, Y height (up on bag), thickness
PLATE_R = 6.0                                    # plate corner radius
VEL_W, VEL_H, VEL_DEPTH = 64.0, 69.0, 1.2        # velcro recess on the back (leaves a 3 mm rim, pad stands ~0.3-0.8 proud)
ANGLE = 35.0                                     # peg tilt from the plate normal, toward up
Y0 = 36.0                                        # peg axis crosses the plate front at this height
SEAT_D, SEAT_OFFSET = 42.0, 18.0                 # seat pedestal diameter, seat distance along axis from the plate front
STEM_D, STEM_LEN = 18.0, 17.0                    # stem sits well inside the 1" (25.4) grommet hole
TIP_CHAMFER = 3.0
BEAD_AT, BEAD_H, BEAD_LEN = 10.0, 0.8, 0.8       # click bead (radius +BEAD_H), distance from seat
GROM_ID, GROM_OD, GROM_T = 25.4, 38.0, 2.5       # reference ring only (OD/thickness assumed - measure yours)
MAG_N, MAG_D, MAG_T, MAG_R = 4, 5.0, 3.0, 16.0   # N52 discs on a circle around the stem
MAG_FIT, MAG_RECESS = 0.1, 0.2                   # pocket oversize (press fit + glue); magnet sits this far below the seat face

# --- Geometry helpers ---
th = math.radians(ANGLE)
a = V(0, math.sin(th), math.cos(th))             # peg axis (unit)
e1, e2 = V(1, 0, 0), V(0, math.cos(th), -math.sin(th))   # in-seat-plane axes
P0 = V(0, Y0, PLATE_T)                           # axis point on the plate front
C = P0 + a * SEAT_OFFSET                         # seat face centre

def cyl(r, h, base, d): return Part.makeCylinder(r, h, base, d)

# --- Plate ---
plate = Part.makeBox(PLATE_W, PLATE_H, PLATE_T, V(-PLATE_W / 2, 0, 0))
plate = plate.makeFillet(PLATE_R, [e for e in plate.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6])

# --- Seat pedestal (tilted cylinder, clipped to z >= 0 so it never pokes through the back) ---
ped = cyl(SEAT_D / 2, 25 + SEAT_OFFSET, P0 - a * 25, a)
ped = ped.common(Part.makeBox(200, 200, 200, V(-100, -50, 0)))
body = plate.fuse(ped)

# --- Stem with lead-in tip and click bead ---
r = STEM_D / 2
stem = cyl(r, STEM_LEN - TIP_CHAMFER, C, a)
stem = stem.fuse(Part.makeCone(r, r - TIP_CHAMFER, TIP_CHAMFER, C + a * (STEM_LEN - TIP_CHAMFER), a))
stem = stem.fuse(Part.makeCone(r, r + BEAD_H, BEAD_LEN, C + a * BEAD_AT, a))
stem = stem.fuse(Part.makeCone(r + BEAD_H, r, BEAD_LEN, C + a * (BEAD_AT + BEAD_LEN), a))
body = body.fuse(stem).removeSplitter()

# --- Magnet pockets (open to the seat face; press-fit and glue, magnet recessed) ---
pk_d, pk_h = MAG_D + MAG_FIT, MAG_T + MAG_RECESS
pockets = []
for i in range(MAG_N):
    ph = math.radians(360.0 / MAG_N * i + 45.0)
    pos = C + (e1 * math.cos(ph) + e2 * math.sin(ph)) * MAG_R
    pockets.append(pos)
    body = body.cut(cyl(pk_d / 2, pk_h + 2, pos - a * pk_h, a))

# --- Velcro recess on the back ---
body = body.cut(Part.makeBox(VEL_W, VEL_H, VEL_DEPTH, V(-VEL_W / 2, (PLATE_H - VEL_H) / 2, 0)))

# --- Reference parts (not printed): steel grommet seated on the magnets, and the magnets ---
ring = cyl(GROM_OD / 2, GROM_T, C, a).cut(cyl(GROM_ID / 2, GROM_T + 2, C - a, a))
mags = [cyl(MAG_D / 2, MAG_T, p - a * pk_h + a * 0.1, a) for p in pockets]

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
doc = App.newDocument("DGTowelQDv3")
items = [("Base", body), ("Grommet_ref", ring)] + [("Magnet%d" % i, m) for i, m in enumerate(mags)]
objs = {}
for n, s in items:
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    objs[n] = o
doc.recompute()
fc = os.path.join(here, "dg-towel-qd-v3.FCStd")
doc.saveAs(fc)
show_on_open(fc, list(objs))
import MeshPart, Mesh
Mesh.Mesh(MeshPart.meshFromShape(Shape=body, LinearDeflection=0.03, AngularDeflection=0.15)).write(os.path.join(here, "dg-towel-qd-v3-base.stl"))
Part.export([objs["Base"]], os.path.join(here, "dg-towel-qd-v3-base.step"))

bb = body.BoundBox
print("RESULT base valid=%s solids=%d vol=%.0f mm3 bbox=%s" % (body.isValid(), len(body.Solids), body.Volume, bb))
print("RESULT grommet/base interference=%.4f mm3; magnets inside solid=%s" % (ring.common(body).Volume, [round(m.common(body).Volume, 3) for m in mags]))
print("RESULT seat upper-rim height above plate front=%.1f, lower-rim=%.1f, total protrusion=%.1f" % (
    SEAT_OFFSET * a.z - (SEAT_D / 2) * math.sin(th), SEAT_OFFSET * a.z + (SEAT_D / 2) * math.sin(th), bb.ZMax - PLATE_T))
print("RESULT magnet gap to hole edge: pocket inner edge r=%.1f vs grommet hole r=%.1f; outer edge r=%.1f vs seat r=%.1f vs grommet r=%.1f" % (
    MAG_R - pk_d / 2, GROM_ID / 2, MAG_R + pk_d / 2, SEAT_D / 2, GROM_OD / 2))
