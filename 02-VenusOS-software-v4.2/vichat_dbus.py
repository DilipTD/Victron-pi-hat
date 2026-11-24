#!/usr/bin/env python3
# Publishes Victron Pi HAT status on dbus (com.victronenergy.vichat) for the
# classic (v1) GUI page "Victron HAT status".
import os, subprocess, sys, time
sys.path.insert(1, '/opt/victronenergy/dbus-systemcalc-py/ext/velib_python')
import dbus
from dbus.mainloop.glib import DBusGMainLoop
try:
    from gi.repository import GLib as gobject
except ImportError:
    import gobject
from vedbus import VeDbusService

PORTS = [("J301", "ttySC0"), ("J302", "ttySC1"), ("J401", "ttySC2"), ("J402", "ttySC3")]
BUZ = 24
FAN = 23            # board v25.0: OUT5 (ULN2003 ch.5+7) -> J603 fan header, 5 V / 2-pin
CONF = ['/data/VictronHat/diag.json', '/data/setupOptions/VictronHat/diag.json']   # 2nd = user copy, survives package updates
FANCFG = {'fan_mode': 1, 'fan_on_c': 65.0, 'fan_off_c': 55.0}   # mode 0 = off, 1 = on, 2 = auto (Pi CPU temperature; board v28.0 has no NTCs)
import json
for _f in CONF:
    try:
        _c = json.load(open(_f))
        FANCFG.update({k: _c[k] for k in FANCFG if k in _c})
    except Exception:
        pass

def run(args, t=3):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=t).stdout.strip()
    except Exception:
        return ""

def dget(svc, path):
    v = run(["dbus", "-y", svc, path, "GetValue"])
    return v.strip("'") if v else None

def rd(p):
    try:
        return open(p).read().strip()
    except Exception:
        return None

def gpio_base():
    g = os.environ.get("GPIO_SYSFS", "/sys/class/gpio")
    try:
        for c in sorted(os.listdir(g)):
            if c.startswith("gpiochip") and "bcm2835" in (rd(g + "/" + c + "/label") or ""):
                return g, int(rd(g + "/" + c + "/base"))
    except Exception:
        pass
    return g, 0

def gpio_write(v, pin=BUZ):
    try:
        g, base = gpio_base()
        open("%s/gpio%d/value" % (g, base + pin), "w").write(v)
        return True
    except Exception:
        return False

def hat_version():
    try:
        return int((rd(os.environ.get("HAT_DT", "/proc/device-tree/hat") + "/product_ver") or "0").strip("\x00 \n"), 16)
    except Exception:
        return 0
HAS_FAN = hat_version() >= 0x0700 or os.environ.get("VICHAT_FAN") == "1"

DBusGMainLoop(set_as_default=True)
s = VeDbusService('com.victronenergy.vichat', bus=dbus.SystemBus())
s.add_path('/Mgmt/ProcessName', 'vichat')
s.add_path('/Mgmt/ProcessVersion', '2.0')
s.add_path('/Mgmt/Connection', 'local')
s.add_path('/ProductName', 'Victron Pi HAT status')
s.add_path('/DeviceInstance', 0)   # MQTT: N/<portal>/vichat/0/...
s.add_path('/Connected', 1)
s.add_path('/Config', '')
for i in range(4):
    s.add_path('/Port/%d/Device' % i, '')
s.add_path('/Can/State', '')
s.add_path('/Can/Errors', '')
s.add_path('/Can/Devices', '')
def on_out(path, value):
    # /Out/<n>/State written (Node-RED, MQTT W/...) -> Venus relay n
    n = int(path.split('/')[2])
    try:
        v = 1 if int(value) else 0
    except Exception:
        return False
    run(["dbus", "-y", "com.victronenergy.system", "/Relay/%d/State" % n, "SetValue", str(v)])
    return True
for i in range(4):
    s.add_path('/Out/%d' % i, '')
    s.add_path('/In/%d' % i, '')
    s.add_path('/Out/%d/State' % i, None, writeable=True, onchangecallback=on_out)   # 0/1, writeable
    s.add_path('/In/%d/State' % i, None)                                             # 0/1

