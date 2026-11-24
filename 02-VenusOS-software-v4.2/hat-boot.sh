#!/bin/sh
# called from /data/rc.local at every boot
mkdir -p /run/udev/rules.d
cp /data/VictronHat/90-victron-hat.rules /run/udev/rules.d/
udevadm control --reload
udevadm trigger --action=add --subsystem-match=tty
# RS485 (J402) direction control - harmless if the EEPROM overlay already set it
for i in 1 2 3 4 5 6 7 8 9 10; do [ -e /dev/ttySC3 ] && break; sleep 1; done
[ -e /dev/ttySC3 ] && python3 /data/VictronHat/rs485-mode.py /dev/ttySC3
# sysfs number = chip base + GPIO
G=${GPIO_SYSFS:-/sys/class/gpio}
BASE=0
for c in $G/gpiochip*; do
    if grep -q bcm2835 $c/label 2>/dev/null; then BASE=$(cat $c/base); break; fi
done
# GPIO24 buzzer (BZ601) and GPIO23 OUT5 fan (J603, board v25.0): outputs, off at boot.
# vichat_dbus.py switches the fan afterwards (diag.json fan_mode: 0 off, 1 on, 2 auto).
PINS=24
V=$(tr -d '\000' < ${HAT_DT:-/proc/device-tree/hat}/product_ver 2>/dev/null)
[ -n "$V" ] && [ $((V)) -ge $((0x0700)) ] && PINS="24 23"      # GPIO23 only on v25.0+ boards
for P in $PINS; do
    N=$((BASE + P))
    [ -d $G/gpio$N ] || echo $N > $G/export 2>/dev/null
    echo out > $G/gpio$N/direction 2>/dev/null
    echo 0 > $G/gpio$N/value 2>/dev/null
done
# v29.8: no RTC on the board (IC901/supercap removed). The system clock comes from NTP or the GUI.
exit 0
