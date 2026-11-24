# pcb helper library (KiCad 7 pcbnew). Design mm = internal/1e6 - 20
import pcbnew, math, json, re, collections
from shapely.geometry import Point, LineString, Polygon, box as sbox, MultiPolygon
from shapely.ops import unary_union
OX,OY=20.0,20.0
def P(x,y): return pcbnew.VECTOR2I(int(round((x+OX)*1e6)),int(round((y+OY)*1e6)))
def D(v): return (v.x/1e6-OX, v.y/1e6-OY)
def mm(v): return v/1e6
F,B,I1,I2=pcbnew.F_Cu,pcbnew.B_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu
CU=[F,I1,I2,B]
LNAME={F:'F',I1:'In1',I2:'In2',B:'B'}
b=None
MASTER_PRO='/tmp/v272master.kicad_pro'
def load(path):
    global b
    import shutil, os
    if MASTER_PRO and os.path.exists(MASTER_PRO): shutil.copy(MASTER_PRO,path.replace('.kicad_pcb','.kicad_pro'))
    if os.path.exists('/tmp/v270.kicad_dru'): shutil.copy('/tmp/v270.kicad_dru',path.replace('.kicad_pcb','.kicad_dru'))
    b=pcbnew.LoadBoard(path); return b
def save(path):
    import shutil
    pcbnew.SaveBoard(path,b)
    if MASTER_PRO: shutil.copy(MASTER_PRO,path.replace('.kicad_pcb','.kicad_pro'))
    import os
    if os.path.exists('/tmp/v270.kicad_dru'): shutil.copy('/tmp/v270.kicad_dru',path.replace('.kicad_pcb','.kicad_dru'))
def net(name):
    n=b.FindNet(name)
    if n is None:
        n=pcbnew.NETINFO_ITEM(b,name); b.Add(n); n=b.FindNet(name)
    return n
def fp(ref):
    for f in b.GetFootprints():
        if f.GetReference()==ref: return f
    return None
def pad(ref,num,pth=None):
    f=fp(ref); ps=[p for p in f.Pads() if p.GetNumber()==str(num)]
    if pth is not None: ps=[p for p in ps if (p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH)==pth]
    return ps[0]
def padxy(p): return D(p.GetPosition())
def track(netname,layer,pts,w):
    n=net(netname); out=[]
    for a,c in zip(pts[:-1],pts[1:]):
        if abs(a[0]-c[0])<1e-6 and abs(a[1]-c[1])<1e-6: continue
        t=pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetLayer(layer); t.SetWidth(int(round(w*1e6))); t.SetNet(n); b.Add(t); out.append(t)
    return out
def via(netname,x,y,d=0.6,drill=0.3):
    v=pcbnew.PCB_VIA(b); v.SetPosition(P(x,y)); v.SetWidth(int(round(d*1e6))); v.SetDrill(int(round(drill*1e6))); v.SetNet(net(netname)); v.SetViaType(pcbnew.VIATYPE_THROUGH); b.Add(v); return v
def tracks(nets=None,boxr=None,layers=None,vias=True,segs=True):
    out=[]
    for t in b.GetTracks():
        isv=t.GetClass()=='PCB_VIA'
        if isv and not vias: continue
        if (not isv) and not segs: continue
        if nets is not None and t.GetNetname() not in nets: continue
        if layers is not None and not isv and t.GetLayer() not in layers: continue
        if boxr is not None:
            x0,y0,x1,y1=boxr
            if isv:
                x,y=D(t.GetPosition())
                if not (x0<=x<=x1 and y0<=y<=y1): continue
            else:
                a=D(t.GetStart()); c=D(t.GetEnd())
                if not LineString([a,c]).intersects(sbox(x0,y0,x1,y1)): continue
        out.append(t)
    return out
def rip(nets=None,boxr=None,layers=None,vias=True):
    ts=tracks(nets,boxr,layers,vias); [b.RemoveNative(t) for t in ts]; return len(ts)
def tgeom(t):
    if t.GetClass()=='PCB_VIA':
        return Point(*D(t.GetPosition())).buffer(t.GetWidth()/2e6,16)
    return LineString([D(t.GetStart()),D(t.GetEnd())]).buffer(t.GetWidth()/2e6,8) if t.GetStart()!=t.GetEnd() else Point(*D(t.GetStart())).buffer(t.GetWidth()/2e6,8)
_PG={}
def pgeom(p,layer=None):
    k=(p.m_Uuid.AsString(),p.GetPosition().x,p.GetPosition().y,p.GetOrientation().AsDegrees())
    if k in _PG: return _PG[k]
    g=_pgeom(p); _PG[k]=g; return g