def on_buzzer(path, value):
    if value:
        gpio_write("1"); time.sleep(0.3); gpio_write("0")
        gobject.timeout_add(500, lambda: (s.__setitem__('/Buzzer/Test', 0), False)[1])
    return True
s.add_path('/Buzzer/Test', 0, writeable=True, onchangecallback=on_buzzer)

# ---- OUT5: fan header J603 (board v25.0 and later) ----
fan = {'on': None}
def fan_set(on):
    on = 1 if on else 0
    if fan['on'] != on and gpio_write(str(on), FAN):
        fan['on'] = on
    s['/Fan/State'] = fan['on'] if fan['on'] is not None else 0   # what the pin really is
def fan_eval():
    if not HAS_FAN:
        return
    m = s['/Fan/Mode']
    if m == 0:
        fan_set(0)
    elif m == 1:
        fan_set(1)
    else:                               # auto: hysteresis on the Pi CPU temperature (v28.0: no board NTCs)
        tc = rd('/sys/class/thermal/thermal_zone0/temp')
        t = round(int(tc) / 1000.0, 1) if tc and tc.lstrip('-').isdigit() else None
        s['/Fan/Temperature'] = t
        if t is None:
            fan_set(1)                  # sensor missing: fail safe, fan on
        elif t >= FANCFG['fan_on_c']:
            fan_set(1)
        elif t <= FANCFG['fan_off_c']:
            fan_set(0)
        elif fan['on'] is None:
            fan_set(0)
def on_fan_mode(path, value):
    try:
        v = int(value)
    except Exception:
        return False
    if v not in (0, 1, 2):
        return False
    gobject.timeout_add(50, lambda: (fan_eval(), False)[1])
    return True
s.add_path('/Fan/Present', 1 if HAS_FAN else 0)
s.add_path('/Fan/Mode', int(FANCFG['fan_mode']), writeable=True, onchangecallback=on_fan_mode,
           gettextcallback=lambda p, v: {0: 'Off', 1: 'On', 2: 'Auto'}.get(v, str(v)))
s.add_path('/Fan/State', 0, gettextcallback=lambda p, v: 'ON' if v else 'OFF')
s.add_path('/Fan/Temperature', None)
s.add_path('/Fan/OnC', FANCFG['fan_on_c'])
s.add_path('/Fan/OffC', FANCFG['fan_off_c'])
# ---- Venus OS / Raspberry Pi system stats ----
for k_, v_ in (('Model', ''), ('Kernel', ''), ('Venus', ''), ('Uptime', ''), ('CpuCores', None), ('CpuMHz', None), ('CpuMaxMHz', None), ('CpuLoadPct', None),
               ('Load1', None), ('CpuTempC', None), ('RamTotalMB', None), ('RamUsedMB', None), ('RamPct', None), ('SwapPct', None),
               ('DataTotalGB', None), ('DataPct', None), ('RootPct', None), ('Throttled', ''), ('PiVolt', ''), ('Governor', '')):
    s.add_path('/System/' + k_, v_)
s.add_path('/Health/System', -1)
s.add_path('/Health/System/Text', 'starting')
_cpu_prev = [None]
def cpu_pct():
    try:
        a = [int(x) for x in open('/proc/stat').readline().split()[1:8]]
        tot, idle = sum(a), a[3] + a[4]
        pv = _cpu_prev[0]; _cpu_prev[0] = (tot, idle)
        if pv and tot > pv[0]: return round(100.0 * (1 - (idle - pv[1]) / float(tot - pv[0])), 0)
    except Exception: pass
    return None
