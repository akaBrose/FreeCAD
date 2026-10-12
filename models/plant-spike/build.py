"""Plant Spike - hollow spike: straight shaft, curved tapering section, blunt tip, drain holes. Units: mm.

Path (from the original Plant Spike sketch): a straight run up +Y, then a tangent arc
ending at (ARC_END_X, ARC_END_Y). Open end (hollow) is at the origin; tip at the far end.
"""
import math
import os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
STRAIGHT_LEN = 150.0      # straight shaft length along +Y
ARC_END_X = 120.0         # arc end point (from original sketch)
ARC_END_Y = 424.95454     # arc end point (from original sketch)
OD_SHAFT = 38.0           # outer diameter of straight shaft and of the curve where it meets the shaft
OD_TIP = 15.0             # outer diameter at end of taper, right before the blunt dome begins
WALL = 2.0                # wall thickness
HOLE_D = 2.0              # drain hole diameter
HOLE_RINGS = 12           # rings of holes along the curved section
HOLES_PER_RING = 6        # holes around each ring (alternate rings are staggered)
HOLE_T_START = 0.08       # fraction along curved section where holes begin
HOLE_T_END = 0.85         # ... and end (keep clear of the tip)
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

def spine():
    arc = Part.ArcOfCircle(Part.Circle(C, Z, R), math.pi - THETA, math.pi).toShape()
    return Part.Wire(arc)

def taper(r_start, r_end):
    ps = Part.BRepOffsetAPI.MakePipeShell(spine())
    ps.setFrenetMode(True)
    ps.add(circle(0, r_start))
    ps.add(circle(THETA, r_end))
    ps.build()
    ps.makeSolid()
    return ps.shape()

def r_at(t, r0, r1): return r0 + (r1 - r0) * t

r0, r1 = OD_SHAFT / 2, OD_TIP / 2

# --- Outer solid: shaft + tapered curve + domed tip ---
shaft = Part.makeCylinder(r0, STRAIGHT_LEN, V(0, 0, 0), V(0, 1, 0))
outer = shaft.fuse([taper(r0, r1), Part.makeSphere(r1, pt(THETA))]).removeSplitter()

# --- Cavity: open at the origin end, closes at the end of the taper (tip stays solid) ---
cav_shaft = Part.makeCylinder(r0 - WALL, STRAIGHT_LEN + 1, V(0, -1, 0), V(0, 1, 0))
cavity = cav_shaft.fuse(taper(r0 - WALL, r1 - WALL)).removeSplitter()
body = outer.cut(cavity)

# --- Holes: radial cylinders from the axis out through the wall ---
holes = []
for i in range(HOLE_RINGS):
    t = HOLE_T_START + (HOLE_T_END - HOLE_T_START) * i / max(HOLE_RINGS - 1, 1)
    th = THETA * t
    r = r_at(t, r0, r1)
    stagger = (i % 2) * 0.5
    for j in range(HOLES_PER_RING):
        # spread around the circumference (centred on the arc's outer side)
        phi = math.radians(HOLE_ARC_DEG) * (j + stagger) / HOLES_PER_RING
        d = nrm(th) * math.cos(phi) + Z * math.sin(phi)
        holes.append(Part.makeCylinder(HOLE_D / 2, r + 3, pt(th), d))
body = body.cut(Part.makeCompound(holes))
body = body.removeSplitter()

# --- Save / export ---
here = os.path.dirname(os.path.abspath(__file__))
doc = App.newDocument("PlantSpike")
obj = doc.addObject("Part::Feature", "PlantSpike")
obj.Shape = body
doc.recompute()
doc.saveAs(os.path.join(here, "plant-spike.FCStd"))
Part.export([obj], os.path.join(here, "plant-spike.step"))
import Mesh
Mesh.export([obj], os.path.join(here, "plant-spike.stl"))

print("RESULT valid=%s solids=%d volume=%.1f mm3 bbox=%s holes=%d R=%.2f sweep=%.1fdeg" % (
    body.isValid(), len(body.Solids), body.Volume, body.BoundBox, len(holes), R, math.degrees(THETA)))
