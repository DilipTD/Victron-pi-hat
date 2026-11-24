## v2.7 (board v27.6, EEPROM 0x0E00)
* ADC2 CH6 is now AUX2, a second 0-3.3 V test pad (1k series): `/Diag/Aux2`, warning "AUX2 over range". All 16 ADC channels are used.
* GUI shows AUX2.

## v2.6 (board v27.5, EEPROM 0x0D00) - 8-channel second ADC
* IC905 is an MCP3208 (8 channels) on SPI0 CE2 (GPIO16). New readings: display 5 V after F102 (`/Diag/Vdisp`), relay/fan 5 V after F601 (`/Diag/Vrelay`),
  battery before the input fuse (`/Diag/Vraw`) and a spare 0-3.3 V test-pad input AUX (`/Diag/Aux`); CH6 is a spare tied to GND.
* New warnings: "display fuse (PTC) tripped", "relay/fan fuse (PTC) tripped", "input fuse/FET drop high".
* GUI shows the four new values; older boards hide them (no value).
* Board LEDs: solder jumper JP601 "LED PWR" (bridged = on, cut = off) switches the always-on power LED.

## v2.5 (board v27.4, EEPROM 0x0C00) - Raspberry Pi 5 + Active Cooler
* Supports Raspberry Pi 5 with the official Active Cooler (20 mm M2.5 standoffs + 2x20 stacking/extender header). Needs Venus OS v3.70 or later, **raspberrypi5** image.
* Pi current warning at 3.3 A on 0x0C00 boards (2.6 A before); new warning "5 V module near 5 A limit" when Iout > 4.6 A; display current warning at 1.4 A (1.5 A PTC F101).
* Leave `usb_max_current_enable` at its default (Pi 5 USB 600 mA total): the HAT budgets 3.5 A for the Pi, and Pi + display + relays must stay at or below 5 A.
* Pi 5 serial console is on its own debug connector, so the GPIO14/15 UART stays free; overlays are unchanged (RP1 GPIO numbering is the same on the header).
* EEPROM is a legacy V1 HAT (HAT+ class 00); the Pi 5 reads it as before.

## v2.4 (board v27.3, EEPROM 0x0B00)

* IC901 channels in safety order on 0x0B00 boards (CH0 VIN, CH1 IIN, CH2 IOUT, CH3 Pi 5 V, CH4 Pi 5 V current, CH5 5 V module, CH6 TH901, CH7 3V3); IC905 CH3 spare.
* Older boards keep their own channel map.

# VictronHat - SetupHelper package v2.1 (HAT v19.1 - v26.0, Pi 3)
Install (needs SetupHelper already installed):
  scp -r VictronHat root@<pi>:/data/
  ssh root@<pi> /data/VictronHat/setup      # choose Install, then reboot
Uninstall: run setup again and choose Uninstall.

Does: config.txt block (I2C, SPI, 2x SC16IS752, MCP2515), udev rules at boot
(ttySC0-2 VE.Direct, ttySC3 cgwacs/ET112), buzzer GPIO24 off at boot.
Relays/inputs: install kwindrem RpiGpioSetup separately; pins in gpio_list.REFERENCE.
Then GUI: Settings > Services > VE.Can port > "VE.Can & Lynx Ion BMS".

Unverified on hardware: written from the SetupHelper docs; test on a spare SD card.

## v1.2 - "Victron HAT status" in the classic GUI
Settings > Package manager > **Victron HAT status** (new line right after it).
Shows config.txt check, J301/J302/J401/J402 devices, VE.Can state/errors/devices,
OUT1-4, IN1-4 and a Buzzer test switch. No web server, no open port.
How: service vichat publishes com.victronenergy.vichat on dbus; setup copies
PageVictronHat.qml into /opt/victronenergy/gui/qml and adds the menu entry to
PageSettings.qml (marked "VictronHat begin/end"; Uninstall removes it).
After a firmware update PackageManager (Auto install ON) re-applies it.
Classic GUI only (not GUI v2). Needs the Package manager entry to exist.
Relays/inputs need RpiGpioSetup; otherwise they show n/a.
Not tested on a real Venus; the QML/patch code was written from Venus conventions.
Log: /var/log/vichat. Roll back: run setup > Uninstall.

## Install from GitHub (SetupHelper)
Repo: https://github.com/DilipTD/VictronHat (branch main; repo name must equal the folder name).
In Venus: Settings > Package manager > Inactive packages > add "VictronHat" (user DilipTD, branch main) > Download > Install.

