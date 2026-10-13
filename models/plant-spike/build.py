"""Plant Spike - hollow spike: straight shaft, curved tapering section, blunt tip, drain holes (rounded-square). Units: mm.

Path (from the original Plant Spike sketch): a straight run up +Y, then a tangent arc
ending at (ARC_END_X, ARC_END_Y). Open end (hollow) is at the origin; tip at the far end.
"""
import math
import os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
SCALE = 0.70              # overall size vs the original v1 (1.0 = 38 mm OD, 432 mm long). Wall, joint gap and
                          # joint overlap stay fixed so the print keeps the same wall thickness
STRAIGHT_LEN = 150.0 * SCALE      # straight shaft length along +Y
ARC_END_X = 120.0 * SCALE         # arc end point (from original sketch)
ARC_END_Y = 424.95454 * SCALE     # arc end point (from original sketch)
OD_SHAFT = 38.0 * SCALE           # outer diameter of straight shaft and of the curve where it meets the shaft
OD_TIP = 15.0 * SCALE             # outer diameter at end of taper, right before the blunt dome begins
TIP_LEN = 24.0 * SCALE            # length of the point past the end of the taper (along the path)
TIP_NOSE_R = 2.5 * SCALE          # radius of curvature of the blunt end (5 mm diameter equivalent)
WALL = 2.0                # wall thickness
HOLE_SIDE = 9.0 * SCALE           # square hole side length at the start of the curve (full diameter)
HOLE_CORNER_FRAC = 0.2    # corner radius as a fraction of the side length
HOLE_RINGS = 13           # rings of holes along the curved section
HOLES_PER_RING = 6        # holes around each ring (alternate rings are staggered)
HOLE_T_START = 0.1446     # fraction along curved section where holes begin (first row dropped to clear the joint)
HOLE_T_END = 0.92         # ... and end (keep clear of the tip)
JOINT_LEN = 12.0          # minimum lap-joint overlap length, measured along the path
CUT_ANGLE_DEG = 23.6      # tilt of the cut plane; the curve piece prints tilted back by this much (23.6 = half the sweep, lean balanced +/-)
JOINT_CLEAR = 0.2         # radial bond gap between spigot and socket (ABS slurry / epoxy)
HOLE_ARC_DEG = 360.0      # angular spread of holes around the circumference (360 = all round)

# --- Path geometry ---
dx, dy = ARC_END_X, ARC_END_Y - STRAIGHT_LEN
R = (dx * dx + dy * dy) / (2 * dx)              # arc radius (tangent to the straight run)
THETA = math.atan2(dy, R - dx)                  # arc sweep
C = V(R, STRAIGHT_LEN, 0)                       # arc centre
Z = V(0, 0, 1)

def pt(th): return C + V(-R * math.cos(th), R * math.sin(th), 0)
def tan(th): return V(math.sin(th), math.cos(th), 0)
def nrm(th): return V(math.cos(th), -math.sin(th), 0)   # in-plane, points away from the arc centre

def circle(th, r):
    return Part.Wire(Part.Circle(pt(th), tan(th), r).toShape())

def spine(th_end=THETA):
    arc = Part.ArcOfCircle(Part.Circle(C, Z, R), math.pi - th_end, math.pi).toShape()
    return Part.Wire(arc)

def taper(r_start, r_end, th_end=THETA):
    ps = Part.BRepOffsetAPI.MakePipeShell(spine(th_end))
    ps.setFrenetMode(True)
    ps.add(circle(0, r_start))
    ps.add(circle(th_end, r_end))
    ps.build()
    ps.makeSolid()
    return ps.shape()

def r_at(t, r0, r1): return r0 + (r1 - r0) * t

r0, r1 = OD_SHAFT / 2, OD_TIP / 2

