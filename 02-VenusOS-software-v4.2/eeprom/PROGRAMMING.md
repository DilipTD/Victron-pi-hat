# Writing the HAT ID EEPROM (IC801, 24LC32A, I2C address 0x50)

`victron-hat.eep` is the complete raw EEPROM image (product_ver **0x0900**, board v27.0). Write it from address 0.
The image is the same as for v25.0 except for product_ver (GPIO23 = OUT5 fan output stays).

## Board v26.0: with the Pi fitted

Board v26.0 has no USB-C programming port (removed on request). Write the EEPROM from the Pi:

1. Boot Raspberry Pi OS (not Venus OS) on the Pi with the HAT fitted and powered from X101 (7-40 V). Do NOT plug a USB-C supply into the Pi: on v28.x the Pi 5 V is tied directly to the HAT +5V rail.
2. Bridge solder jumper **JP801 "ID WP"** on the back of the HAT. This pulls WP low, so the EEPROM accepts writes.
3. Run `sudo ./flash-eeprom.sh` in this folder. It writes `victron-hat.eep` and reads it back
   (`EEPROM written and verified`).
4. Remove the JP801 bridge (write protection back on) and reboot into Venus OS.

## Older boards

* v25.0: USB-C port J802 and `usb-flash-eeprom.py` - use package v2.0 for that tool; `flash-eeprom.sh` works there too.
* v24.1 / v24.2: J801 1x5 header (3V3, SDA, SCL, WP, GND) with a 3.3 V I2C programmer, or `flash-eeprom.sh`.
* Write each board its own image: 0x0900 = v27.0, 0x0800 = v26.0, 0x0700 = v25.0, 0x0602 = v24.2. Package v2.2 runs on every board.

## Check
On Venus OS after a reboot: `cat /proc/device-tree/hat/product_ver` shows `0x0900`, and the Victron HAT status page shows
"EEPROM 0x0900", hardware "Victron Pi HAT v27", the "OUT5 fan" line and the "Pi 5 V current" line.

## Board v28.0 (package v4.0)
`victron-hat.eep` in package v4.0 is product_ver **0x0F00** (board v28.0). Same overlay as before (MCP2515 on CE0, 2x SC16IS752); CE1/CE2 are unused on v28.0.
Write it the same way (Raspberry Pi OS, JP801 bridged, `sudo ./flash-eeprom.sh`, then open JP801). Check: `cat /proc/device-tree/hat/product_ver` shows `0x0F00`.