def sysstat():
    why, lv = [], 0
    s['/System/Model'] = (rd('/proc/device-tree/model') or '').strip('\x00')
    s['/System/Kernel'] = rd('/proc/sys/kernel/osrelease') or ''
    vv = rd('/opt/victronenergy/version')
    s['/System/Venus'] = (vv.splitlines()[0] if vv else '')
    up = rd('/proc/uptime')
    if up:
        sec = int(float(up.split()[0])); s['/System/Uptime'] = '%dd %02dh %02dm' % (sec // 86400, sec % 86400 // 3600, sec % 3600 // 60)
    s['/System/CpuCores'] = os.cpu_count()
    f = rd('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq') or rd('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq')
    s['/System/CpuMHz'] = int(f) // 1000 if f and f.isdigit() else None
    m = rd('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq')
    s['/System/CpuMaxMHz'] = int(m) // 1000 if m and m.isdigit() else None
    s['/System/Governor'] = rd('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor') or ''
    s['/System/CpuLoadPct'] = cpu_pct()
    la = rd('/proc/loadavg'); s['/System/Load1'] = float(la.split()[0]) if la else None
    tc = rd('/sys/class/thermal/thermal_zone0/temp')
    tcv = round(int(tc) / 1000.0, 1) if tc and tc.lstrip('-').isdigit() else None
    s['/System/CpuTempC'] = tcv
    if tcv is not None:
        if tcv > 80: lv = 2; why.append('CPU %.0f C' % tcv)
        elif tcv > 70: lv = max(lv, 1); why.append('CPU %.0f C' % tcv)
    mi = {}
    for ln in (rd('/proc/meminfo') or '').splitlines():
        k, _, v = ln.partition(':')
        try: mi[k] = int(v.split()[0])
        except Exception: pass
    if mi.get('MemTotal'):
        tot = mi['MemTotal']; used = tot - mi.get('MemAvailable', mi.get('MemFree', 0))
        s['/System/RamTotalMB'] = tot // 1024; s['/System/RamUsedMB'] = used // 1024; s['/System/RamPct'] = round(100.0 * used / tot, 0)
        if 100.0 * used / tot > 90: lv = max(lv, 1); why.append('RAM %.0f %%' % (100.0 * used / tot))
        st = mi.get('SwapTotal', 0)
        s['/System/SwapPct'] = round(100.0 * (st - mi.get('SwapFree', 0)) / st, 0) if st else 0
    try:
        d = os.statvfs('/data'); s['/System/DataTotalGB'] = round(d.f_blocks * d.f_frsize / 1e9, 1)
        dp = 100.0 * (1 - d.f_bavail / float(d.f_blocks)); s['/System/DataPct'] = round(dp, 0)
        if dp > 90: lv = max(lv, 1); why.append('/data %.0f %% full' % dp)
        r = os.statvfs('/'); s['/System/RootPct'] = round(100.0 * (1 - r.f_bavail / float(r.f_blocks)), 0)
    except Exception: pass
    th = run(['vcgencmd', 'get_throttled'])          # e.g. throttled=0x50005 (not on every image)
    if 'throttled=' in th:
        try:
            x = int(th.split('=')[1], 16); fl = []
            for bit, txt in ((0x1, 'under-voltage now'), (0x2, 'freq capped now'), (0x4, 'throttled now'), (0x8, 'soft temp limit now'),
                             (0x10000, 'under-voltage since boot'), (0x40000, 'throttled since boot')):
                if x & bit: fl.append(txt)
            s['/System/Throttled'] = th.split('=')[1]; s['/System/PiVolt'] = ', '.join(fl) if fl else 'OK'
            if x & 0x1: lv = 2; why.append('Pi under-voltage now')
            elif x & 0x4: lv = max(lv, 1); why.append('Pi throttled now')
            elif x & 0x50000: lv = max(lv, 1); why.append('Pi under-voltage/throttle since boot')
        except Exception: pass
    s['/Health/System'] = lv; s['/Health/System/Text'] = ', '.join(why) if why else 'OK'
s.add_path('/Health/Score', None)
s.add_path('/Health/Overall', -1)
s.add_path('/Health/Summary', 'starting')
def overall():
    parts = [('Ports/VE.Can', s['/Health/Comms'], s['/Health/Comms/Text']), ('System', s['/Health/System'], s['/Health/System/Text'])]
    known = [p for p in parts if p[1] is not None and p[1] >= 0]
    if not known: return
    s['/Health/Score'] = max(0, 100 - sum(30 if lv == 2 else 10 if lv == 1 else 0 for _, lv, _ in known))
    s['/Health/Overall'] = max(lv for _, lv, _ in known)
    bad = ['%s: %s' % (n, w) for n, lv, w in known if lv > 0]
    s['/Health/Summary'] = '; '.join(bad) if bad else 'All systems OK'
s.add_path('/Health/Comms', -1)          # -1 unknown, 0 OK, 1 warning, 2 critical
s.add_path('/Health/Comms/Text', 'starting')

def update():
    try:
        sysstat()
    except Exception:
        pass
    try:
        t = rd("/u-boot/config.txt") or ""
        hat = (rd(os.environ.get("HAT_DT","/proc/device-tree/hat")+"/product") or "").strip("\x00")
        if "Victron Pi HAT" in hat:
            ver = (rd(os.environ.get("HAT_DT","/proc/device-tree/hat")+"/product_ver") or "").strip("\x00")
            s['/Config'] = "EEPROM " + ver
        elif "VictronHat begin" in t and "sc16is752" in t and "mcp2515" in t:
            s['/Config'] = "OK (config.txt)"
        else:
            s['/Config'] = "MISSING - run setup"
        svcs = [x.strip() for x in run(["dbus", "-y"]).splitlines() if x.startswith("com.victronenergy.")]
        conn = {x: (dget(x, "/Mgmt/Connection") or "") for x in svcs}
        for i, (j, tty) in enumerate(PORTS):
            dev = None
            for x in svcs:
                if tty in conn[x]:
                    dev = dget(x, "/ProductName") or x.split(".", 2)[-1]
                    break
            s['/Port/%d/Device' % i] = dev if dev else ("Idle" if os.path.exists("/dev/" + tty) else "Missing")
        st = rd("/sys/class/net/can0/operstate")
        s['/Can/State'] = st if st else "not found"
        s['/Can/Errors'] = "rx %s / tx %s" % (rd("/sys/class/net/can0/statistics/rx_errors") or "-",
                                              rd("/sys/class/net/can0/statistics/tx_errors") or "-")
        s['/Can/Devices'] = str(len([x for x in svcs if "can" in conn[x].lower()]))
        lv, why = 0, []
        if s['/Config'].startswith('MISSING'): lv = 2; why.append('HAT config missing')
        miss = [str(i) for i in range(4) if s['/Port/%d/Device' % i] == 'Missing']
        if miss: lv = 2; why.append('ttySC%s missing' % ','.join(miss))
        if s['/Can/State'] == 'not found': lv = max(lv, 1); why.append('can0 not found')
        try:
            e = [int(x) for x in s['/Can/Errors'].replace('rx', '').replace('tx', '').replace('/', ' ').split() if x.isdigit()]
            if e and max(e) > 100: lv = max(lv, 1); why.append('CAN errors %d' % max(e))
        except Exception: pass
        s['/Health/Comms'] = lv; s['/Health/Comms/Text'] = ', '.join(why) if why else 'OK'
        for i in range(4):
            v = dget("com.victronenergy.system", "/Relay/%d/State" % i)
            s['/Out/%d' % i] = "n/a" if v is None else ("ON" if int(float(v)) == 1 else "OFF")
            if v is not None: s['/Out/%d/State' % i] = int(float(v))
        dins = [x for x in svcs if ".digitalinput" in x]
        for i in range(4):
            v = dget(dins[i], "/State") if i < len(dins) else None
            s['/In/%d' % i] = "n/a" if v is None else ("ACTIVE" if int(float(v)) % 2 == 1 else "inactive")
            if v is not None: s['/In/%d/State' % i] = int(float(v)) % 2
    except Exception:
        pass
    try:
        overall()
    except Exception:
        pass
    try:
        fan_eval()
    except Exception:
        pass
    return True

update()
gobject.timeout_add(3000, update)
gobject.MainLoop().run()