def _pgeom(p):
    sh=p.GetEffectivePolygon()
    polys=[]
    for i in range(sh.OutlineCount()):
        o=sh.Outline(i); pts=[D(o.CPoint(k)) for k in range(o.PointCount())]
        if len(pts)>=3: polys.append(Polygon(pts))
    g=unary_union(polys) if polys else Point(*padxy(p)).buffer(0.1)
    return g
def player(p):
    return [l for l in CU if p.IsOnLayer(l)]
def add_fp(libdir,name,ref,val,x,y,rot=0,back=True,nets=None,lcsc=None):
    f=pcbnew.FootprintLoad(libdir,name)
    if f is None: raise Exception('no fp '+libdir+name)
    f.SetReference(ref); f.SetValue(val)
    b.Add(f)
    if back: f.Flip(f.GetPosition(),False)
    f.SetPosition(P(x,y)); f.SetOrientationDegrees(rot)
    if nets:
        for p in f.Pads():
            if p.GetNumber() in nets: p.SetNet(net(nets[p.GetNumber()]))
    if lcsc: f.SetField('LCSC',lcsc) if hasattr(f,'SetField') else None
    return f
STD='/usr/share/kicad/footprints/'
def drc(path_rpt,fill=True):
    if fill:
        for _ in range(2): b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        b.BuildConnectivity()
    pcbnew.WriteDRCReport(b,path_rpt,pcbnew.EDA_UNITS_MILLIMETRES,True)
    t=open(path_rpt).read()
    c=collections.Counter(re.findall(r'^\[(\w+)\]',t,re.M))
    unc=re.search(r'\*\* Found (\d+) unconnected',t).group(1)
    return dict(c),int(unc),t
def drc_items(t,kinds=None):
    items=[]
    for blk in re.split(r'\n(?=\[)',t):
        m=re.match(r'\[(\w+)\]: (.*)',blk)
        if not m: continue
        if kinds and m.group(1) not in kinds: continue
        locs=re.findall(r'@\(([-\d.]+) mm, ([-\d.]+) mm\): (.*)',blk)
        items.append((m.group(1),m.group(2),[(float(a)-OX,float(c)-OY,d) for a,c,d in locs]))
    return items
def net_items(netn,with_zones=False):
    items=[]   # (kind, obj, layers set, geom)
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname()==netn: items.append(('pad',p,set(player(p)),pgeom(p)))
    for t in b.GetTracks():
        if t.GetNetname()!=netn: continue
        if t.GetClass()=='PCB_VIA': items.append(('via',t,set(CU),tgeom(t)))
        else: items.append(('trk',t,{t.GetLayer()},tgeom(t)))
    if with_zones:
        for z in b.Zones():
            if z.GetNetname()!=netn or not z.IsFilled(): continue
            for l in CU:
                if not z.IsOnLayer(l): continue
                ps=z.GetFilledPolysList(l)
                for i in range(ps.OutlineCount()):
                    o=ps.Outline(i); pts=[D(o.CPoint(k)) for k in range(o.PointCount())]
                    if len(pts)>2: items.append(('zone',z,{l},Polygon(pts).buffer(0)))
    return items
def components(netn,with_zones=False):
    it=net_items(netn,with_zones); n=len(it); par=list(range(n))
    def f(i):
        while par[i]!=i: par[i]=par[par[i]]; i=par[i]
        return i
    from shapely.strtree import STRtree
    tree=STRtree([x[3] for x in it])
    for i,x in enumerate(it):
        for j in tree.query(x[3]):
            j=int(j)
            if j<=i: continue
            y=it[j]
            if x[2]&y[2] and x[3].distance(y[3])<1e-4: par[f(i)]=f(j)
    comps={}
    for i in range(n): comps.setdefault(f(i),[]).append(it[i])
    return list(comps.values())
def prune(nets,keep_vias_on_zone=True,verbose=False):
    """remove dangling track ends (iteratively); vias with <1 connection removed unless they touch a same-net zone layer"""
    tot=0
    for netn in nets:
        zl=[]
        for z in b.Zones():
            if z.GetNetname()!=netn: continue
            ol=z.Outline()
            for i in range(ol.OutlineCount()):
                o=ol.Outline(i); poly=Polygon([D(o.CPoint(k)) for k in range(o.PointCount())])
                zl.append(({l for l in CU if z.IsOnLayer(l)},poly))
        while True:
            it=net_items(netn,with_zones=False); rem=[]
            for x in it:
                if x[0]!='trk': continue
                t=x[1]; ends=[Point(*D(t.GetStart())),Point(*D(t.GetEnd()))]
                for e in ends:
                    ok=any((x[2]&zs) and zp.contains(e) for zs,zp in zl)
                    if ok: continue
                    for y in it:
                        if y[1] is t or y[0]=='zone' and False: continue
                        if y[1] is t: continue
                        if not (y[2]&x[2]): continue
                        if y[0]=='trk':
                            yt=y[1]; 
                            if e.distance(Point(*D(yt.GetStart())))<1e-3 or e.distance(LineString([D(yt.GetStart()),D(yt.GetEnd())]) if yt.GetStart()!=yt.GetEnd() else Point(*D(yt.GetStart())))<=yt.GetWidth()/2e6: ok=True; break
                        elif y[0]=='zone': continue
                        else:
                            if y[3].distance(e)<1e-3: ok=True; break
                    if not ok: rem.append(t); break
            if not rem: break
            for t in rem: b.RemoveNative(t)
            tot+=len(rem)
    return tot