## v1.3 - HAT ID EEPROM (board v20.9 and later)
v20.9 boards carry a 24LC32A ID EEPROM (IC801). Write `eeprom/victron-hat.eep` to it once
(Raspberry Pi OS, JP801 bridged, `sudo eeprom/flash-eeprom.sh`). After that the Pi firmware loads the
board overlay (2x SC16IS752 + MCP2515, I2C and SPI) and the GPIO defaults by itself - no config.txt edits,
and it survives Venus firmware updates. `setup` detects the EEPROM and then leaves /u-boot/config.txt alone
(older boards without EEPROM still get the config.txt lines). The status page shows "Board config: EEPROM 0x0209".
Overlay source: eeprom/victron-hat-overlay.dts (checked: applies cleanly to the Pi 3 bcm2710-rpi-3-b.dtb).

## v2.2 - board v27.0 (Pi 5 V current, module 5 mm from X101, comm pairs)
* Board v27.0 (EEPROM product_ver **0x0900**). ADC channel 7 now measures the **Pi 5 V current**: RS3 (5 mOhm, 1206) sits in
  PI_5V after the ideal-diode FET Q102, IC904 INA181A3 (x100) gives 0.5 V/A, range 0-5 A (the Pi branch is limited to 2.5 A).
  New dbus paths `/Diag/Ipi` (A) and `/Diag/Ppi` (W = Vpi x Ipi); status warns "Pi current high" above 2.6 A.
  On v27.0 boards `/Diag/I3v3` and `/Diag/P3v3` stay empty (the HAT 3.3 V current sense is removed, J201 pins 1/17 feed +3V3 directly).
  Older boards (0x0601-0x0800) keep CH7 = HAT 3.3 V current as before. Calibration: `k_ipi`, `cal_ipi`, `off_ipi` in diag.json.
* GUI: "Pi 5 V current" and "Pi 5 V power" lines (shown on v27.0); "HAT 3.3 V current" only on v24.1-v26.0 boards.
* Node-RED: `global.hat.Ipi` and `global.hat.Ppi`.
* Status page shows "Victron Pi HAT v27". No change to the UART / CAN / RS485 / I/O configuration (same GPIOs and overlay).

## v2.1 - board v26.0 (7Semi AP64500 5 V module, no USB-C port)
* Board v26.0 (EEPROM product_ver **0x0800**) takes its 5 V from a plug-on 7Semi AP64500 buck module (U101, fixed 5.0 V / 5 A)
  instead of the on-board LM5146. The diagnostics channels are unchanged: "5 V supply output" (+5V_REG, module output),
  "5 V output current" (RS2), "5 V supply temperature" (TH901 under the module). Labels renamed from "buck" to "5 V supply".
* The USB-C EEPROM port of v25.0 is gone: `eeprom/usb-flash-eeprom.py` is removed from this package. Write the EEPROM from the
  Pi with `eeprom/flash-eeprom.sh` (bridge JP801). See `eeprom/PROGRAMMING.md`.
* Fan (OUT5, GPIO23) works as in v2.0 on v25.0 and v26.0 boards. Status page shows "Victron Pi HAT v26".
* The 5 V supply output reads about 5.0 V on v26.0 (5.2 V on v24/v25 boards): this is expected.

## v2.0 - board v25.0 (OUT5 fan header, USB-C EEPROM programming)
* Board v25.0 (EEPROM product_ver 0x0700) adds **OUT5**: GPIO23 drives ULN2003 channels 5 and 7 in parallel, which switch the
  low side of the 2-pin fan header **J603** (JST PH, pin 1 = +5 V, pin 2 = FAN-). For a 5 V fan up to 0.5 A.
* `vichat_dbus.py` controls the fan: `/Fan/Mode` 0 = off, 1 = on, 2 = auto (default). Auto switches on at 55 C and off at
  45 C buck temperature (TH901, from vichat_diag); with no temperature reading the fan runs (fail safe).
  Set `fan_mode`, `fan_on_c`, `fan_off_c` in diag.json (or in the user copy /data/setupOptions/VictronHat/diag.json).
  MQTT: `W/<portal>/vichat/0/Fan/Mode {"value": 2}`; state on `N/<portal>/vichat/0/Fan/State`.
