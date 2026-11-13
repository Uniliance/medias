"""Visuel citation 1080x1350 dans le style du site uniliance.life.
Usage : python3 citation.py "Ligne 1|Ligne 2" "Fin en italique|ligne 2" sortie.jpg 76 "Le Labyrinthe des ombres"
Le | sépare les lignes. Polices (dossier polices/) : Cormorant Garamond 600 et 500 italique, Jost 400 et 500.
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1080,1350
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def hexc(h): return tuple(int(h[i:i+2],16) for i in (1,3,5))
stops=[(0,hexc('#B8D4E8')),(0.35,hexc('#D4C4B8')),(0.7,hexc('#E8C4A8')),(1,hexc('#F5D4B8'))]
bg=Image.new('RGB',(W,H)); px=bg.load()
for y in range(H):
    t=y/(H-1)
    for i in range(len(stops)-1):
        if stops[i][0]<=t<=stops[i+1][0]:
            c=lerp(stops[i][1],stops[i+1][1],(t-stops[i][0])/(stops[i+1][0]-stops[i][0])); break
    for x in range(W): px[x,y]=c
# golden halo bottom
halo=Image.new('L',(W,H),0); ImageDraw.Draw(halo).ellipse((240,1080,840,1560),fill=170)
halo=halo.filter(ImageFilter.GaussianBlur(120))
bg=Image.composite(Image.new('RGB',(W,H),(248,214,150)),bg,halo)
# card shadow + card
x0,y0,x1,y1=70,120,1010,1230
sh=Image.new('L',(W,H),0); ImageDraw.Draw(sh).rounded_rectangle((x0,y0+12,x1,y1+12),40,fill=60)
sh=sh.filter(ImageFilter.GaussianBlur(25))
bg=Image.composite(Image.new('RGB',(W,H),(150,120,100)),bg,sh)
card=Image.new('RGB',(W,H)); cp=card.load()
for y in range(H):
    c=lerp((245,242,238),(252,243,232),max(0,min(1,(y-y0)/(y1-y0))))
    for x in range(W): cp[x,y]=c
m=Image.new('L',(W,H),0); ImageDraw.Draw(m).rounded_rectangle((x0,y0,x1,y1),40,fill=240)
bg=Image.composite(card,bg,m)
d=ImageDraw.Draw(bg)
F=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','polices')+'/'
def spaced(text,font,y,fill,sp):
    w=sum(font.getlength(ch) for ch in text)+sp*(len(text)-1); x=(W-w)/2
    for ch in text:
        d.text((x,y),ch,font=font,fill=fill); x+=font.getlength(ch)+sp
def center(text,font,y,fill):
    d.text(((W-font.getlength(text))/2,y),text,font=font,fill=fill)
brown=hexc('#8B4513'); copper=hexc('#C17854'); ink=hexc('#3d3531')
chambre=sys.argv[4]; atelier=sys.argv[5]
spaced(f'ATELIER JAUNE · CHAMBRE {chambre}',ImageFont.truetype(F+'Jost500.ttf',36),226,brown,5)
d.line((470,299,610,299),fill=copper,width=3)
main=sys.argv[1].split('|'); ital=sys.argv[2].split('|'); out=sys.argv[3]
fm=ImageFont.truetype(F+'CG600.ttf',92); fi=ImageFont.truetype(F+'CG500i.ttf',92)
lh=108; gap=24
total=lh*len(main)+gap+lh*len(ital)
y=650-total/2+22
for l in main: center(l,fm,y,ink); y+=lh
y+=gap
for l in ital: center(l,fi,y,copper); y+=lh
d.line((470,997,610,997),fill=copper,width=3)
center(atelier,ImageFont.truetype(F+'Jost400.ttf',36),1056,ink)
center('Replay disponible · uniliance.life',ImageFont.truetype(F+'Jost500.ttf',34),1108,brown)
bg.save(out,quality=93)
