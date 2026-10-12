"""Shared parametric builder for the snowboard and ski base protectors (v2). Units: mm.

Coordinates: X along the gear (+X = tip), Y across, Z up. The gear base sits on the plane Z=0 and the
rollable body is built BELOW it (negative Z):

    z = LIP_H ........... top of the (soft) edge-guard lip, V-notched so the body can roll
    z = 0 ............... gear base rests here (on the edge shelf)
    z = -LINER_T ........ bottom of the liner (thin shock-absorbing insert)
    z = -LINER_T-SKIN_T . bottom of the flexible skin (TPU/TPE backing, carries scales + strap tabs)
    below that .......... overlapping hard scale plates, one stud each into the skin

Rollable body = Liner + Skin + Scales (+ strap tabs). Roll it with the scales on the OUTSIDE.
Tip and tail caps are separate hard cups (shell) with a soft lining; they slide on over the ends of the gear
and are held by straps; the body stops short of them (CAP_LEN from each end).
Straps: webbing over the gear, through slotted tabs on both sides (body and caps).
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
    """Closed outline [(x, y)] of a board/ski: parabolic sidecut + elliptical tip/tail caps."""
    lw = length - 2 * cap
    b = (tip / 2 - tail / 2) / lw
    c = (tip / 2 + tail / 2 - waist) * 2 / lw ** 2

    def quad(x):
        return waist / 2 + b * x + c * x * x

    upper = []
    for k in range(cap_steps + 1):
        th = math.pi / 2 * k / cap_steps
        upper.append((-lw / 2 - cap * math.cos(th), quad(-lw / 2) * math.sin(th)))
    n = max(1, int(lw / step))
    for k in range(1, n):
        x = -lw / 2 + lw * k / n
        upper.append((x, quad(x)))
    for k in range(cap_steps + 1):
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


def union_prism(faces, z0, z1):
    s = prism(faces[0], z0, z1)
    for f in faces[1:]:
        s = s.fuse(prism(f, z0, z1))
    return s.removeSplitter() if len(faces) > 1 else s


def bottom_face(solid):
    zmin = solid.BoundBox.ZMin
    fs = [f for f in solid.Faces if abs(f.BoundBox.ZMax - zmin) < 1e-6 and abs(f.BoundBox.ZMin - zmin) < 1e-6]
    return max(fs, key=lambda f: f.Area)


def xbox(x0, x1, z0, z1, y=2000.0):
    a, b = min(x0, x1), max(x0, x1)
    return Part.makeBox(b - a, 2 * y, z1 - z0, Vector(a, -y, z0))


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


def y_extent(poly, x):
    """(ymin, ymax) of the polygon along the vertical line at x."""
    ys = []
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (x1 <= x < x2) or (x2 <= x < x1):
            ys.append(y1 + (y2 - y1) * (x - x1) / (x2 - x1))
    return min(ys), max(ys)


def poly_of(face):
    return [(v.x, v.y) for v in face.OuterWire.discretize(Deflection=0.3)]


# ------------------------------------------------------------------ scales
def moved(shape, pos):
    """Placed copy sharing the underlying geometry (small files, fast)."""
    s = shape.copy(False)
    s.Placement = Placement(Vector(*pos), Rotation()).multiply(shape.Placement)
    return s


def make_scale(p):
    """One scale plate + its stud, tilted so the trailing tip stands off the skin."""
    L, W, t = p["SCALE_L"], p["SCALE_W"], p["SCALE_T"]
    pts = [(0, -W / 2), (0.5 * L, -W / 2), (L, 0), (0.5 * L, W / 2), (0, W / 2)]
    v = [Vector(x, y, 0) for x, y in pts]
    plate = Part.Face(Part.makePolygon(v + [v[0]])).extrude(Vector(0, 0, -t))
    edges = [e for e in plate.Edges if all(abs(vx.Z + t) < 1e-6 for vx in e.Vertexes)]
    try:
        plate = plate.makeChamfer(p["SCALE_CHAMFER"], edges)
    except Exception:
        pass
    stud = Part.makeCylinder(p["STUD_R"], p["STUD_H"], Vector(p["STUD_X"], 0, 0), Vector(0, 0, 1))
    s = plate.fuse(stud).removeSplitter()
    s.rotate(Vector(0, 0, 0), Vector(0, 1, 0), p["SCALE_TILT"])
    return s


def tile_scales(p, tmpl, outer_poly, z0, xlim):
    """Staggered (hex-packed) scales kept where they fit inside outer_poly (inset) and |x| <= xlim."""
    L, W, P, G = p["SCALE_L"], p["SCALE_W"], p["SCALE_PITCH"], p["SCALE_GAP"]
    wp = W + G
    cth = math.cos(math.radians(p["SCALE_TILT"]))
    verts = [(0, -W / 2), (0.5 * L, -W / 2), (L, 0), (0.5 * L, W / 2), (0, W / 2)]
    m = p["SCALE_MARGIN"]
    probes = [(0, 0)] + [(dx * m, dy * m) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
    ys = [q[1] for q in outer_poly]
    i_min = int(math.floor(-xlim / P)) - 1
    i_max = int(math.ceil(xlim / P)) + 1
    j_max = int(math.ceil(max(ys) / wp)) + 1
    placed = []
    for i in range(i_min, i_max + 1):
        x0 = i * P
        if x0 < -xlim or x0 + L * cth > xlim:
            continue
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


def check_scale_clearance(p, tmpl):
    P, wp = p["SCALE_PITCH"], p["SCALE_W"] + p["SCALE_GAP"]
    out = {}
    for name, d in [("next column (same y)", (P, 0, 0)), ("next column (+half row)", (P, wp / 2, 0)),
                    ("same column (+row)", (0, wp, 0)), ("two columns on", (2 * P, 0, 0))]:
        other = moved(tmpl, d)
        out[name] = (tmpl.common(other).Volume, tmpl.distToShape(other)[0])
    return out


def check_roll(p, tmpl):
    """Smallest neutral-surface radius R (scales on the OUTSIDE of the roll) at which two neighbouring scales
    still don't collide. The skin mid-plane is the neutral surface (0.5*SKIN_T above the scale origin)."""
    P = p["SCALE_PITCH"]
    hn = p["SKIN_T"] / 2
    min_ok = None
    for R in range(300, 9, -2):
        phi = P / R
        nb = tmpl.copy()
        nb.rotate(Vector(0, 0, 0), Vector(0, 1, 0), -math.degrees(phi))   # tilts toward the centre (gear side, +z)
        nb.translate(Vector((R + hn) * math.sin(phi), 0, hn + R - (R + hn) * math.cos(phi)))
        if tmpl.common(nb).Volume > 1e-3 or tmpl.distToShape(nb)[0] < 1e-6:
            break
        min_ok = R
    return min_ok


