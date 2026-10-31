"""Skull Ashtray (concept A, "open skull") - parametric FreeCAD build script. Units: mm.

Top view is a frontal human skull (face looking straight up at you). One bowl follows the outline inside an
even-width rim, with a drafted wall and a large floor fillet. The face (orbits, nasal opening, teeth) is a black
inlay flush with the bowl floor; the body is white. U-notches in the rim hold cigarettes, joints and a cigar.

Axes: X = skull width, Y = chin (0) to crown (OVERALL_L), Z = up from the table (prints in this orientation).
"""
import math
import os
import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Parameters ---
OVERALL_W = 100.0        # skull width (limit 4 in = 101.6)
OVERALL_L = 150.0        # chin to crown (limit 6 in = 152.4)
HEIGHT = 38.0            # rim height above the table (limit 1.5 in = 38.1)
RIM = 8.0                # rim wall thickness at the top, constant all the way round
CAVITY_DEPTH = 30.0      # rim top to bowl floor (1.18 in; spec 1.00-1.25 in)
DRAFT_DEG = 3.0          # bowl wall leans out toward the top so ash tips out cleanly
FLOOR_FILLET = 10.0      # floor-to-wall radius (no corners for ash to pack into)
TOP_OUTER_R = 2.0        # rounding of the outer top edge
TOP_INNER_R = 1.5        # rounding of the inner top edge
BASE_CHAMFER = 0.8       # 45 deg chamfer on the bottom outer edge (elephant-foot relief)
INLAY_DEPTH = 1.5        # black face inlay thickness (vertical), flush with the bowl surface
TEETH_LINE = 1.6         # black line width of the teeth outlines (>= 2-3 extrusion lines)
NOTCH_EDGE_R = 1.0       # rounding on the notch edges
# Rests: (name, target point on the outline in sketch coords (x, y down from crown), diameter, depth below rim top)
RESTS = [
    ("cigar_crown", (0.0, 0.0), 22.0, 11.0),
    ("cigarette_L", (-38.0, 18.0), 9.0, 7.0),
    ("cigarette_R", (38.0, 18.0), 9.0, 7.0),
    ("joint_L", (-50.0, 50.0), 11.0, 8.0),
    ("joint_R", (50.0, 50.0), 11.0, 8.0),
]
SECTION_PTS = 72         # points per loft section

# --- Outline: right half of a frontal skull as cubic Beziers, sketch coords (x, y down from crown), 100 x 150 ---
RIGHT_HALF = [
    [(0, 0), (30, 0), (50, 18), (50, 45)],          # cranium vault
    [(50, 45), (50, 58), (46, 66), (44, 72)],       # parietal down to the temple
    [(44, 72), (47, 76), (49, 82), (48, 88)],       # zygomatic arch (cheekbone)
    [(48, 88), (46, 96), (36, 102), (31, 108)],     # under the cheekbone to the maxilla
    [(31, 108), (34, 114), (37, 120), (37, 128)],   # mandible ramus to the jaw angle
    [(37, 128), (36, 138), (26, 148), (0, 150)],    # jaw line to the chin
]


def sk(p):
    """sketch (x, y down) -> model (X, Y up from the chin)"""
    return V(p[0], OVERALL_L - p[1], 0)


def bez(pts, n):
    out = []
    for i in range(n):
        t = i / n
        a, b, c, d = pts
        out.append(tuple((1 - t) ** 3 * a[k] + 3 * (1 - t) ** 2 * t * b[k] + 3 * (1 - t) * t * t * c[k] + t ** 3 * d[k]
                         for k in range(2)))
    return out


def periodic(points):
    # uniform parameters: every section with the same point count gets the same knots, which keeps the loft light
    c = Part.BSplineCurve()
    c.interpolate(Points=points, PeriodicFlag=True, Parameters=[i / len(points) for i in range(len(points) + 1)])
    return Part.Wire([c.toShape()])


