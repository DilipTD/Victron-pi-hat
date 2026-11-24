#!/bin/bash
# Write the Victron Pi HAT ID EEPROM (IC801, 24LC32A at 0x50 on ID_SD/ID_SC).
# Run ONCE per new board, on Raspberry Pi OS (Venus OS has no dtoverlay tool):
#   1. Bridge solder jumper JP801 "ID WP" on the back to disable write protect.
#   (board v26.0: the EEPROM is written from the Pi only; v25.0 boards can also use their USB-C port, package v2.0)
#   2. sudo ./flash-eeprom.sh            (uses victron-hat.eep from this folder)
#   3. Remove the solder bridge on JP801 again, power off, move the SD card back to Venus.
set -e
cd "$(dirname "$0")"
EEP=${1:-victron-hat.eep}
[ -f "$EEP" ] || { echo "missing $EEP"; exit 1; }
dtoverlay i2c-gpio i2c_gpio_sda=0 i2c_gpio_scl=1 bus=9
modprobe at24
DEV=/sys/class/i2c-adapter/i2c-9
[ -d $DEV/9-0050 ] || echo "24c32 0x50" > $DEV/new_device
sleep 1
dd if="$EEP" of=$DEV/9-0050/eeprom status=none
if cmp -n "$(stat -c%s "$EEP")" "$EEP" $DEV/9-0050/eeprom; then echo "EEPROM written and verified."; else echo "VERIFY FAILED (is JP801 bridged?)"; RC=1; fi
echo 0x50 > $DEV/delete_device
exit ${RC:-0}