* GUI page: "OUT5 fan (J603)" (Off / On / Auto) and "OUT5 fan state", shown only on v25.0 boards.
* Node-RED flow: inject nodes FAN AUTO / ON / OFF, topic `FAN`; `global.hat.FAN` and `FAN_MODE`.
* `hat-boot.sh` sets GPIO23 as output, low, at boot (only on v25.0 boards). Do not add GPIO23 to the RpiGpioSetup gpio_list.
* EEPROM: board v25.0 has no J801 header. Write the EEPROM through the USB-C port J802 with `eeprom/usb-flash-eeprom.py`
  (MCP2221A bridge, works on Windows / Linux / macOS, Pi not needed). See `eeprom/PROGRAMMING.md`.
* Older boards (v19.1 to v24.2) work as before: no fan line, GPIO23 not touched.

## v1.9 - board v24.2
* Board v24.2 (EEPROM product_ver 0x0602) has R909 = 47k: the buck temperature is read down to -35 C. vichat_diag picks the
  47k pull-up automatically from the EEPROM version; v24.0/v24.1 boards keep 10k. An `ntc_pullup` entry in diag.json still overrides it.
* v24.2 measures the input current after the reverse-polarity FET (RS1/IC902 moved): no software change needed.
* EEPROM image `eeprom/victron-hat.eep`: product_ver 0x0602 (same overlay as 0x0601).

## v1.8 - fixes found by the v24.1 simulation and software tests
* Buck temperature (TH901) now uses the Murata NCP18XH103 R-T table instead of one Beta value
  (Beta 3435 read 2.5 C high at -20 C and 1.7 C high at 120 C). Table and pull-up are in `diag.json`.
* With the v24.0/v24.1 pull-up (R909 10k) the ADC input saturates below about -3 C. v1.7 then showed
  "-1.8 C" with status OK. v1.8 shows no value and the status "T1 below -3 C (sensor range)".
  Boards with R909 = 47k (v24.2) read down to -35 C: set `"ntc_pullup": 47000` in diag.json.
* Any channel at full scale is reported ("Vin over range" above 38 V, etc.).
* When the ADC is missing, silent or fails, all values are cleared (no stale numbers on the GUI, MQTT or VRM).
* Node-RED flow: the first keepalive is sent as soon as the portal ID is known; later keepalives use
  `suppress-republish`, so Venus no longer re-sends every topic every 30 s.

## v1.7 - board v24.0 / v24.1: HAT diagnostics (MCP3208 ADC)
* New service **vichatdiag** (`vichat_diag.py`) reads the MCP3208 on SPI0 CE1 (`/dev/spidev0.1`) once per second:
  input voltage/current/power (X101, RS1), buck output voltage (+5V_REG), 5 V output current/power (RS2),
  Pi 5 V after Q102, 3.3 V rail, HAT 3.3 V current (RS3 + INA181, board v24.1), buck temperature (TH901), efficiency.
* dbus: `com.victronenergy.dcload.vichat` (DC load "Victron HAT input" - shows in the device list and VRM),
  `com.victronenergy.temperature.vichat_t1` (buck temperature sensor, usable for alarms/Node-RED).
* The "Victron HAT status" page has a new top section with all values and a Diagnostics status line
  (OK / HOT / Pi 5 V low / input low).
* Calibration: copy `/data/VictronHat/diag.json` to `/data/setupOptions/VictronHat/diag.json` and edit it there (survives package updates): `cal_iin`, `cal_iout` gain trims, `off_iin`, `off_iout`, `hot_c`.
  Measure the input and 5 V currents once with a meter and set the gains; restart with `svc -t /service/vichatdiag`.
* EEPROM image for board v24.1: product_ver 0x0601 (v24.0 used 0x0600, same overlay); the overlay additionally enables spidev on SPI0 CE1. Programming: `eeprom/PROGRAMMING.md` (J801 header or the Pi).
  Re-flash the EEPROM on v24 boards (`eeprom/flash-eeprom.sh`). Older boards: the service stays idle ("no ADC").
* Board v24.1: CH7 = HAT 3.3 V current (`/Diag/I3v3`, `/Diag/P3v3`); the second temperature sensor was removed.
* **Node-RED**: `nodered/victron-hat-io-flow.json` (import in Node-RED: menu > Import). It uses the local Venus MQTT broker
  (enable Settings > Services > MQTT Access) and gives every value in `global.hat`: Vin, Iin, Pin, V5reg, Iout, Pout,
  Efficiency, Vpi, V3v3, I3v3, P3v3, T1, Status, IN1-IN4, OUT1-OUT4. Set outputs with msg.topic OUT1-OUT4 (or BUZZER) and payload 1/0.
  Without MQTT: the Victron "Custom" input/output nodes list `com.victronenergy.dcload.vichat` (analog) and
  `com.victronenergy.vichat` (/In/n/State, /Out/n/State writeable, /Buzzer/Test).
