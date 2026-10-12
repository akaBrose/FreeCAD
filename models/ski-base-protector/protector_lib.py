"""Shared parametric builder for the snowboard and ski base protectors. Units: mm.

Coordinates: X along the board (+X = tip), Y across, Z up. The board/ski base sits on the plane Z=0 and
the protector is built BELOW it (negative Z):

    z = LIP_H ........ top of the edge-guard lip (liner + skin wrap the sidewalls up to here)
    z = 0 ............ base of the board rests here (on the edge shelf)
    z = -LINER_T ..... bottom of the liner (shock-absorbing insert)
    z = -LINER_T-SKIN_T  bottom of the flexible skin (TPU/TPE backing)
    below that ....... overlapping hard scale plates, riveted to the skin by a stud each

Parts: Liner (soft insert), Skin (flexible backing), Scales (hard plates, one compound).
"""
import math
import os
import shutil
import zipfile

import FreeCAD as App
import Part
from FreeCAD import Vector, Placement, Rotation


# ---------------------------------------------------------------- 2D helpers
def profile_pts(length, tip, waist, tail, cap, step=12.0, cap_steps=18):
    """Closed outline (list of (x, y)) of a board/ski: parabolic sidecut + elliptical tip/tail caps.

    tip/waist/tail are the full widths at the end of the sidecut, centre and start of the sidecut.
    """
    lw = length - 2 * cap
    b = (tip / 2 - tail / 2) / lw
    c = (tip / 2 + tail / 2 - waist) * 2 / lw ** 2

    def quad(x):
        return waist / 2 + b * x + c * x * x

    upper = []
    for k in range(cap_steps + 1):                      # tail cap, apex -> shoulder
        th = math.pi / 2 * k / cap_steps
        upper.append((-lw / 2 - cap * math.cos(th), quad(-lw / 2) * math.sin(th)))
    n = max(1, int(lw / step))
    for k in range(1, n):
        x = -lw / 2 + lw * k / n
        upper.append((x, quad(x)))
    for k in range(cap_steps + 1):                      # tip cap, shoulder -> apex
        th = math.pi / 2 * (1 - k / cap_steps)
        upper.append((lw / 2 + cap * math.cos(th), quad(lw / 2) * math.sin(th)))
    lower = [(x, -y) for x, y in reversed(upper[1:-1])]
    return upper + lower


def face_from_pts(pts, dy=0.0):
    v = [Vector(x, y + dy, 0) for x, y in pts]
    return Part.Face(Part.makePolygon(v + [v[0]]))


def offset_face(face, d):
    r = face.makeOffset2D(d, join=0, fill=False, openResult=False, intersection=False)
    if r.Faces:
        return r.Faces[0]
    return Part.Face(r.Wires[0])


def prism(face, z0, z1):
    f = face.copy()
    f.translate(Vector(0, 0, z0))
    return f.extrude(Vector(0, 0, z1 - z0))


def point_in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


# ------------------------------------------------------------------ scales
def moved(shape, pos):
    """Placed copy that shares the underlying geometry (small files, fast)."""
    s = shape.copy(False)
    s.Placement = Placement(Vector(*pos), Rotation()).multiply(shape.Placement)
    return s


def make_scale(p):
    """One scale plate + its rivet stud, tilted so the trailing tip stands off the skin."""
    L, W, t = p["SCALE_L"], p["SCALE_W"], p["SCALE_T"]
    pts = [(0, -W / 2), (0.5 * L, -W / 2), (L, 0), (0.5 * L, W / 2), (0, W / 2)]
    v = [Vector(x, y, 0) for x, y in pts]
    plate = Part.Face(Part.makePolygon(v + [v[0]])).extrude(Vector(0, 0, -t))
    edges = [e for e in plate.Edges if all(abs(vx.Z + t) < 1e-6 for vx in e.Vertexes)]
    try:
        plate = plate.makeChamfer(p["SCALE_CHAMFER"], edges)       # domed / bevelled outer face
    except Exception:
        pass
    stud = Part.makeCylinder(p["STUD_R"], p["STUD_H"], Vector(p["STUD_X"], 0, 0), Vector(0, 0, 1))
    s = plate.fuse(stud).removeSplitter()
    s.rotate(Vector(0, 0, 0), Vector(0, 1, 0), p["SCALE_TILT"])
    return s


