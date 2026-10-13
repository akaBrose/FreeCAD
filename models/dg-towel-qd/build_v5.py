"""Disc golf towel quick-detach v5 - flat velcro plate with a curved horn for a 1" steel grommet. Units: mm.

Model orientation = print orientation: flat back (velcro) face on the bed at z=0, +Z outward from the bag, +Y UP on the bag.
The horn is a tapered circular section lofted along a circular arc: near-1" diameter where it meets the plate, blunt
rounded tip. It leaves the plate steeply (close to the plate normal, tilted up) and curves upward, so the tip points up
and out. The grommet hangs around the horn base, flat on the plate, pulled on by magnets in the plate face.
Stow: swing the ring onto the horn, it slides down to the base. Release: pull the lanyard up and out along the tip.
"""
import math, os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
PLATE_W, PLATE_H, PLATE_T, PLATE_R = 45.0, 65.0, 3.0, 4.0
Y0 = 26.0                      # horn axis crosses the plate front at this height (ring hangs centred here)
R_BASE, R_TIP = 11.5, 3.5      # horn radius at the plate (Ø23, under the 25.4 hole) and at the blunt tip (Ø7)
L = 22.0                       # horn length along its curved axis (short)
PHI0, SWEEP = 20.0, 40.0       # tilt from the plate normal (toward up) where it leaves the plate, and extra curve to the tip
S_BACK = 8.0                   # straight extension behind the plate front so the foot is fully buried (clipped at the back)
N_SEC = 10
GROM_ID, GROM_OD, GROM_T = 25.4, 38.0, 2.5    # reference ring (OD / thickness assumed - measure yours)
MAG_N, MAG_D, MAG_T, MAG_R = 4, 6.0, 2.0, 15.8  # N52 discs in the plate face around the horn
MAG_FIT, MAG_RECESS = 0.1, 0.2

# --- Horn axis: circular arc in the Y-Z plane. phi = angle of the tangent from +Z toward +Y ---
R_PATH = L / math.radians(SWEEP)
phi0 = math.radians(PHI0)
S = V(0, Y0, PLATE_T)
Cc = S - V(0, -math.cos(phi0), math.sin(phi0)) * R_PATH
def phi(s): return phi0 + s / R_PATH
def p(s):  return Cc + V(0, -math.cos(phi(s)), math.sin(phi(s))) * R_PATH
def t(s):  return V(0, math.sin(phi(s)), math.cos(phi(s)))
def r(s):  return R_BASE + (R_TIP - R_BASE) * (s / L)

secs = [Part.Wire(Part.makeCircle(r(s), p(s), t(s))) for s in [L * i / (N_SEC - 1) for i in range(N_SEC)]]
horn = Part.makeLoft(secs, True, False)
horn = horn.fuse(Part.makeSphere(R_TIP, p(L)))
horn = horn.fuse(Part.makeCylinder(R_BASE, S_BACK + 0.3, p(0) - t(0) * S_BACK, t(0)))
horn = horn.common(Part.makeBox(200, 200, 200, V(-100, -100, 0)))       # flat back

# --- Plate ---
plate = Part.makeBox(PLATE_W, PLATE_H, PLATE_T, V(-PLATE_W / 2, 0, 0))
plate = plate.makeFillet(PLATE_R, [e for e in plate.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1e-6])
body = plate.fuse(horn).removeSplitter()

# --- Magnet pockets, open to the plate front (press-fit + glue, recessed) ---
pk_d, pk_h = MAG_D + MAG_FIT, MAG_T + MAG_RECESS
pos = [V(MAG_R * math.cos(math.radians(360.0 / MAG_N * i + 45)), Y0 + MAG_R * math.sin(math.radians(360.0 / MAG_N * i + 45)), PLATE_T)
       for i in range(MAG_N)]
for q in pos:
    body = body.cut(Part.makeCylinder(pk_d / 2, pk_h + 2, q - V(0, 0, pk_h)))

# --- Reference parts (not printed): ring flat on the plate around the horn, magnets ---
ring = Part.makeCylinder(GROM_OD / 2, GROM_T, V(0, Y0 + 0.6, PLATE_T)).cut(Part.makeCylinder(GROM_ID / 2, GROM_T + 2, V(0, Y0 + 0.6, PLATE_T - 1)))
mags = [Part.makeCylinder(MAG_D / 2, MAG_T, q - V(0, 0, pk_h - 0.1)) for q in pos]

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
doc = App.newDocument("DGTowelQDv5")
objs = {}
for n, s in [("Base", body), ("Grommet_ref", ring)] + [("Magnet%d" % i, m) for i, m in enumerate(mags)]:
    o = doc.addObject("Part::Feature", n)
    o.Shape = s
    objs[n] = o
doc.recompute()
fc = os.path.join(here, "dg-towel-qd-v5.FCStd")
doc.saveAs(fc)
show_on_open(fc, list(objs))
import MeshPart, Mesh
Mesh.Mesh(MeshPart.meshFromShape(Shape=body, LinearDeflection=0.03, AngularDeflection=0.15)).write(os.path.join(here, "dg-towel-qd-v5-base.stl"))
Part.export([objs["Base"]], os.path.join(here, "dg-towel-qd-v5-base.step"))

bb = body.BoundBox
tip = p(L)
print("RESULT base valid=%s solids=%d vol=%.0f bbox=%s" % (body.isValid(), len(body.Solids), body.Volume, bb))
print("RESULT ring/horn interference=%.3f mm3; magnets in solid=%s; magnet floor=%.2f mm" % (
    ring.common(body).Volume, [round(m.common(body).Volume, 3) for m in mags], PLATE_T - pk_h))
print("RESULT horn: tip at y=%.1f z=%.1f (protrudes %.1f from the bag), tip tangent %.0f deg from the plate normal, taper half-angle %.0f deg, max underside overhang ~%.0f deg" % (
    tip.y, tip.z + R_TIP, bb.ZMax, PHI0 + SWEEP, math.degrees(math.atan((R_BASE - R_TIP) / L)), PHI0 + SWEEP - math.degrees(math.atan((R_BASE - R_TIP) / L))))
print("RESULT ring footprint y %.1f..%.1f on a %.0f-high plate; horn base Ø%.1f vs hole Ø%.1f" % (Y0 - GROM_OD / 2, Y0 + GROM_OD / 2, PLATE_H, 2 * R_BASE, GROM_ID))