# --- Outer solid: shaft + tapered curve + domed tip ---
shaft = Part.makeCylinder(r0, STRAIGHT_LEN, V(0, 0, 0), V(0, 1, 0))
# Tip: one smooth revolved profile (cubic Bezier) that starts tangent to the taper (no kink) and curves into a blunt nose.
gamma = math.atan((r0 - r1) / (R * THETA))                 # taper half-angle at the join
a_len = 0.5 * TIP_LEN
v2x = TIP_LEN - a_len * math.cos(gamma)
b_nose = math.sqrt(TIP_NOSE_R * v2x / 1.5)                 # sets the curvature radius at the nose
# profile in (radius = X, axial = Y); axial runs along the path tangent at the taper end
bez = Part.BezierCurve()
bez.setPoles([V(r1, 0, 0),
              V(r1 - a_len * math.sin(gamma), a_len * math.cos(gamma), 0),
              V(b_nose, TIP_LEN, 0),
              V(0, TIP_LEN, 0)])
prof = Part.Wire([bez.toShape(), Part.makeLine(V(0, TIP_LEN, 0), V(0, 0, 0)), Part.makeLine(V(0, 0, 0), V(r1, 0, 0))])
tip = Part.Face(prof).revolve(V(0, 0, 0), V(0, 1, 0), 360)
tip.Placement = App.Placement(pt(THETA), App.Rotation(Z, -math.degrees(THETA)))
outer = shaft.fuse([taper(r0, r1), tip]).removeSplitter()

# --- Cavity: open at the origin end, closes at the end of the taper (tip stays solid) ---
cav_shaft = Part.makeCylinder(r0 - WALL, STRAIGHT_LEN + 1, V(0, -1, 0), V(0, 1, 0))
cavity = cav_shaft.fuse(taper(r0 - WALL, r1 - WALL)).removeSplitter()
body = outer.cut(cavity)

# --- Holes: rounded-square prisms from just inside the bore out through the wall ---
holes = []
for i in range(HOLE_RINGS):
    t = HOLE_T_START + (HOLE_T_END - HOLE_T_START) * i / max(HOLE_RINGS - 1, 1)
    th = THETA * t
    r = r_at(t, r0, r1)
    side = HOLE_SIDE * r / r0                  # shrinks in proportion to the spike diameter
    stagger = (i % 2) * 0.5
    for j in range(HOLES_PER_RING):
        phi = math.radians(HOLE_ARC_DEG) * (j + stagger) / HOLES_PER_RING
        d = nrm(th) * math.cos(phi) + Z * math.sin(phi)     # radial direction (hole axis)
        T = tan(th)
        B = d.cross(T)
        # square turned 45 deg so corners point along the path (T) and around the spike (B)
        u, w = (T - B) * (1 / math.sqrt(2)), (T + B) * (1 / math.sqrt(2))
        rho0 = max(r - WALL - 0.5, 0.3)          # start just inside the bore (cutters sharing the axis break the boolean)
        box = Part.makeBox(side, side, r + 3 - rho0, V(-side / 2, -side / 2, rho0))
        edges = [e for e in box.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99]
        box = box.makeFillet(HOLE_CORNER_FRAC * side, edges)
        m = App.Matrix(u.x, w.x, d.x, pt(th).x,
                       u.y, w.y, d.y, pt(th).y,
                       u.z, w.z, d.z, pt(th).z,
                       0, 0, 0, 1)
        box.transformShape(m)
        holes.append(box)
body = body.cut(Part.makeCompound(holes))
body = body.removeSplitter()

# --- Split into two printable pieces with a lap joint on a tilted cut plane at the start of the curve ---
# The cut plane passes through the start of the curve (0, STRAIGHT_LEN) and is tilted CUT_ANGLE_DEG toward the curve
# side, so when the curve piece sits with that plane on the bed it leans back and the tip lean is reduced by that angle.
# The lap joint follows the path: it runs from the plane to arc angle TH_J (>= JOINT_LEN past the highest point of the cut).
# Shaft piece: everything below the plane plus a spigot (outer part of the wall removed) up to TH_J.
# Curve piece: everything above the plane, with a matching socket (inner part of the wall removed) up to TH_J.
ALPHA = math.radians(CUT_ANGLE_DEG)
SPLIT_Y = STRAIGHT_LEN
r_in = r0 - WALL
half = WALL * 0.45                                   # each side of the joint keeps ~0.9 mm of wall
TH_J = (r0 * math.tan(ALPHA) + JOINT_LEN) / R        # joint end (arc angle)
def r_th(th): return r_at(th / THETA, r0, r1)        # outer radius along the path
big = 1000.0
def ycyl(r, y0, y1): return Part.makeCylinder(r, y1 - y0, V(0, y0, 0), V(0, 1, 0))
def halfspace(side):                                  # side=+1 above the cut plane, -1 below
    b = Part.makeBox(big, big, big, V(-big / 2, 0 if side > 0 else -big, -big / 2))
    b.Placement = App.Placement(V(0, SPLIT_Y, 0), App.Rotation(Z, -CUT_ANGLE_DEG))
    return b