* Needs the Venus OS kernel spidev driver (`/dev/spidev0.1` must exist) - not verified on hardware yet.

## v1.6 - board v23.0
* EEPROM image for board v23.0 (product_ver 0x0500, same overlay). The Victron HAT page shows "EEPROM 0x0500".
* Board v23.0: 7-40 V input, 5 A output, JP101 5 V link, constant-current DC inputs (IN COM = minus). No software changes; the inputs still read LOW when driven.
* Boards v21.0 (0x0300) and v22.0 (0x0400) keep working with this package.

## v1.5 - board v22.0
* EEPROM image for board v22.0 (product_ver 0x0400, same overlay: 2x SC16IS752, MCP2515, RS485 auto-direction). The Victron HAT page shows "EEPROM 0x0400".
* No software changes otherwise. Boards v21.0 (0x0300) keep working with this package.

## v1.4 - RS485 direction control + board v21.0
* J402 (ttySC3) needs the SC16IS752 auto RS-485 mode so RTSB switches the SP3485 to transmit. v1.3 and
  earlier did not set it (the meter would never get an answer). Now: the EEPROM overlay sets it
  (linux,rs485-enabled-at-boot-time + rs485-rts-active-low on the 0x49 chip) and hat-boot.sh also sets it
  with rs485-mode.py at every boot (for boards configured through config.txt).
* EEPROM image updated for board v21.0 (product_ver 0x0300).

## v2.8 - classic GUI and GUI v2
* Hardware side (EEPROM overlay, ttySC0-3, can0, udev, buzzer off) is GUI independent and works in both.
* Classic GUI: "Victron HAT status" page as before. If PageSettings.qml is absent or differs, setup skips the patch and the install still succeeds.
* GUI v2: no custom page (separate framework). Use `hat-status.sh` (D-Bus), MQTT (N/<id>/vichat/...) or the Node-RED flows. VE.Can profile is set in the GUI v2 CAN-bus settings.
* Superseded by v2.9.

## v2.9 - native GUI v2 status page (plugin)
* gui-v2/VictronHat/VictronHatSettings.qml: "Victron HAT status" for GUI v2 using the official Victron.GuiPlugins API (Settings > Integrations > UI Plugins > Victron HAT status). Same rows as the classic page (board, supply, temperatures, display/relay/AUX, ports, VE.Can, OUT1-4, fan mode, IN1-4, buzzer test). Optional rows hide when the ADC channel is not valid.
* setup runs gui-v2/install-gui-v2.sh: compiles the plugin on the GX with /opt/victronenergy/gui-v2/gui-v2-plugin-compiler.py (Large image) or uses a prebuilt gui-v2/VictronHat.json; installs to /data/apps/available/VictronHat/gui-v2 and links /data/apps/enabled/VictronHat. Uninstall removes both.
* Requires a Venus OS / gui-v2 release that has the plugin system (merged Nov 2026; check your version). Dev-compile elsewhere: python3 <gui-v2>/tools/gui-v2-plugin-compiler.py --min-required-version v1.4.1 --settings VictronHatSettings.qml
* NOT tested: the QML was written from the published plugin docs and not run in gui-v2 (no Qt/gui-v2 build here). If a row shows "--", check the instance numbers (dcload = instance_dc 290 in diag.json).
* Classic GUI page is unchanged and keeps working.