# ---------------------------------------------------------- straps / tabs
def make_tab(p, sx, poly, z0, thick):
    """Slotted strap tab on each side at x=sx on the outline poly. Returns ([tab +y, tab -y], [slot_y +, slot_y -])."""
    tl, to, sw = p["TAB_LEN"], p["TAB_OUT"], p["STRAP_W"]
    ymin, ymax = y_extent(poly, sx)
    sols, slot_y = [], []
    for side, edge in ((1, ymax), (-1, ymin)):
        y_in = edge - side * 0.8
        y_out = edge + side * to
        tab = Part.makeBox(tl, abs(y_out - y_in), thick, Vector(sx - tl / 2, min(y_in, y_out), z0))
        sy = edge + side * (to * 0.55)
        slot = Part.makeBox(sw + 1.0, p["SLOT_W"], thick + 2,
                            Vector(sx - (sw + 1.0) / 2, sy - p["SLOT_W"] / 2, z0 - 1))
        sols.append(tab.cut(slot))
        slot_y.append(sy)
    return sols, slot_y


def make_strap(p, sx, slot_y, z_slot, z_top):
    """Webbing as a U-shaped band: through one slot, over the gear top, through the other slot."""
    sw, st = p["STRAP_W"], p["STRAP_T"]
    yR, yL = slot_y
    return Part.Compound([
        Part.makeBox(sw, abs(yR - yL) + st, st, Vector(sx - sw / 2, min(yR, yL) - st / 2, z_top)),
        Part.makeBox(sw, st, z_top + st - z_slot, Vector(sx - sw / 2, yR - st / 2, z_slot)),
        Part.makeBox(sw, st, z_top + st - z_slot, Vector(sx - sw / 2, yL - st / 2, z_slot)),
    ])