def resample(wire, n=SECTION_PTS):
    """Uniform arc-length points starting at the crown (max Y), counter-clockwise, as a periodic B-spline wire.
    Every loft section gets the same structure so the loft is clean."""
    if not isinstance(wire, Part.Wire):
        wire = max(wire.Wires, key=lambda w: w.Length)        # offsets come back as a generic shape
    pts = wire.discretize(Distance=0.2)
    if pts[0].distanceToPoint(pts[-1]) < 1e-6:
        pts = pts[:-1]
    area = sum(pts[i].x * pts[(i + 1) % len(pts)].y - pts[(i + 1) % len(pts)].x * pts[i].y for i in range(len(pts)))
    if area < 0:
        pts.reverse()
    top = max(range(len(pts)), key=lambda i: pts[i].y - 0.01 * abs(pts[i].x))
    pts = pts[top:] + pts[:top]
    pts.append(pts[0])
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + pts[i].distanceToPoint(pts[i - 1]))
    out, j = [], 0
    for k in range(n):
        s = cum[-1] * k / n
        while cum[j + 1] < s:
            j += 1
        f = (s - cum[j]) / max(cum[j + 1] - cum[j], 1e-9)
        out.append(pts[j] + (pts[j + 1] - pts[j]) * f)
    return periodic(out)


# master outline: sample the Beziers (right half crown->chin, mirrored chin->crown), fit a smooth periodic B-spline,
# then scale it to exactly OVERALL_W x OVERALL_L
half = []
for seg in RIGHT_HALF:
    half += bez(seg, 14)
half.append(RIGHT_HALF[-1][-1])
ring = [(-x, y) for (x, y) in half[1:-1]] + [(x, y) for (x, y) in reversed(half)]   # left side down, right side up
ring = ring[:-1]
raw = periodic([sk(p) for p in ring])
bb = raw.BoundBox
m = App.Matrix()
m.scale(OVERALL_W / bb.XLength, OVERALL_L / bb.YLength, 1)
raw = Part.Wire(raw.transformGeometry(m).Edges)
_p = resample(raw, 120).discretize(Number=120)[:-1]     # re-fit, then pin the fitted curve to the exact size
_x0, _x1 = min(p.x for p in _p), max(p.x for p in _p)
_y0, _y1 = min(p.y for p in _p), max(p.y for p in _p)
outline = periodic([V((p.x - (_x0 + _x1) / 2) * OVERALL_W / (_x1 - _x0), (p.y - _y0) * OVERALL_L / (_y1 - _y0), 0)
                    for p in _p])
outline_poly = Part.makePolygon(outline.discretize(Number=600) + [outline.discretize(Number=600)[0]])


def inset(d, z):
    # offset a dense polygon of the outline (OCC's B-spline offset fails past ~16 mm), then re-fit a smooth section
    w = outline_poly.makeOffset2D(-d, join=0, fill=False, openResult=False, intersection=False)
    s = resample(w)
    s.translate(V(0, 0, z))
    return s


# --- Body: extruded outline ---
outer = Part.Face(outline).extrude(V(0, 0, HEIGHT))

# --- Bowl: lofted sections. Wall inset grows by the draft toward the floor; the bottom R is a quarter circle ---
Z_FLOOR = HEIGHT - CAVITY_DEPTH
TD = math.tan(math.radians(DRAFT_DEG))
def wall_inset(z): return RIM + (HEIGHT - z) * TD
R = FLOOR_FILLET
wc = wall_inset(Z_FLOOR + R) + R
sections = []
for deg in (0, 12, 25, 38, 52, 66, 79, 90):
    phi = math.radians(deg)
    sections.append(inset(wc - R * math.sin(phi), Z_FLOOR + R * (1 - math.cos(phi))))
for z in (Z_FLOOR + R + 5, (Z_FLOOR + R + HEIGHT) / 2, HEIGHT - 3, HEIGHT, HEIGHT + 3):
    sections.append(inset(wall_inset(z), z))
cavity = Part.makeLoft(sections, True, False)
FLOOR_INSET = wc

body = outer.cut(cavity)
top_edges = [e for e in body.Edges if abs(e.BoundBox.ZMin - HEIGHT) < 1e-4 and abs(e.BoundBox.ZMax - HEIGHT) < 1e-4]
outer_top = max(top_edges, key=lambda e: e.Length)
inner_top = min(top_edges, key=lambda e: e.Length)
body = body.makeFillet(TOP_OUTER_R, [outer_top])
inner_top = [e for e in body.Edges if abs(e.BoundBox.ZMax - HEIGHT) < 1e-4 and abs(e.Length - inner_top.Length) < 0.5]
body = body.makeFillet(TOP_INNER_R, inner_top)
bottom = [e for e in body.Edges if e.BoundBox.ZMax < 1e-4]
body = body.makeChamfer(BASE_CHAMFER, bottom)

