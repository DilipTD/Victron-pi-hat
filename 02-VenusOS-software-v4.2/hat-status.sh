#!/bin/sh
# Victron HAT diagnostics from the command line - works with classic GUI and GUI v2 (reads D-Bus, no GUI needed)
# usage: /data/VictronHat/hat-status.sh
S=com.victronenergy.vichat
for p in $(dbus -y $S / GetValue 2>/dev/null | tr -d "{}'," | tr ' ' '\\n' | grep -o '^/[^:]*' | sort -u); do
    echo "$p = $(dbus -y $S $p GetValue 2>/dev/null)"
done
[ -z "$p" ] && { echo "no $S on D-Bus: check 'svstat /service/vichat' and /var/log/vichat"; exit 1; }
