"""<Project name> - parametric FreeCAD build script. Units: mm."""
import os
import FreeCAD as App
import Part

# --- Parameters ---
LENGTH = 50.0
WIDTH = 30.0
HEIGHT = 10.0

# --- Build ---
here = os.path.dirname(os.path.abspath(__file__))
doc = App.newDocument("Part")
body = doc.addObject("Part::Box", "Body")
body.Length, body.Width, body.Height = LENGTH, WIDTH, HEIGHT
doc.recompute()

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

doc.saveAs(os.path.join(here, "part.FCStd"))
show_on_open(os.path.join(here, "part.FCStd"), ["Body"])
Part.export([body], os.path.join(here, "part.step"))