# --- Rests: U-notches square to the rim (the lit end hangs over the bowl) ---
oc = outline.Edges[0].Curve
notch_info = []
for name, target, dia, depth in RESTS:
    p = sk(target)
    u = oc.parameter(p)
    q = oc.value(u)
    t = oc.tangent(u)[0]
    nrm = V(-t.y, t.x, 0)                          # outline runs counter-clockwise, so this points inward
    r = dia / 2
    zc = HEIGHT - depth + r                        # U centre height
    L = RIM + 14
    cyl = Part.makeCylinder(r, L, V(0, 0, 0), V(1, 0, 0))
    box = Part.makeBox(L, dia, HEIGHT, V(0, -r, 0))
    tool = cyl.fuse(box).removeSplitter()
    tool.translate(V(-6, 0, zc))
    tool.transformShape(App.Matrix(nrm.x, t.x, 0, q.x, nrm.y, t.y, 0, q.y, 0, 0, 1, 0, 0, 0, 0, 1))
    body = body.cut(tool)
    notch_info.append((name, q, dia, HEIGHT - depth))
body = body.removeSplitter()

notch_edges = []
for e in body.Edges:
    c = e.BoundBox.Center
    for _, q, dia, zb in notch_info:
        if math.hypot(c.x - q.x, c.y - q.y) < RIM + dia and e.BoundBox.ZMax > zb + 0.5 and e.BoundBox.ZMin > zb - 0.01 \
                and e.BoundBox.ZMax > HEIGHT - dia - 3:
            notch_edges.append(e)
            break
try:
    body = body.makeFillet(NOTCH_EDGE_R, notch_edges)
    notch_fillet = "ok (%d edges)" % len(notch_edges)
except Exception as ex:                             # fall back to sharp notch edges rather than fail the build
    notch_fillet = "FAILED (%s) - notch edges left sharp" % ex

# --- Face inlay (black): orbits, nasal aperture, teeth. Sketch coords, mirrored about x = 0 ---
ORBIT_R = [(6, 71), (10, 65.5), (17, 63.5), (24, 64.5), (28.5, 68.5), (29.5, 75), (27, 82), (21, 86), (14, 86),
           (8.5, 82), (6, 77)]
NOSE = [(0, 89), (3.5, 92), (6, 97.5), (7.5, 103), (5.5, 107), (2, 107.5), (0, 105.5), (-2, 107.5), (-5.5, 107),
        (-7.5, 103), (-6, 97.5), (-3.5, 92)]
TEETH = dict(x=16.0, y0=111.0, y1=125.0, n=6, r=3.0)    # band half-width, top/bottom (sketch y), teeth per row


def blob(pts):
    return Part.Face(periodic([sk(p) for p in pts]))


def rrect(x0, y0, x1, y1, r):
    b = Part.makeBox(x1 - x0, y1 - y0, 1, V(x0, y0, 0))
    return b.makeFillet(r, [e for e in b.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99])


faces = [blob(ORBIT_R), blob([(-x, y) for (x, y) in ORBIT_R]), blob(NOSE)]
feat = Part.makeCompound(faces).extrude(V(0, 0, HEIGHT))
ty0, ty1 = OVERALL_L - TEETH["y1"], OVERALL_L - TEETH["y0"]   # model Y
tx = TEETH["x"]
band = rrect(-tx, ty0, tx, ty1, TEETH["r"])
lw = TEETH_LINE
inner = rrect(-tx + lw, ty0 + lw, tx - lw, ty1 - lw, max(TEETH["r"] - lw, 0.4))
teeth = band.cut(inner)
ym = (ty0 + ty1) / 2
lines = [Part.makeBox(2 * tx, lw, 1, V(-tx, ym - lw / 2, 0))]
for i in range(1, TEETH["n"]):
    x = -tx + 2 * tx * i / TEETH["n"]
    lines.append(Part.makeBox(lw, ty1 - ty0, 1, V(x - lw / 2, ty0, 0)))
