# grid A* router: octilinear tracks on F/B/In2 with through vias
import heapq, math, numpy as np
from PIL import Image, ImageDraw
import pcbnew
import pl
from pl import D, P, F, B, I1, I2, CU
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, box as sbox
from shapely.ops import unary_union
DIRS=[(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
class Router:
    def __init__(self,region,g=0.05,layers=(F,B,I2),zone_obst=None,edge=0.55,extra_obst=None):
        self.b=pl.b; self.x0,self.y0,self.x1,self.y1=region; self.g=g; self.layers=list(layers)
        self.nx=int(round((self.x1-self.x0)/g))+1; self.ny=int(round((self.y1-self.y0)/g))+1
        R=sbox(self.x0-3,self.y0-3,self.x1+3,self.y1+3)
        self.obs={l:[] for l in CU}; self.holes=[]; self.smdpads=[]; self.innerzones=[]
        for f in self.b.GetFootprints():
            for p in f.Pads():
                g_=pl.pgeom(p)
                if not g_.intersects(R): continue
                for l in pl.player(p): self.obs[l].append((p.GetNetname(),g_))
                if p.GetAttribute()==pcbnew.PAD_ATTRIB_SMD: self.smdpads.append((p.GetNetname(),g_))
                if p.GetDrillSize().x>0:
                    self.holes.append((p.GetNetname(),Point(*pl.padxy(p)).buffer(max(p.GetDrillSize().x,p.GetDrillSize().y)/2e6,16)))
        for t in self.b.GetTracks():
            g_=pl.tgeom(t)
            if not g_.intersects(R): continue
            if t.GetClass()=='PCB_VIA':
                for l in CU: self.obs[l].append((t.GetNetname(),g_))
                self.holes.append((t.GetNetname(),Point(*D(t.GetPosition())).buffer(t.GetDrillValue()/2e6,16)))
            else: self.obs[t.GetLayer()].append((t.GetNetname(),g_))
        # zones that act as obstacles: list of (net, layer) or None -> default: all zones except full planes
        for z in self.b.Zones():
            if z.GetIsRuleArea(): 
                continue
            key=(z.GetNetname(),pl.LNAME.get(z.GetLayer()))
            if zone_obst is not None and key not in zone_obst: continue
            ol=z.Outline()
            for i in range(ol.OutlineCount()):
                o=ol.Outline(i); poly=Polygon([D(o.CPoint(k)) for k in range(o.PointCount())])
                for l in CU:
                    if z.IsOnLayer(l):
                        self.obs[l].append((z.GetNetname(),poly))
                        if l in (I1,I2): self.innerzones.append(id(poly))
        if extra_obst:
            for netn,l,geo in extra_obst: self.obs[l].append((netn,geo))
        bb=self.b.GetBoardEdgesBoundingBox()
        self.edge=sbox(bb.GetX()/1e6-pl.OX+edge,bb.GetY()/1e6-pl.OY+edge,bb.GetRight()/1e6-pl.OX-edge,bb.GetBottom()/1e6-pl.OY-edge)
    def raster(self,geoms):
        im=Image.new('1',(self.nx,self.ny),0); dr=ImageDraw.Draw(im)
        tx=lambda x,y:((x-self.x0)/self.g,(y-self.y0)/self.g)
        def drawp(pg,val):
            dr.polygon([tx(*c) for c in pg.exterior.coords],fill=val,outline=val)
            for h in pg.interiors: dr.polygon([tx(*c) for c in h.coords],fill=0,outline=0)
        for gg in geoms:
            if gg.is_empty: continue
            for pg in (gg.geoms if hasattr(gg,'geoms') else [gg]):
                if pg.geom_type=='Polygon': drawp(pg,1)
        return np.array(im,dtype=bool).T   # [ix,iy]
    def build(self,netn,w,clear,via_d,via_drill,hole_clear=0.3,same=()):
        import ncls
        same=set(same)|{netn}
        CL=lambda n: 0.5 if n=='' else max(clear,ncls.cls_of(n)[2])
        self.blk={}
        for l in self.layers:
            gs=[geo.buffer(CL(n)+w/2+0.01,8) for n,geo in self.obs[l] if n not in same]
            a=self.raster(gs)
            # board edge
            outside=~self.raster([self.edge.buffer(-w/2,4)])
            self.blk[l]=a|outside
        gs=[]
        for l in CU:
            gs+=[geo.buffer(CL(n)+via_d/2+0.01,8) for n,geo in self.obs[l] if n not in same and id(geo) not in self.innerzones]
        gs+=[geo.buffer(hole_clear+via_d/2+0.01,8) for n,geo in self.holes if n!=netn]
        gs+=[geo.buffer(hole_clear+via_drill/2+0.01,8) for n,geo in self.holes if n==netn]  # no via on top of same-net holes
        gs+=[geo.buffer(via_d/2+0.05,8) for n,geo in self.smdpads if n in same]       # no via-in-pad
        self.vblk=self.raster(gs)|~self.raster([self.edge.buffer(-via_d/2,4)])
    def cells(self,geo):
        a=self.raster([geo]); return list(zip(*np.nonzero(a)))
    def route(self,netn,starts,goals,w=0.25,clear=0.2,via_d=0.6,via_drill=0.3,viacost=2.0,bend=0.3,maxexp=None,same=(),noviazone=None,lcost=None,cellcost=None):
        import scipy.sparse as sp
        from scipy.sparse.csgraph import dijkstra
        self.build(netn,w,clear+0.03,via_d,via_drill,same=same)
        if noviazone is not None: self.vblk|=self.raster([noviazone])
        L=self.layers; nl=len(L); nx,ny=self.nx,self.ny; N=nx*ny
        goal=np.zeros((nl,nx,ny),bool); start=np.zeros((nl,nx,ny),bool)
        li={l:i for i,l in enumerate(L)}
        for l,geo in goals:
            if l in li: goal[li[l]]|=self.raster([geo])
        for l,geo in starts:
            if l in li: start[li[l]]|=self.raster([geo])
        if not goal.any() or not start.any(): return None
        free=np.stack([~self.blk[l] for l in L])|goal|start
        idx=np.arange(nl*N).reshape(nl,nx,ny)
        rows=[];cols=[];vals=[]
        for (dx,dy),c in (((1,0),1.0),((0,1),1.0),((1,1),1.4142),((1,-1),1.4142)):
            xs=slice(0,nx-dx); xd=slice(dx,nx)
            if dy>=0: ys=slice(0,ny-dy); yd=slice(dy,ny)
            else: ys=slice(-dy,ny); yd=slice(0,ny+dy)
            for k in range(nl):
                ok=free[k][xs,ys]&free[k][xd,yd]
                if dx and dy:
                    # no corner cutting
                    ok&=free[k][xd,ys]&free[k][xs,yd]
                a_=idx[k][xs,ys][ok]; b_=idx[k][xd,yd][ok]
                cc=c*((lcost or {}).get(L[k],1.0))
                if cellcost is not None and L[k] in cellcost:
                    M=cellcost[L[k]]; v_=cc*0.5*(M[xs,ys][ok]+M[xd,yd][ok])
                    rows+=[a_,b_]; cols+=[b_,a_]; vals+=[v_,v_]
                else:
                    rows+=[a_,b_]; cols+=[b_,a_]; vals+=[np.full(a_.size,cc),np.full(a_.size,cc)]
        vok=~self.vblk
        for k1 in range(nl):
            for k2 in range(k1+1,nl):
                ok=vok&free[k1]&free[k2]
                a_=idx[k1][ok]; b_=idx[k2][ok]
                rows+=[a_,b_]; cols+=[b_,a_]; vals+=[np.full(a_.size,viacost/self.g)]*2
        G=sp.csr_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(nl*N,nl*N))
        src=idx[start]
        dist,pred,srcs=dijkstra(G,directed=False,indices=src,min_only=True,return_predecessors=True)
        gi=idx[goal]; gd=dist[gi]
        if not np.isfinite(gd).any(): return None
        end=gi[np.argmin(gd)]
        path=[end]
        while pred[path[-1]]>=0: path.append(pred[path[-1]])
        path.reverse()
        P_=[(int(p//N),int((p%N)//ny),int(p%ny)) for p in path]
        X=lambda i:self.x0+i*self.g; Y=lambda i:self.y0+i*self.g
        runs=[]; cur=[P_[0]]
        for k in P_[1:]:
            if k[0]!=cur[-1][0]: runs.append(cur); cur=[k]
            else: cur.append(k)
        runs.append(cur)
        items=[]
        for ri,run in enumerate(runs):
            if ri>0: items.append(('via',X(run[0][1]),Y(run[0][2])))
            l=L[run[0][0]]; fr=free[run[0][0]]
            pts=self.smooth([(c[1],c[2]) for c in run],fr)
            for a,c in zip(pts[:-1],pts[1:]):
                if a!=c: items.append(('seg',l,X(a[0]),Y(a[1]),X(c[0]),Y(c[1])))
        return items
    def segfree(self,fr,a,c):
        dx=c[0]-a[0]; dy=c[1]-a[1]
        if not (dx==0 or dy==0 or abs(dx)==abs(dy)): return False
        n=max(abs(dx),abs(dy))
        if n==0: return True
        sx=(dx>0)-(dx<0); sy=(dy>0)-(dy<0)
        for i in range(n+1):
            if not fr[a[0]+sx*i,a[1]+sy*i]: return False
            if sx and sy and i<n and not (fr[a[0]+sx*(i+1),a[1]+sy*i] and fr[a[0]+sx*i,a[1]+sy*(i+1)]): return False
        return True
    def smooth(self,pts,fr):
        out=[pts[0]]; i=0; n=len(pts)
        while i<n-1:
            best=None
            for k in range(n-1,i,-1):
                a=pts[i]; c=pts[k]
                if self.segfree(fr,a,c): best=(k,None); break
                dx=c[0]-a[0]; dy=c[1]-a[1]; m=min(abs(dx),abs(dy)); sx=(dx>0)-(dx<0); sy=(dy>0)-(dy<0)
                hit=None
                for cor in ((a[0]+sx*m,a[1]+sy*m),(c[0]-sx*m,c[1]-sy*m)):
                    if self.segfree(fr,a,cor) and self.segfree(fr,cor,c): hit=cor; break
                if hit: best=(k,hit); break
                if k-i<=1: best=(k,None); break
            k,cor=best
            if cor and cor!=out[-1]: out.append(cor)
            out.append(pts[k]); i=k
        # merge collinear
        res=[out[0]]
        for j in range(1,len(out)-1):
            d1=(np.sign(out[j][0]-res[-1][0]),np.sign(out[j][1]-res[-1][1])); d2=(np.sign(out[j+1][0]-out[j][0]),np.sign(out[j+1][1]-out[j][1]))
            if d1!=d2: res.append(out[j])
        res.append(out[-1])
        return res
def commit(netn,items,w,via_d=0.6,via_drill=0.3):
    for it in items:
        if it[0]=='seg': pl.track(netn,it[1],[(round(it[2],4),round(it[3],4)),(round(it[4],4),round(it[5],4))],w)
        else: pl.via(netn,round(it[1],4),round(it[2],4),via_d,via_drill)
def pad_target(p,shrink=0.12):
    g=pl.pgeom(p).buffer(-shrink)
    return [(l,g) for l in pl.player(p)]
def net_targets(netn,exclude=None,layers=None):
    """all copper of net as goal/start geoms"""
    out=[]
    for f in pl.b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname()==netn and (exclude is None or not exclude(p)): out+=pad_target(p)
    for t in pl.b.GetTracks():
        if t.GetNetname()!=netn: continue
        if t.GetClass()=='PCB_VIA': out+=[(l,Point(*D(t.GetPosition())).buffer(t.GetWidth()/2e6-0.05)) for l in CU]
        else: out.append((t.GetLayer(),LineString([D(t.GetStart()),D(t.GetEnd())]).buffer(0.01) if t.GetStart()!=t.GetEnd() else Point(*D(t.GetStart())).buffer(0.01)))
    return out
