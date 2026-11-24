# mk11.py - relay extension v1.2: 85 x 40 mm, 4 layers (1 / 0.5 / 0.5 / 1 oz), no fan opening,
# four fan holes (HAT MH5-MH8), SPST G5Q-1A relays, 6-pin header J5 above HAT J601 (short cable). Searches terminal pin orders until the contacts route.
import sys, json, itertools, time
sys.path.insert(0, '/home/claude/ext/work/lib')
import pcbnew, pl, rt, ncls
from shapely.geometry import Point
K = '/home/claude/ext/relay-ext-v1.2/kicad'
PCB = K + '/victron-hat-relay-ext.kicad_pcb'; PRO = K + '/victron-hat-relay-ext.kicad_pro'
LIBD = K + '/relay-ext.pretty'
F, B, I1, I2 = pl.F, pl.B, pl.I1, pl.I2
DY = 8.0                       # extension y = HAT y - 8 (extension covers HAT y 8..48)
W_, H_, R = 85.0, 40.0, 1.0
WC = 2.0                       # contact track width per outer layer (F and B in parallel)

def write_pro():
    d = json.load(open('/home/claude/ext/work/hat.kicad_pro'))
    d['meta']['filename'] = 'victron-hat-relay-ext.kicad_pro'
    ns = d['net_settings']; tmpl = dict(ns['classes'][0]); ns['classes'] = []
    for name, tw, cl, vd, vdr, nets, desc in ncls.CLASSES:
        c = dict(tmpl); c.update(name=name, track_width=tw, clearance=cl, via_diameter=vd, via_drill=vdr); ns['classes'].append(c)
    ns['netclass_patterns'] = [{'netclass': name, 'pattern': n} for name, tw, cl, vd, vdr, nets, desc in ncls.CLASSES for n in nets]
    ns['netclass_assignments'] = None
    d['board']['design_settings']['rules']['min_copper_edge_clearance'] = 0.5
    d['board']['design_settings']['track_widths'] = [0.0, 0.25, 0.4, 0.6, 2.0]
    d['board']['design_settings']['via_dimensions'] = [{'diameter': 0.0, 'drill': 0.0}, {'diameter': 0.6, 'drill': 0.3}]
    d['boards'] = []; d['text_variables'] = {}
    json.dump(d, open(PRO, 'w'), indent=2)

# physical layout (extension coordinates, mm)
YO = 30.5                                   # relay origin (coil pad 1) row; rotation 90: courtyard y 10.8..32.45
REL = {1: (10.15, 90), 2: (32.8, 90), 3: (53.85, 90), 4: (65.85, 90)}      # relay origin x, rotation
YT = 0.1 + 4.66                              # top-edge terminal pin row (rotation 180, wire entry at the top edge)
TERM = {n: (REL[n][0] + 1.95 - 3.04 - 0.1 - 0.0, YT, 180) for n in REL}   # pin-1 x at the column right side
HOLES = {'H1': (17.0, 12.0 - DY), 'H2': (41.0, 12.0 - DY), 'H3': (17.0, 36.0 - DY), 'H4': (41.0, 36.0 - DY)}
J5 = (14.0, 34.95)                            # 6-pin header, mating side over the bottom edge, above HAT J601
SMALL = {n: 14.0 + 4.0 * (n - 1) for n in range(1, 5)}                    # rows for R / LED / D (right zone)
def set_rot(n, rot): pass

def new_board():
    b = pcbnew.BOARD(); b.SetCopperLayerCount(4)
    pcbnew.SaveBoard(PCB, b); write_pro(); b = pcbnew.LoadBoard(PCB); pl.b = b; return b

def shape(b, kind, layer, **k):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(kind); s.SetLayer(layer); s.SetWidth(int(0.1e6))
    if kind == pcbnew.SHAPE_T_SEGMENT: s.SetStart(pl.P(*k['a'])); s.SetEnd(pl.P(*k['c']))
    else:
        s.SetCenter(pl.P(*k['c'])); s.SetStart(pl.P(*k['a'])); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T), True)
    b.Add(s)

def outline(b):
    E, S, A = pcbnew.Edge_Cuts, pcbnew.SHAPE_T_SEGMENT, pcbnew.SHAPE_T_ARC
    for a, c in (((R, 0), (W_ - R, 0)), ((W_, R), (W_, H_ - R)), ((W_ - R, H_), (R, H_)), ((0, H_ - R), (0, R))): shape(b, S, E, a=a, c=c)
    for c, a in (((R, R), (0, R)), ((W_ - R, R), (W_ - R, 0)), ((W_ - R, H_ - R), (W_, H_ - R)), ((R, H_ - R), (R, H_))): shape(b, A, E, c=c, a=a)

def add(b, name, ref, val, x, y, rot, nets=None):
    f = pcbnew.FootprintLoad(LIBD, name); f.SetReference(ref); f.SetValue(val); b.Add(f)
    f.SetPosition(pl.P(x, y)); f.SetOrientationDegrees(rot)
    for p in f.Pads():
        if nets and p.GetNumber() in nets: p.SetNet(pl.net(nets[p.GetNumber()]))
    return f