teeth = teeth.fuse(band.common(Part.makeCompound(lines)))
teeth_prism = Part.makeCompound([f for f in teeth.Faces if abs(f.normalAt(0, 0).z + 1) < 1e-6]).extrude(V(0, 0, HEIGHT))
feat = feat.fuse(teeth_prism)
skin = body.common(cavity.translated(V(0, 0, -INLAY_DEPTH)))     # 1.5 mm layer under the bowl surface
inlay = skin.common(feat)
inlay = Part.makeCompound([s for s in inlay.Solids if s.Volume > 0.5]).removeSplitter()
white = body.cut(inlay).removeSplitter()

# --- Checks ---
import Mesh, MeshPart
def mesh(shp): return MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.03, AngularDeflection=0.2)
mw = mesh(white)
over = 0.0
for f in mw.Facets:
    n = V(*f.Normal)
    if n.z < -math.cos(math.radians(45)) - 1e-3 and min(p[2] for p in f.Points) > 0.05:
        over += f.Area
RIM_CHECK_Z = min(zb for *_, zb in notch_info) - 1          # just below the lowest notch, so the rim is a full ring
wires = sorted(body.slice(V(0, 0, 1), RIM_CHECK_Z), key=lambda w: w.Length)
rim_min = wires[-1].distToShape(wires[-2])[0]
bowl = cavity.common(Part.makeBox(300, 300, HEIGHT - Z_FLOOR, V(-150, -150, Z_FLOOR)))

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
doc = App.newDocument("SkullAshtray")
parts = {"Body_White": white, "Inlay_Black": inlay}
objs = {}
for name, shp in parts.items():
    o = doc.addObject("Part::Feature", name)
    o.Shape = shp
    objs[name] = o
doc.recompute()
fc = os.path.join(here, "skull-ashtray.FCStd")
doc.saveAs(fc)
show_on_open(fc, list(parts))

Part.export(list(objs.values()), os.path.join(here, "skull-ashtray.step"))
mi = mesh(inlay)
mw.write(os.path.join(here, "skull-ashtray-white.stl"))
mi.write(os.path.join(here, "skull-ashtray-black.stl"))
try:
    Mesh.export(list(objs.values()), os.path.join(here, "skull-ashtray.3mf"))
except Exception as ex:
    print("RESULT 3mf export failed:", ex)
mesh(body).write(os.path.join(here, "skull-ashtray-single-color.stl"))

bbw = white.BoundBox
print("RESULT white valid=%s solids=%d vol=%.0f mm3  inlay valid=%s solids=%d vol=%.0f mm3" % (
    white.isValid(), len(white.Solids), white.Volume, inlay.isValid(), len(inlay.Solids), inlay.Volume))
print("RESULT bbox %.2f x %.2f x %.2f mm (%.3f x %.3f x %.3f in)" % (
    bbw.XLength, bbw.YLength, bbw.ZLength, bbw.XLength / 25.4, bbw.YLength / 25.4, bbw.ZLength / 25.4))
print("RESULT cavity depth %.2f mm (%.3f in), floor %.1f mm thick, floor inset %.1f mm, bowl volume %.0f ml" % (
    HEIGHT - Z_FLOOR, (HEIGHT - Z_FLOOR) / 25.4, Z_FLOOR, FLOOR_INSET, bowl.Volume / 1000))
print("RESULT min rim thickness at z=%.0f: %.2f mm (expected %.2f with draft)" % (RIM_CHECK_Z, rim_min, wall_inset(RIM_CHECK_Z)))
print("RESULT downward overhang >45 deg area (excluding base): %.1f mm2" % over)
print("RESULT notch fillets:", notch_fillet)
for name, q, dia, zb in notch_info:
    print("RESULT rest %-12s dia %.0f  at (%.1f, %.1f)  bottom z=%.1f" % (name, dia, q.x, q.y, zb))
print("RESULT weight ~%.0f g in ABS (100%% infill), ~%.0f g PETG" % (body.Volume * 1.04e-3, body.Volume * 1.27e-3))