def tile_scales(p, tmpl, outer_poly, z0):
    """Staggered (hex-packed) scales, kept only where they fit inside outer_poly (inset by SCALE_MARGIN)."""
    L, W, P, G = p["SCALE_L"], p["SCALE_W"], p["SCALE_PITCH"], p["SCALE_GAP"]
    wp = W + G
    cth = math.cos(math.radians(p["SCALE_TILT"]))
    verts = [(0, -W / 2), (0.5 * L, -W / 2), (L, 0), (0.5 * L, W / 2), (0, W / 2)]
    # shrink test polygon by testing extra margin points around each vertex
    m = p["SCALE_MARGIN"]
    probes = [(0, 0)] + [(dx * m, dy * m) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
    xs = [q[0] for q in outer_poly]
    ys = [q[1] for q in outer_poly]
    i_min = int(math.floor((min(xs) - L) / P))
    i_max = int(math.ceil(max(xs) / P))
    j_max = int(math.ceil(max(ys) / wp)) + 1
    placed = []
    for i in range(i_min, i_max + 1):
        x0 = i * P
        for j in range(-j_max, j_max + 1):
            y0 = (j + 0.5 * (i % 2)) * wp
            ok = True
            for vx, vy in verts:
                for dx, dy in probes:
                    if not point_in_poly(x0 + vx * cth + dx, y0 + vy + dy, outer_poly):
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                placed.append(moved(tmpl, (x0, y0, z0)))
    return placed


# ---------------------------------------------------------------- checks
def check_scale_clearance(p, tmpl):
    P, wp = p["SCALE_PITCH"], p["SCALE_W"] + p["SCALE_GAP"]
    out = {}
    for name, d in [("next column (same y)", (P, 0, 0)), ("next column (+half row)", (P, wp / 2, 0)),
                    ("same column (+row)", (0, wp, 0)), ("two columns on", (2 * P, 0, 0))]:
        other = moved(tmpl, d)
        out[name] = (tmpl.common(other).Volume, tmpl.distToShape(other)[0])
    return out


# ------------------------------------------------------------ file helpers
def show_on_open(path, names):
    """Headless saves have no GUI data, so objects open hidden. Add GuiDocument.xml with Visibility on."""
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


# -------------------------------------------------------------------- build
def build(p, here):
    """p: parameter dict (see build.py). Returns dict of shapes."""
    name = p["NAME"]
    clear, wall, lip = p["CLEARANCE"], p["WALL"], p["LIP_H"]
    liner_t, skin_t = p["LINER_T"], p["SKIN_T"]

    # --- pockets (one per board/ski) -----------------------------------
    base_pts = profile_pts(p["LENGTH"], p["TIP_W"], p["WAIST_W"], p["TAIL_W"], p["CAP"])
    centers = p["CENTERS_Y"]
    gear_faces = [face_from_pts(base_pts, dy) for dy in centers]
    pocket_faces = [offset_face(f, clear) for f in gear_faces]
    if len(pocket_faces) == 1:
        merged = pocket_faces[0]
    else:
        half = p["LENGTH"] / 2 - p["CAP"] - 60
        yc = max(abs(c) for c in centers)
        bridge = face_from_pts([(-half, -yc), (half, -yc), (half, yc), (-half, yc)][:], 0.0)
        solid = prism(pocket_faces[0], 0, 1)
        for f in pocket_faces[1:] + [bridge]:
            solid = solid.fuse(prism(f, 0, 1))
        solid = solid.removeSplitter()
        merged = [f for f in solid.Faces if abs(f.BoundBox.ZMax) < 1e-6 and abs(f.BoundBox.ZMin) < 1e-6][0]
    liner_outer = offset_face(merged, wall)
    skin_outer = offset_face(liner_outer, skin_t)

    # --- liner ----------------------------------------------------------
    liner = prism(liner_outer, -liner_t, lip)
    for f in pocket_faces:
        liner = liner.cut(prism(f, 0, lip + 1))                        # board pocket / edge-guard lips
        liner = liner.cut(prism(offset_face(f, -p["SHELF_W"]), -p["RECESS"], 0.01))  # base relief
    # transverse flex-relief grooves under the floor (closed by the skin -> air cushions)
    xs_g = []
    x = -p["LENGTH"] / 2 + p["CAP"]
    while x < p["LENGTH"] / 2 - p["CAP"]:
        xs_g.append(x)
        x += p["GROOVE_PITCH"]
    ymax = max(q.y for q in liner_outer.OuterWire.discretize(Deflection=1.0)) + 1
    grooves = [Part.makeBox(p["GROOVE_W"], 2 * ymax, p["GROOVE_D"],
                            Vector(gx - p["GROOVE_W"] / 2, -ymax, -liner_t)) for gx in xs_g]
    liner = liner.cut(Part.Compound(grooves)).removeSplitter()

    # --- skin (flexible backing, wraps the liner up to the lip) ----------
    skin = prism(skin_outer, -liner_t - skin_t, lip).cut(prism(liner_outer, -liner_t, lip + 1))
    skin = skin.removeSplitter()

    # --- scales ---------------------------------------------------------
    tmpl = make_scale(p)
    z0 = -liner_t - skin_t
    poly = [(v.x, v.y) for v in liner_outer.OuterWire.discretize(Deflection=0.3)]
    scales = tile_scales(p, tmpl, poly, z0)
    scales_c = Part.Compound(scales)
    clearances = check_scale_clearance(p, tmpl)

    # --- reference gear (not part of the product) -------------------------
    ref = Part.Compound([prism(f, 0, p["GEAR_T"]) for f in gear_faces])

    # --- document ---------------------------------------------------------
    doc = App.newDocument(name)
    objs = {}
    for label, shp in [("Liner", liner), ("Skin", skin), ("Scales", scales_c), ("Gear_Reference", ref)]:
        o = doc.addObject("Part::Feature", label)
        o.Shape = shp
        objs[label] = o
    doc.recompute()
    fc = os.path.join(here, name + ".FCStd")
    doc.saveAs(fc)
    show_on_open(fc, ["Liner", "Skin", "Scales"])           # reference gear opens hidden

    import Mesh
    parts = [objs["Liner"], objs["Skin"], objs["Scales"]]
    for o in parts:
        Part.export([o], os.path.join(here, "%s-%s.step" % (name, o.Label.lower())))
        Mesh.export([o], os.path.join(here, "%s-%s.stl" % (name, o.Label.lower())))
    Part.export(parts, os.path.join(here, name + "-assembled.step"))

    # --- report -----------------------------------------------------------
    bb = Part.Compound([liner, skin, scales_c]).BoundBox
    print("=== %s ===" % name)
    print("scales: %d | liner vol %.0f mm3 valid=%s | skin vol %.0f valid=%s" %
          (len(scales), liner.Volume, liner.isValid(), skin.Volume, skin.isValid()))
    print("bbox: X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  (size %.0f x %.0f x %.1f)" %
          (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, bb.XLength, bb.YLength, bb.ZLength))
    for k, (vol, dist) in clearances.items():
        print("scale clearance vs %-26s overlap vol %.4f mm3, min gap %.2f mm" % (k, vol, dist))
    return {"liner": liner, "skin": skin, "scales": scales_c, "ref": ref}