def t1_pose():
    """left-edge terminal: wire entry facing the left edge, pins vertical"""
    b = pcbnew.BOARD()
    for rot in (90, 270):
        f = pcbnew.FootprintLoad(LIBD, 'TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal'); b.Add(f)
        f.SetPosition(pcbnew.VECTOR2I(0, 0)); f.SetOrientationDegrees(rot)
        cy = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
        p1 = [p for p in f.Pads() if p.GetNumber() == '1'][0].GetPosition(); p3 = [p for p in f.Pads() if p.GetNumber() == '3'][0].GetPosition()
        front = (p1.x - cy.GetX()) / 1e6
        if abs(front - 5.1) < 0.05: return rot, (p3.y - p1.y) / 1e6, cy.GetY() / 1e6, cy.GetBottom() / 1e6
    raise Exception('no T1 pose')


def pads_xy(ref):
    f = [q for q in pl.b.GetFootprints() if q.GetReference() == ref][0]
    return {p.GetNumber(): pl.padxy(p) for p in f.Pads()}

def build(perm):
    """perm[n] = functions on terminal pins 1..2, e.g. ('COM','NO')"""
    b = new_board(); outline(b)
    for h, (x, y) in HOLES.items():
        f = add(b, 'MountingHole_3.2mm_Fan', h, 'M2.5 3.2 mm', x, y, 0); f.Reference().SetVisible(False)
    add(b, 'PhoenixContact_MC_1,5_6-G-3.5_1x06_P3.50mm_Horizontal', 'J5', 'MC 1,5/6-G-3.5 (cable to HAT J601)', J5[0], J5[1], 0,
        {'1': '/OUT1', '2': '/OUT2', '3': '/OUT3', '4': '/OUT4', '5': '+5V', '6': 'GND'})
    for n in range(1, 5):
        xr, rot = REL[n]
        add(b, 'Relay_SPST_Omron-G5Q-1A', 'K%d' % n, 'G5Q-1A4-EU DC5', xr, YO, rot,
            {'1': '/OUT%d' % n, '5': '+5V', '2': '/CH%d_COM' % n, '3': '/CH%d_NO' % n})
        x, y, trot = TERM[n]
        add(b, 'TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal', 'J%d' % n, 'MKDS 1,5/2-5.08', x, y, trot,
            {str(i + 1): '/CH%d_%s' % (n, fn) for i, fn in enumerate(perm[n])})
        ys = SMALL[n]
        add(b, 'R_0603_1608Metric', 'R%d' % n, '1k', 72.0, ys, 0, {'1': '+5V', '2': 'Net-(LED%d-A)' % n})
        add(b, 'LED_0603_1608Metric', 'LED%d' % n, 'green', 75.3, ys, 180, {'1': '/OUT%d' % n, '2': 'Net-(LED%d-A)' % n})
        add(b, 'D_SOD-323', 'D%d' % n, '1N4148WS', 79.1, ys, 180, {'1': '+5V', '2': '/OUT%d' % n})
    for (x, y) in HOLES.values():   # rule areas: no copper on the outer layers under screw head / sleeve
        z = pcbnew.ZONE(b); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET(); ls.AddLayer(F); ls.AddLayer(B); z.SetLayerSet(ls)
        ol = z.Outline(); ol.NewOutline()
        for k in range(32):
            a = 2 * 3.14159265 * k / 32; ol.Append(pl.P(x + 3.0 * __import__('math').cos(a), y + 3.0 * __import__('math').sin(a)))
        b.Add(z)
    return b

def route(netn, layers, w, lcost=None, viacost=3.0):
    """connect all pads of a net on the given layers; returns number of failed connections"""
    ps = [p for f in pl.b.GetFootprints() for p in f.Pads() if p.GetNetname() == netn]
    ps.sort(key=lambda p: pl.padxy(p))
    done = [ps[0]]; fails = 0
    for p in ps[1:]:
        # no copper under the M2.5 screw head (top) or the spacer sleeve (bottom): 3.0 mm radius
        ko = [('', l, Point(x, y).buffer(2.5, 32)) for (x, y) in HOLES.values() for l in (F, B)]
        ko += [('', l, Point(x, y).buffer(1.6, 32)) for (x, y) in HOLES.values() for l in (I1, I2)]   # NPTH wall on inner layers
        Rr = rt.Router((0, 0, W_, H_), g=0.1, layers=layers, edge=0.5, extra_obst=ko)
        dn = {q.m_Uuid.AsString() for q in done}
        starts = [t for t in rt.net_targets(netn, exclude=lambda q: q.m_Uuid.AsString() not in dn) if t[0] in layers]
        goals = [t for t in rt.pad_target(p) if t[0] in layers]
        items = Rr.route(netn, starts, goals, w=w, clear=ncls.cls_of(netn)[2], via_d=0.6, via_drill=0.3, viacost=viacost, lcost=lcost)
        if items is None: fails += 1; continue
        rt.commit(netn, items, w); done.append(p)
    return fails

if __name__ == '__main__':
    t0 = time.time()
    perms = [('COM', 'NO'), ('NO', 'COM')]
    order = [1, 2, 3, 4]
    def ok_for(choice, upto):
        build(choice)
        for m in order[:upto]:
            for fn in ('COM', 'NO'):
                if route('/CH%d_%s' % (m, fn), (F,), WC): return False
        return True
    def dfs(k, choice):
        if k == len(order): return choice
        n = order[k]
        for pm in perms:
            c = dict(choice); c[n] = pm
            if ok_for(c, k + 1):
                r = dfs(k + 1, c)
                if r: return r
        return None
    res = dfs(0, {n: perms[0] for n in order})
    print('result', res, '%.0f s' % (time.time() - t0))
    if res: json.dump({'perm': {str(n): list(v) for n, v in res.items()}, 'rot': {str(n): 90 for n in REL}}, open('/home/claude/ext/work/choice12.json', 'w'))