above, below = halfspace(+1), halfspace(-1)
def joint_tube(extra):                                # tube of radius (r_in + half + extra), straight part + along the arc
    ra, rb = r_in + half + extra, r_th(TH_J) - WALL + half + extra
    return ycyl(ra, STRAIGHT_LEN - 40, STRAIGHT_LEN).fuse(taper(ra, rb, TH_J)).removeSplitter()

spigot = body.common(joint_tube(0))
shaft_piece = body.common(below).fuse(spigot).removeSplitter()
curve_piece = body.common(above).cut(joint_tube(JOINT_CLEAR)).removeSplitter()

# Print orientation: both stand upright with the seam/open end on the bed, no supports needed.
def to_print(shape, tilt_deg, ox, oy):
    s = shape.copy()
    s.Placement = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), 90) * App.Rotation(Z, tilt_deg))  # Y -> Z
    bb = s.optimalBoundingBox(True, False)
    s.translate(V(ox - bb.XMin, oy - bb.YMin, -bb.ZMin))
    return s
print_curve = to_print(curve_piece, CUT_ANGLE_DEG, 0, 0)
cbb = print_curve.optimalBoundingBox(True, False)
print_shaft = to_print(shaft_piece, 0, cbb.XMax + 25, 0)

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
doc = App.newDocument("PlantSpike")
parts = {"Shaft": print_shaft, "Curve": print_curve}
objs = {}
for name, shp in parts.items():
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    objs[name] = o
doc.recompute()
doc.saveAs(os.path.join(here, "plant-spike.FCStd"))
show_on_open(os.path.join(here, "plant-spike.FCStd"), list(parts))

import MeshPart, Mesh
for name, shp in parts.items():
    Part.export([objs[name]], os.path.join(here, "plant-spike-%s.step" % name.lower()))
    Mesh.Mesh(MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.03, AngularDeflection=0.15)).write(
        os.path.join(here, "plant-spike-%s.stl" % name.lower()))
Mesh.Mesh(MeshPart.meshFromShape(Shape=Part.makeCompound(list(parts.values())), LinearDeflection=0.03, AngularDeflection=0.15)).write(
    os.path.join(here, "plant-spike.stl"))      # both pieces, laid out as printed
asm = doc.addObject("Part::Feature", "Assembled")
asm.Shape = body
Part.export([asm], os.path.join(here, "plant-spike-assembled.step"))
doc.removeObject("Assembled")

for name, shp in parts.items():
    print("RESULT %s valid=%s solids=%d volume=%.0f mm3 bbox=%s" % (name, shp.isValid(), len(shp.Solids), shp.Volume, shp.BoundBox))
_ov = shaft_piece.common(curve_piece).Volume
print("RESULT interference=%.3f mm3  joint-gap-volume=%.0f mm3  split_y=%.1f" % (
    _ov, body.Volume - shaft_piece.Volume - curve_piece.Volume, SPLIT_Y))
print("RESULT joint ends %.1f mm along path; tip lean %.1f deg (+%.1f taper), start lean -%.1f deg" % (TH_J * R, math.degrees(THETA) - CUT_ANGLE_DEG, math.degrees(math.atan((r0 - r1) / (R * THETA))), CUT_ANGLE_DEG))
print("RESULT tip: smooth profile, %.1f mm past the taper, nose radius ~%.1f mm, tangent to the taper (%.2f deg)" % (TIP_LEN, TIP_NOSE_R, math.degrees(gamma)))
print("RESULT holes=%d joint: spigot r=%.2f socket r=%.2f" % (len(holes), r_in + half, r_in + half + JOINT_CLEAR))