## v3.0 - advanced display (both GUIs)
* Overview page: health dot + warning text, board config, 4 bar gauges (input V, 5 V output A, Pi A, T1) with fixed warn/critical colours.
* Sub-pages: Power rails and temperatures (bar gauges with limits), Trends (last 10 min bar history of Vin, 5 V A, Pi A, T1), Ports/VE.Can/outputs/inputs/all values; GUI v2 also has Controls (OUT1-4 relays, fan mode, buzzer, Installer access).
* vichat_diag.py: new /Diag/Level (0 OK, 1 warning, 2 critical), /Diag/WarnCount, /History/{Vin,Iout,Ipi,T1} (60 samples, 10 s, in memory).
* Classic GUI files: PageVictronHat*.qml, HatBar.qml, HatTrend.qml. GUI v2 plugin files: gui-v2/VictronHat/*.qml (HatGauge, HatSpark, HatHealth + pages).
* Limits: GUI v2 plugins cannot read the theme, so gauge colours are fixed; thresholds are fixed in the QML. Trends are bars, not a true line chart. NOT run on real Venus/Qt (no Qt here); expect small QML fixes on first run.

## v3.1 - overall and subsystem health
* vichatdiag publishes /Health/Score (0-100), /Health/Overall (-1 unknown, 0 OK, 1 warning, 2 critical), /Health/Summary and, per subsystem, /Health/<Input|Supply|Pi|Protection|Thermal|Sensors> plus /Health/<name>/Text (reason). vichat publishes /Health/Comms (ports, config, can0).
* Score = 100 - 10 per warning subsystem - 30 per critical subsystem. Limits: input <7.5 V / >33 V / >5 A critical, <9 V / >30 V / >4.25 A warning; 5 V <4.7 V critical, <4.85 V warning, load >4.0 A warning, >4.6 A critical; Pi 5 V <4.75 V, Pi current >3.0 A warning, >3.3 A critical; PTC tripped = critical, fuse/FET drop >0.6 V warning; temperature >60 C warning, >70 C critical; 3.3 V rail outside 3.2-3.4 V warning, 3.1-3.5 V critical.
* Overview page (both GUIs): score with state (HEALTHY/WARNING/CRITICAL), colour bar, one-line summary, then 7 subsystem rows (dot + reason), board config, live gauges, sub-pages.
* The health logic was unit-tested offline with sample values; the QML is still not run on a real Venus.

## v3.2 - Venus OS system page, label fixes
* vichat publishes /System/* (Model, Venus version, Kernel, Uptime, CpuCores, CpuMHz, CpuMaxMHz, CpuLoadPct, Load1, CpuTempC, RamTotalMB, RamUsedMB, RamPct, SwapPct, DataPct, RootPct, Governor, Throttled/PiVolt from vcgencmd if present) and /Health/System (CPU >70/80 C, RAM >90 %, /data >90 %, Pi under-voltage/throttled).
* New page "Venus OS system: CPU, RAM, storage" in both GUIs and a "Venus OS system" row in the health list. Values that the image does not provide (e.g. cpufreq or vcgencmd) show "--".
* Fixes for board v27.6 names: display PTC is F101 (1.5 A hold), input fuse is F102 (7 A), relay/fan PTC is F601 (1.1 A hold). Labels corrected; relay/fan gauge limits now 0.9 A warning / 1.1 A critical; new Protection warnings near the F601 and F101 trip currents.

## v4.0 - board v28.0 (no ADC diagnostics, no LEDs, no protection parts)
* For HAT board v28.0 (EEPROM product_ver 0x0F00). Board v28.0 has no MCP3208 ADCs, no current/voltage/temperature sensing, no LEDs.
* Removed: vichatdiag service and vichat_diag.py (setup stops and deletes an old /service/vichatdiag), the power/temperature/trends pages and gauges in both GUIs.
* Kept: Venus OS system page (CPU speed, load, temperature, RAM, swap, /data, root fs, throttling), ports and VE.Can, OUT1-4 relays, fan, buzzer, IN1-4.
* Overall health now from two parts: Ports/VE.Can and Venus OS system (/Health/Score, /Health/Overall, /Health/Summary on com.victronenergy.vichat).
* Fan auto mode (OUT5) now follows the Pi CPU temperature: on at 65 C, off at 55 C (diag.json). A user copy in /data/setupOptions/VictronHat/diag.json overrides this.
* IN1-IN4 are direct 3.3 V inputs on board v28.0 (GPIO5/6/13/19, 4.7k pull-up, 1k series, active low). Never apply more than 3.3 V.
* Node-RED flow: the diagnostics node now shows the /System values.
* Older boards (v27.x with ADCs) should stay on package v3.2.

## v4.1 - board v28.2 (fan switched by a MOSFET, U101 on a 5 mm air gap)
* Fan (OUT5, J603) default is now ON (diag.json fan_mode 1): the v28.2 thermal limits assume the fan is running. Auto (2, CPU temperature) and Off (0) are still selectable in both GUIs.
* Board v28.2 drives the fan with Q601 (AO3400A) from GPIO23 instead of ULN2003 channels 5/7; same GPIO, same polarity (high = on), no software change needed.
* 5 V load limits for the HAT to stay <= 45 C at 30 C ambient (fan on): 7 V in 2.0 A, 12 V in 1.7 A, 24 V in 1.3 A (see SIMULATION/THERMAL-v28.2-30C.md).

## v4.2 - final package for board v28.2
* GUI v2 label "Opto inputs" is now "Digital inputs (3.3 V, active low)". EEPROM/PROGRAMMING text corrected: power the HAT from X101 only, never USB-C. Node-RED flow still has an unused "HAT analog" node (no ADC on v28.x). Code otherwise = v4.1.