# ------------------------------------------------------------------- caps
def make_cap(p, gear_faces, side, bridge_y):
    """Tip (side=+1) or tail (side=-1) protector. Returns (shell, liner, strap_x, shell_poly, (z_bottom, z_top))."""
    L, GT = p["LENGTH"], p["GEAR_T"]
    cc, cl, cs = p["CAP_CLEAR"], p["CAP_LINER_T"], p["CAP_SHELL_T"]
    x_c = L / 2 - p["CAP_LEN"]
    xs = side * (x_c + 0.5)                     # cap starts here (open back)
    xfar = side * (L / 2 + 60)
    xr = side * (L / 2 - p["ROOF_LEN"])         # roof starts here
    zb = -(cl + cs)
    zc = GT + cc + cl                           # underside of the roof liner
    zt = zc + cs                                # roof top
    zw = GT + p["CAP_WALL_ABOVE"]               # side-wall top where there is no roof

    cav_f = [offset_face(f, cc) for f in gear_faces]
    lo_f = [offset_face(f, cc + cl) for f in gear_faces]
    sh_f = [offset_face(f, cc + cl + cs) for f in gear_faces]

    shell = union_prism(sh_f, zb, zt)
    if bridge_y:
        shell = shell.fuse(xbox(xs, xfar - side * 70, zb, zb + cs, bridge_y)).removeSplitter()
    poly = poly_of(bottom_face(shell))
    shell = shell.common(xbox(xs, xfar, zb - 1, zt + 1))
    back = xs - side * 5
    open_top = union_prism(lo_f, -cl, zt + 1).common(xbox(back, xr, -cl - 1, zt + 2))
    cavity = union_prism(lo_f, -cl, zc).common(xbox(back, xfar, -cl - 1, zc + 1))
    shell = shell.cut(cavity).cut(open_top).cut(xbox(back, xr, zw, zt + 2)).removeSplitter()

    liner = union_prism(lo_f, -cl, zc).cut(union_prism(cav_f, 0, GT + cc))
    liner = liner.common(xbox(xs, xfar, -cl - 1, zc + 1)).cut(xbox(back, xr, GT + cc, zc + 2)).removeSplitter()
    sx = side * (L / 2 - p["ROOF_LEN"] / 2)
    return shell, liner, sx, poly, (zb, zt)


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
    name = p["NAME"]
    clear, wall, lip = p["CLEARANCE"], p["WALL"], p["LIP_H"]
    liner_t, skin_t = p["LINER_T"], p["SKIN_T"]
    L = p["LENGTH"]
    x_c = L / 2 - p["CAP_LEN"]
    clip = x_c - 0.5                                   # body ends here (1 mm gap to the cap)

    # --- outlines --------------------------------------------------------
    base_pts = profile_pts(L, p["TIP_W"], p["WAIST_W"], p["TAIL_W"], p["CAP"])
    centers = p["CENTERS_Y"]
    gear_faces = [face_from_pts(base_pts, dy) for dy in centers]
    pocket_faces = [offset_face(f, clear) for f in gear_faces]
    bridge_y = max(abs(c) for c in centers) if len(centers) > 1 else 0
    if len(pocket_faces) == 1:
        merged = pocket_faces[0]
    else:
        half = L / 2 - p["CAP"] - 60
        bridge = face_from_pts([(-half, -bridge_y), (half, -bridge_y), (half, bridge_y), (-half, bridge_y)])
        solid = prism(pocket_faces[0], 0, 1)
        for f in pocket_faces[1:] + [bridge]:
            solid = solid.fuse(prism(f, 0, 1))
        solid = solid.removeSplitter()
        merged = [f for f in solid.Faces if abs(f.BoundBox.ZMax) < 1e-6 and abs(f.BoundBox.ZMin) < 1e-6][0]
    liner_outer = offset_face(merged, wall)
    skin_outer = offset_face(liner_outer, skin_t)
    ymax_all = max(v.y for v in skin_outer.OuterWire.discretize(Deflection=1.0)) + 5
    body_clip = xbox(-clip, clip, -liner_t - skin_t - 1, lip + 1)

    # --- roll-relief V-notches in the lip (it compresses when the body is rolled gear-side in) -------
    wb, wt, wpitch = p["WEDGE_BOT"], p["WEDGE_TOP"], p["WEDGE_PITCH"]
    ztop_w = lip + 1
    wt_z = wb + (wt - wb) * ztop_w / lip
    wedges = []
    k = 0
    while k * wpitch < clip - 5:
        for kk in ([k] if k == 0 else [k, -k]):
            cx = kk * wpitch
            pts = [Vector(cx - wb / 2, -ymax_all, 0), Vector(cx + wb / 2, -ymax_all, 0),
                   Vector(cx + wt_z / 2, -ymax_all, ztop_w), Vector(cx - wt_z / 2, -ymax_all, ztop_w)]
            wedges.append(Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, 2 * ymax_all, 0)))
        k += 1
    wedge_c = Part.Compound(wedges)

    # --- liner -----------------------------------------------------------
    liner = prism(liner_outer, -liner_t, lip)
    for f in pocket_faces:
        liner = liner.cut(prism(f, 0, lip + 1))
        liner = liner.cut(prism(offset_face(f, -p["SHELF_W"]), -p["RECESS"], 0.01))
    grooves = []
    x = -clip + p["GROOVE_PITCH"] / 2
    while x < clip:
        grooves.append(Part.makeBox(p["GROOVE_W"], 2 * ymax_all, p["GROOVE_D"],
                                    Vector(x - p["GROOVE_W"] / 2, -ymax_all, -liner_t)))
        x += p["GROOVE_PITCH"]
    liner = liner.cut(Part.Compound(grooves)).cut(wedge_c).common(body_clip).removeSplitter()

    # --- skin (+ strap tabs) -----------------------------------------------
    z0 = -liner_t - skin_t
    skin = prism(skin_outer, z0, lip).cut(prism(liner_outer, -liner_t, lip + 1))
    skin = skin.cut(wedge_c).common(body_clip).removeSplitter()
    skin_poly = poly_of(skin_outer)
    straps = []
    for sx in p["STATIONS"]:
        tabs, sy = make_tab(p, sx, skin_poly, z0, p["TAB_T"])
        for t in tabs:
            skin = skin.fuse(t)
        straps.append(make_strap(p, sx, sy, z0 + 1.0, p["GEAR_T"] + 0.3))
    skin = skin.removeSplitter()

    # --- scales ------------------------------------------------------------
    tmpl = make_scale(p)
    scales = tile_scales(p, tmpl, poly_of(liner_outer), z0, clip)
    scales_c = Part.Compound(scales)
    clearances = check_scale_clearance(p, tmpl)
    r_roll = check_roll(p, tmpl)

    # --- caps --------------------------------------------------------------
    cap_parts = {}
    for label, side in (("Tip", 1), ("Tail", -1)):
        shell, cliner, sx, cpoly, (zb, zt) = make_cap(p, gear_faces, side, bridge_y)
        tabs, sy = make_tab(p, sx, cpoly, zb, p["CAP_SHELL_T"])
        for t in tabs:
            shell = shell.fuse(t)
        cap_parts[label + "_Cap_Shell"] = shell.removeSplitter()
        cap_parts[label + "_Cap_Liner"] = cliner
        straps.append(make_strap(p, sx, sy, zb + 1.0, zt))
    straps_c = Part.Compound(straps)

    ref = Part.Compound([prism(f, 0, p["GEAR_T"]) for f in gear_faces])

    # --- document ----------------------------------------------------------
    doc = App.newDocument(name)
    shapes = [("Liner", liner), ("Skin", skin), ("Scales", scales_c)] + list(cap_parts.items()) + \
             [("Straps", straps_c), ("Gear_Reference", ref)]
    objs = {}
    for label, shp in shapes:
        o = doc.addObject("Part::Feature", label)
        o.Shape = shp
        objs[label] = o
    doc.recompute()
    fc = os.path.join(here, name + ".FCStd")
    doc.saveAs(fc)
    visible = [l for l, _ in shapes if l != "Gear_Reference"]
    show_on_open(fc, visible)

    import Mesh
    product = [objs[l] for l in visible if l != "Straps"]
    fname = lambda o: "%s-%s" % (name, o.Label.lower().replace("_", "-"))
    for o in product + [objs["Straps"]]:
        Part.export([o], os.path.join(here, fname(o) + ".step"))
    for o in product:
        Mesh.export([o], os.path.join(here, fname(o) + ".stl"))
    Part.export(product, os.path.join(here, name + "-assembled.step"))

    # --- report ------------------------------------------------------------
    body = Part.Compound([liner, skin, scales_c])
    allp = Part.Compound([body] + list(cap_parts.values()))
    bb = allp.BoundBox
    print("=== %s ===" % name)
    print("scales: %d | liner valid=%s | skin valid=%s | straps: %d" %
          (len(scales), liner.isValid(), skin.isValid(), len(straps)))
    print("body: %.0f x %.0f mm, %.1f mm thick below the base plane (scale stack included)" %
          (body.BoundBox.XLength, body.BoundBox.YLength, -body.BoundBox.ZMin))
    print("with caps: X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f" % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
    for kname, (vol, dist) in clearances.items():
        print("scale clearance vs %-26s overlap %.4f mm3, min gap %.2f mm" % (kname, vol, dist))
    print("min roll radius (scales outside, neutral surface): %s mm" % r_roll)
    d = p["DENSITY"]
    ms = {"scales": scales_c.Volume * d["scales"], "skin": skin.Volume * d["skin"], "liner": liner.Volume * d["liner"]}
    caps_m = sum(cap_parts[kk].Volume * (d["cap_shell"] if kk.endswith("Shell") else d["liner"]) for kk in cap_parts)
    body_m = sum(ms.values())
    print("est. mass (g): scales %.0f, skin %.0f, liner %.0f => rollable body %.0f; caps (4 parts) %.0f; total %.0f" %
          (ms["scales"], ms["skin"], ms["liner"], body_m, caps_m, body_m + caps_m))
    # roll limit: the V-notches in the lip must close at the top; r (at the base plane, gear side in) >= lip*pitch/notch_top
    r_lip = lip * wpitch / wt
    r_core = max(r_lip + liner_t + skin_t / 2, r_roll or 0)        # neutral-surface radius of the innermost turn
    t_avg = liner_t + skin_t + 3.0
    d_out = math.sqrt((2 * r_core) ** 2 + 4 * 2 * clip * t_avg / math.pi)
    print("lip notches limit the roll radius to %.0f mm at the base plane (scales alone allow %s mm)" % (r_lip, r_roll))
    print("rolled body (length %.0f, avg thickness %.1f): core diameter ~%.0f mm -> outer diameter ~%.0f mm" %
          (2 * clip, t_avg, 2 * r_core, d_out))
    return {"liner": liner, "skin": skin, "scales": scales_c}