def add_zone(template_net,template_layer,netn,layer,poly,prio):
    tz=[z for z in b.Zones() if z.GetNetname()==template_net and z.GetLayer()==template_layer][0]
    z=tz.Duplicate()
    try: z=pcbnew.Cast_to_ZONE(z)
    except Exception: pass
    z.SetNet(net(netn)); z.SetLayer(layer)
    ol=z.Outline(); ol.RemoveAllContours(); ol.NewOutline()
    for x,y in poly: ol.Append(P(x,y))
    z.SetAssignedPriority(prio); b.Add(z); return z

def prune_vias(nets):
    n=0
    for netn in nets:
        zl=set()
        for z in b.Zones():
            if z.GetNetname()==netn: zl|={l for l in CU if z.IsOnLayer(l)}
        if zl: continue   # plane nets: vias may stitch to zones
        it=net_items(netn)
        for x in it:
            if x[0]!='via': continue
            c=Point(*D(x[1].GetPosition()))
            con=[y for y in it if y[1] is not x[1] and y[0] in ('trk','pad') and y[3].distance(c)<x[1].GetWidth()/2e6]
            pads=[y for y in con if y[0]=='pad']
            if not con or (not pads and len(con)<=1): b.RemoveNative(x[1]); n+=1
    return n
def prune_all(nets):
    tot=0
    for _ in range(6):
        a=prune(nets); c=prune_vias(nets); d=0; tot+=a+c+d
        if a+c+d==0: break
    return tot
def prune_tiny(nets,lmax=0.2):
    n=0
    for netn in nets:
        ts=[t for t in b.GetTracks() if t.GetNetname()==netn and t.GetClass()!='PCB_VIA']
        for t in ts:
            a=Point(*D(t.GetStart())); c=Point(*D(t.GetEnd()))
            if a.distance(c)>lmax: continue
            for u in ts:
                if u is t: continue
                if u.GetLayer()!=t.GetLayer(): continue
                ln=LineString([D(u.GetStart()),D(u.GetEnd())]) if u.GetStart()!=u.GetEnd() else Point(*D(u.GetStart()))
                if ln.distance(a)<=u.GetWidth()/2e6 and ln.distance(c)<=u.GetWidth()/2e6:
                    # is t an endpoint-bridge? keep if another track/pad ends exactly at its far end
                    others=[v for v in ts if v is not t and v is not u and (Point(*D(v.GetStart())).distance(a)<1e-3 or Point(*D(v.GetEnd())).distance(a)<1e-3 or Point(*D(v.GetStart())).distance(c)<1e-3 or Point(*D(v.GetEnd())).distance(c)<1e-3)]
                    if not others:
                        b.RemoveNative(t); n+=1; break
    return n

def drc_cleanup(nets=None,rounds=10,path='/tmp/_dc.txt'):
    tot=0
    for _ in range(rounds):
        c,u,t=drc(path,fill=True)
        rem=[]
        for kind,msg,locs in drc_items(t,['track_dangling','via_dangling']):
            x,y,desc=locs[0]
            m=re.search(r'\[([^\]]+)\]',desc); n=m.group(1) if m else None
            if nets is not None and n not in nets: continue
            for tr in b.GetTracks():
                if tr.GetNetname()!=n: continue
                if kind=='via_dangling' and tr.GetClass()=='PCB_VIA' and Point(*D(tr.GetPosition())).distance(Point(x,y))<1e-3: rem.append(tr)
                if kind=='track_dangling' and tr.GetClass()!='PCB_VIA':
                    ml=re.search(r'length ([\d.]+) mm',desc); L_=float(ml.group(1)) if ml else None
                    if (Point(*D(tr.GetStart())).distance(Point(x,y))<1e-3 or Point(*D(tr.GetEnd())).distance(Point(x,y))<1e-3) and (L_ is None or abs(tr.GetLength()/1e6-L_)<2e-3) and LNAME[tr.GetLayer()]+'.Cu' in desc: rem.append(tr)
        rem=list({id(r):r for r in rem}.values())
        if not rem: break
        for r in rem: b.RemoveNative(r)
        tot+=len(rem)
    return tot
_OUT=None
def outline():
    global _OUT
    if _OUT is None:
        ps=pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
        o=ps.Outline(0); _OUT=Polygon([D(o.CPoint(k)) for k in range(o.PointCount())])
    return _OUT
