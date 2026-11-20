import math,zipfile,os
lat0,lon0=-20.45,-54.62
def ll(x,y):
    a=6378137;f=1/298.257223563;e2=f*(2-f);s=math.sin(math.radians(lat0));w=math.sqrt(1-e2*s*s)
    M=a*(1-e2)/w**3;N=a/w
    return lon0+x/(N*math.cos(math.radians(lat0))*math.pi/180), lat0+y/(M*math.pi/180)
def rect(cx,cy,L,W,ang=0):
    r=math.radians(ang);pts=[]
    for dx,dy in [(-L/2,-W/2),(L/2,-W/2),(L/2,W/2),(-L/2,W/2),(-L/2,-W/2)]:
        x=cx+dx*math.cos(r)-dy*math.sin(r);y=cy+dx*math.sin(r)+dy*math.cos(r);pts.append(ll(x,y))
    return ' '.join(f'{a:.9f},{b:.9f},0' for a,b in pts)
pm=lambda n,g:f'<Placemark><name>{n}</name>{g}</Placemark>'
poly=lambda c:f'<Polygon><outerBoundaryIs><LinearRing><coordinates>{c}</coordinates></LinearRing></outerBoundaryIs></Polygon>'
line=' '.join(f'{a:.9f},{b:.9f},0' for a,b in [ll(-200,-150),ll(200,-150),ll(200,150)])
p=ll(30,-20)
k=f'''<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Fazenda Teste</name>
<Folder><name>Benfeitorias</name>
{pm('Galpão de máquinas',poly(rect(0,0,20,12,30)))}
{pm('Casa sede',poly(rect(-40,10,15,10)))}
{pm('Casa funcionário',poly(rect(-40,40,8,6)))}
{pm('Curral',poly(' '.join(f'{a:.9f},{b:.9f},0' for a,b in [ll(50+20*math.cos(t*math.pi/18),30+20*math.sin(t*math.pi/18)) for t in range(37)])))}
{pm('Cobertura curral',poly(rect(50,30,12,8)))}
{pm('Divisão 1',f"<LineString><coordinates>{' '.join(f'{a:.9f},{b:.9f},0' for a,b in [ll(50,10),ll(50,50)])}</coordinates></LineString>")}
{pm('Divisão 2',f"<LineString><coordinates>{' '.join(f'{a:.9f},{b:.9f},0' for a,b in [ll(50,30),ll(70,30)])}</coordinates></LineString>")}
{pm('Curral semicircular',poly(' '.join(f'{a:.9f},{b:.9f},0' for a,b in [ll(-120+15*math.cos(t*math.pi/18),-80+15*math.sin(t*math.pi/18)) for t in range(19)]+[ll(-135,-80)])))}
{pm('Tronco',f"<Point><coordinates>{ll(40,30)[0]},{ll(40,30)[1]},0</coordinates></Point>")}
{pm('Poço artesiano',f'<Point><coordinates>{p[0]},{p[1]},0</coordinates></Point>')}
</Folder>
{pm('Cerca divisa sul',f'<LineString><coordinates>{line}</coordinates></LineString>')}
{pm('Perímetro do imóvel',poly(rect(0,0,500,400)))}
</Document></kml>'''
open(os.path.join(os.path.dirname(__file__),'teste.kml'),'w').write(k)
with zipfile.ZipFile(os.path.join(os.path.dirname(__file__),'teste.kmz'),'w',zipfile.ZIP_DEFLATED) as z: z.writestr('doc.kml',k)
