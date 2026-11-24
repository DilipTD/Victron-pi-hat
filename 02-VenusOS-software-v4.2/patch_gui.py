#!/usr/bin/env python3
# usage: patch_gui.py install|uninstall   (adds/removes the menu entry after "Package manager")
import re, sys
F = "/opt/victronenergy/gui/qml/PageSettings.qml"
B, E = "// VictronHat begin", "// VictronHat end"
t = open(F).read()
t = re.sub(r"[ \t]*" + re.escape(B) + r".*?" + re.escape(E) + r"\n", "", t, flags=re.S)
if sys.argv[1] == "install":
    k = t.find("PageSettingsPackageManager")
    if k < 0:
        sys.exit("Package manager menu entry not found in PageSettings.qml")
    start = t.rfind("MbSubMenu", 0, k)
    i = t.find("{", start); d = 0
    while True:
        d += {"{": 1, "}": -1}.get(t[i], 0)
        if d == 0: break
        i += 1
    eol = t.find("\n", i) + 1
    block = ("\t\t%s\n\t\tMbSubMenu {\n\t\t\tdescription: qsTr(\"Victron HAT status\")\n"
             "\t\t\tsubpage: Component { PageVictronHat {} }\n\t\t}\n\t\t%s\n") % (B, E)
    t = t[:eol] + block + t[eol:]
open(F, "w").write(t)
