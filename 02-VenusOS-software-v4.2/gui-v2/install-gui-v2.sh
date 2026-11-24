#!/bin/sh
# Install / remove the Victron HAT status plugin for GUI v2.  usage: install-gui-v2.sh install|uninstall
# Needs the gui-v2 plugin compiler on the GX (Large image) or a prebuilt VictronHat.json next to this script.
N=VictronHat; HERE=$(cd "$(dirname "$0")" && pwd); A=/data/apps/available/$N; E=/data/apps/enabled/$N
C=/opt/victronenergy/gui-v2/gui-v2-plugin-compiler.py
if [ "$1" = uninstall ]; then rm -f "$E"; rm -rf "${A:?}"; exit 0; fi
[ -e /opt/victronenergy/venus-gui-v2 ] || { echo "GUI v2 not installed - skipped"; exit 0; }
T=$(mktemp -d) || exit 1; mkdir -p "$T/$N"; cp "$HERE/$N"/*.qml "$T/$N"/
if [ -f "$HERE/$N.json" ]; then cp "$HERE/$N.json" "$T/$N/"
elif [ -f $C ]; then (cd "$T/$N" && python3 $C --min-required-version v1.4.1 --settings VictronHatSettings.qml) || { rm -rf "${T:?}"; exit 1; }
else echo "GUI v2 page skipped: this image has no $C (needs a Large image). Compile once elsewhere: python3 <gui-v2>/tools/gui-v2-plugin-compiler.py --min-required-version v1.4.1 --settings VictronHatSettings.qml, copy VictronHat.json to $HERE/, run setup again"; rm -rf "${T:?}"; exit 1; fi
mkdir -p "$A/gui-v2" && cp "$T/$N/$N.json" "$A/gui-v2/" && ln -sfn "$A" "$E" && echo "GUI v2 plugin installed: Settings > Integrations > UI Plugins > Victron HAT status"
rm -rf "${T:?}"
