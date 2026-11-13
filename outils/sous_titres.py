"""Sous-titres karaoké (mot prononcé en or) pour une vidéo verticale 1080x1920.
Usage : python3 sous_titres.py transcript.json "Accroche ligne 1" "Accroche ligne 2 (en or)"
Les deux accroches sont facultatives (affichées en haut pendant les 4 premières secondes).
Produit subs.ass, à incruster avec ffmpeg -vf subtitles=subs.ass
"""
import json, sys
from PIL import ImageFont
segs = json.load(open(sys.argv[1]))
raw = [w for s in segs for w in s['words']]
words = []
for w in raw:
    t = w['w']
    if words and (not t.startswith(' ') or t.strip().startswith("'") or words[-1]['w'].rstrip().endswith("'")):
        words[-1] = {'s': words[-1]['s'], 'e': w['e'], 'w': words[-1]['w'].rstrip() + t.strip()}
    else:
        words.append(dict(w))
for w in words: w['w'] = w['w'].strip()
import os
F = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'polices', 'Poppins-Bold.ttf'), 81)
chunks, cur = [], []
for i, w in enumerate(words):
    if not w['w']: continue
    cand = cur + [w]
    if cur and F.getlength(' '.join(x['w'] for x in cand)) > 900:
        chunks.append(cur); cur = [w]
    else: cur = cand
    nxt = words[i+1] if i+1 < len(words) else None
    if len(cur) >= 4 or w['w'][-1] in '.!?,;:' or nxt is None or nxt['s'] - w['e'] > 0.45:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
def ts(x): x = max(0, x); return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
G, W = '&H0000D7FF&', '&H00FFFFFF&'
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Poppins,140,&H00FFFFFF,&H00FFFFFF,&H00101E2D,&H64000000,1,0,0,0,100,100,0,0,1,8,4,2,60,60,620,1
Style: Hook,Poppins,140,&H00FFFFFF,&H00FFFFFF,&H00101E2D,&H64000000,1,0,0,0,100,100,0,0,1,7,3,8,60,60,170,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
L = []
if len(sys.argv) > 3:
    L.append(f"Dialogue: 1,{ts(0)},{ts(4.0)},Hook,,0,0,0,,{sys.argv[2]}\\N{{\\c{G}}}{sys.argv[3]}")
for ci, c in enumerate(chunks):
    nxt = chunks[ci+1][0]['s'] if ci+1 < len(chunks) else c[-1]['e'] + 0.8
    hold = min(nxt, c[-1]['e'] + 0.6)
    for wi, w in enumerate(c):
        st = w['s'] if wi else c[0]['s']
        en = c[wi+1]['s'] if wi+1 < len(c) else hold
        if en <= st: en = st + 0.05
        txt = ' '.join((f"{{\\c{G}}}{x['w']}{{\\c{W}}}" if j == wi else x['w']) for j, x in enumerate(c))
        L.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{txt}")
open('subs.ass', 'w').write(head + '\n'.join(L) + '\n')
print(' | '.join(' '.join(x['w'] for x in c) for c in chunks))
