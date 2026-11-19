"""Monteur Uniliance : sous-titres mot par mot, styles selon le ton, couleurs de la Spirale, fin Uniliance.

Deux étapes :
  1) python3 outils/monteur.py transcrire video.mp4
     -> travail/mots.txt (un mot par ligne : numéro, début, mot) et travail/mots.json
  2) python3 outils/monteur.py monter video.mp4 plan.json sortie.mp4
     -> vidéo sous-titrée, son remis à niveau (-15 LUFS), fin Uniliance de 2,8 s

plan.json (écrit par l'IA après lecture de mots.txt, puis validé par la personne) :
{
  "corrections": {"commodiquia": "commode Ikea"},            # mot transcrit -> texte affiché
  "sections": [{"debut": "Tu médites", "style": "A"},       # A = Coup de poing (Anton), passages forts
               {"debut": "et tu t'es fait", "style": "B"},  # B = Gravure (Fraunces Black Italic), doux / humour tendre
               {"debut": "Non, je ne résiste", "style": "C"}],  # C = Encre (Permanent Marker), voix du mental / absurde
  "couleurs": [{"mots": "part guerrière", "couleur": "rouge"},
               {"mots": "force", "avant": "rencontré la", "couleur": "rouge"}],  # "avant" = mots juste avant, pour viser une occurrence
  "forts": ["tapis", "bypass"],                               # mots en plus gros, sans couleur
  "fin": true
}
Couleurs (Spirale Dynamique) : beige, violet, rouge, bleu, orange, vert, jaune, turquoise.
Modèle de transcription : faster-whisper large-v3-turbo (domaines huggingface.co et *.hf.co à autoriser).
"""
import json, os, re, subprocess, sys, wave, random
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
POLICES = os.path.join(RACINE, 'polices')
FIN = os.path.join(RACINE, 'modeles', 'fin-uniliance')
TRAV = 'travail'
LEXIQUE = ("Uniliance, Château Intérieur, Kalima, Ennéagramme, Spirale Dynamique, Étienne Gigand, Ciccio, "
           "communication non-violente, Marshall Rosenberg, bypass spirituel, Biocoop, love bagarre.")


def sh(*a):
    subprocess.run(a, check=True)


def audio16k(video):
    os.makedirs(TRAV, exist_ok=True)
    p = os.path.join(TRAV, 'audio16k.wav')
    sh('ffmpeg', '-v', 'error', '-y', '-i', video, '-vn', '-ac', '1', '-ar', '16000', p)
    w = wave.open(p)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def transcrire(video):
    from faster_whisper import WhisperModel
    x = audio16k(video)
    m = WhisperModel('mobiuslabsgmbh/faster-whisper-large-v3-turbo', device='cpu', compute_type='int8', cpu_threads=2)
    segs, _ = m.transcribe(x, language='fr', beam_size=2, word_timestamps=True, vad_filter=False, initial_prompt=LEXIQUE)
    W = []
    for s in segs:
        for wd in s.words:
            t = wd.word.strip().replace("'", "’")
            if not t:
                continue
            if W and (t[0] in "’-"):          # apostrophes et traits d'union collés au mot d'avant
                W[-1]['w'] += t; W[-1]['e'] = round(wd.end, 3)
            else:
                W.append(dict(w=t, s=round(wd.start, 3), e=round(wd.end, 3)))
    # phrase répétée à la toute fin (hallucination fréquente) : on la retire
    txt = [w['w'] for w in W]
    for L in range(12, 3, -1):
        if len(txt) >= 2 * L and txt[-L:] == txt[-2 * L:-L]:
            W = W[:-L]; break
    json.dump(W, open(os.path.join(TRAV, 'mots.json'), 'w'), ensure_ascii=False)
    with open(os.path.join(TRAV, 'mots.txt'), 'w') as f:
        for i, w in enumerate(W):
            f.write(f"{i}\t{w['s']:.2f}\t{w['w']}\n")
    print(' '.join(w['w'] for w in W))
    print(f"\n{len(W)} mots -> {TRAV}/mots.txt")


def norm(w):
    return w.strip('.,?!…«»:;"').lower().replace("'", "’")


def onsets(T, x):
    """Cale le début de chaque mot sur la reprise réelle de la voix (Whisper part souvent trop tôt après une pause)."""
    from scipy.signal import butter, sosfiltfilt
    y = sosfiltfilt(butter(4, [300, 3400], btype='band', fs=16000, output='sos'), x)
    n = len(y) // 160
    dB = 20 * np.log10(np.sqrt((y[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-6)
    for i, w in enumerate(T):
        s, e = w['s'], w['e']
        gap = s - (T[i - 1]['e'] if i else 0)
        on = s + 0.05
        if gap >= 0.12:
            a = max(0, int((s - 1) * 100)); b = int((e + 0.3) * 100)
            floor = np.percentile(dB[a:b], 20)
            for f in range(max(0, int((s - 0.1) * 100)), max(int((s - 0.1) * 100) + 1, int((e - 0.04) * 100))):
                if dB[f] > floor + 15 and dB[f:f + 8].mean() > floor + 12:
                    on = max(s, f / 100) + 0.03; break
        w['on'] = min(on, max(s, e - 0.08))


COUL = {'beige': '&H007AA2C8&', 'violet': '&H00FF7CB5&', 'rouge': '&H003D4AFF&', 'bleu': '&H00FFA64D&',
        'orange': '&H002E9AFF&', 'vert': '&H0068D05F&', 'jaune': '&H003BD9FF&', 'turquoise': '&H00D0E03F&'}
BASE = {'A': ('&H00FFFFFF&', 108, 158), 'B': ('&H00D6ECF6&', 104, 150), 'C': ('&H00FFFFFF&', 100, 130)}


def ts(x):
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def ass(T, plan, path):
    # corrections
    corr = {norm(k): v for k, v in plan.get('corrections', {}).items()}
    for w in T:
        if norm(w['w']) in corr:
            p = re.match(r'^(.*?)([.,?!…:;]*)$', w['w']).group(2)
            w['w'] = corr[norm(w['w'])] + p
    toks = [norm(w['w']) for w in T]
    # sections
    sec = ['A'] * len(T); pos = 0; bornes = []
    for s in plan.get('sections', []):
        ws = [norm(x) for x in s['debut'].split()]
        for i in range(pos, len(T) - len(ws) + 1):
            if toks[i:i + len(ws)] == ws:
                bornes.append((i, s['style'])); pos = i + 1; break
        else:
            print('section introuvable :', s['debut'])
    for k, (i, st) in enumerate(bornes):
        for j in range(i, bornes[k + 1][0] if k + 1 < len(bornes) else len(T)):
            sec[j] = st
    # couleurs
    ci = {}
    for c in plan.get('couleurs', []):
        ph = [norm(x) for x in c['mots'].split()]; av = [norm(x) for x in c.get('avant', '').split()]
        for i in range(len(av), len(T) - len(ph) + 1):
            if toks[i:i + len(ph)] == ph and toks[i - len(av):i] == av:
                for j in range(len(ph)):
                    ci[i + j] = COUL[c['couleur']]
                break
        else:
            print('couleur introuvable :', c['mots'])
    forts = {norm(x) for x in plan.get('forts', [])}
    random.seed(7)
    ev = []
    for i, w in enumerate(T):
        st = sec[i]; a = w['on']; nxt = T[i + 1]['on'] if i + 1 < len(T) else w['e'] + 0.8
        e = min(w['e'] + 0.35, nxt) if nxt - w['e'] < 0.9 else w['e'] + 0.35
        e = max(e, a + 0.12)
        if i + 1 < len(T): e = min(e, nxt)
        col, fs, big = BASE[st]
        t = w['w'].upper() if st in 'AC' else w['w']
        if i in ci: t = r'{\c' + ci[i] + r'\fs' + str(big) + '}' + t
        elif norm(w['w']) in forts: t = r'{\fs' + str(big - 14) + '}' + t
        rot = r'\frz%.1f' % random.uniform(-3.5, 3.5) if st == 'C' else ''
        ev.append(f"Dialogue: 0,{ts(a)},{ts(e)},{st},,0,0,0,,"
                  r"{\fscx90\fscy90\t(0,60,\fscx104\fscy104)\t(60,110,\fscx100\fscy100)" + rot + '}' + t)
    hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: A,Anton,108,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,8,5,2,60,60,560,1
Style: B,Fraunces Black Italic,104,&H00D6ECF6,&H00D6ECF6,&H003B3410,&HA0000000,0,0,0,0,100,100,0,0,1,3,6,2,60,60,560,1
Style: C,Permanent Marker,100,&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,0,0,0,0,100,100,0,0,1,7,4,2,60,60,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(path, 'w').write(hdr + '\n'.join(ev) + '\n')


def fin(video, out):
    """Fin Uniliance de 2,8 s : dernière image floutée, logo qui saute (bloop), « ABONNE-TOI » (plop), souffle."""
    from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
    W_, H_ = 1080, 1920
    last = os.path.join(TRAV, 'derniere.png')
    sh('ffmpeg', '-v', 'error', '-y', '-sseof', '-0.2', '-i', video, '-frames:v', '1', '-vf', f'scale={W_}:{H_}', last)
    fps = 30000 / 1001; N = int(2.8 * fps)
    l0 = Image.open(last).convert('RGB')
    bg = ImageEnhance.Brightness(l0.filter(ImageFilter.GaussianBlur(22))).enhance(0.55)
    bg = Image.blend(bg, Image.new('RGB', bg.size, (16, 52, 59)), 0.45)
    a = np.array(Image.open(os.path.join(FIN, 'logo.png')).convert('RGBA')).astype(np.int16)
    dark = (a[..., 0] < 70) & (a[..., 1] < 70) & (a[..., 2] < 90) & (a[..., 3] > 0)
    a[dark, 0:3] = (246, 236, 214)
    logo = Image.fromarray(a.astype(np.uint8)); logo = logo.crop(logo.getbbox())
    logo = logo.resize((880, int(logo.height * 880 / logo.width)), Image.LANCZOS)
    F = ImageFont.truetype(os.path.join(POLICES, 'Anton.ttf'), 92)
    def eb(t):
        t = min(max(t, 0), 1); return 1 + 2.9 * (t - 1) ** 3 + 1.9 * (t - 1) ** 2
    d = os.path.join(TRAV, 'fin'); os.makedirs(d, exist_ok=True)
    for i in range(N):
        t = i / fps; im = bg.copy()
        k = eb((t - 0.25) / 0.45)
        if t >= 0.25 and k > 0.02:
            L = logo.resize((max(1, int(logo.width * k)), max(1, int(logo.height * k))), Image.LANCZOS)
            im.paste(L, ((W_ - L.width) // 2, 820 - L.height // 2), L)
        k2 = eb((t - 0.95) / 0.4)
        if t >= 0.95 and k2 > 0.02:
            lay = Image.new('RGBA', (700, 200), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
            bb = dr.textbbox((0, 0), 'ABONNE-TOI', font=F); w = bb[2] - bb[0]
            dr.rounded_rectangle([(700 - w) // 2 - 36, 40, (700 + w) // 2 + 36, 40 + bb[3] + 30], radius=20, fill=(240, 190, 74, 255))
            dr.text(((700 - w) // 2, 58 - bb[1]), 'ABONNE-TOI', font=F, fill=(16, 52, 59))
            lay = lay.resize((int(700 * k2), int(200 * k2)), Image.LANCZOS).rotate(-3, expand=True, resample=Image.BICUBIC)
            im.paste(lay, ((W_ - lay.width) // 2, 1140 - lay.height // 2), lay)
        if t < 0.25: im = Image.blend(l0, im, t / 0.25)
        im.save(os.path.join(d, f'{i:04d}.png'))
    sr = 48000; n = int(2.8 * sr); s = np.zeros(n)
    def smp(p):
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True)
        z = np.frombuffer(r.stdout, np.float32).astype(float); return z / np.abs(z).max()
    def place(z, t, g, hit=False):
        i = int(t * sr) - (int(np.argmax(np.convolve(np.abs(z), np.ones(240) / 240, 'same'))) if hit else 0)
        if i < 0: z = z[-i:]; i = 0
        e = min(n, i + len(z)); s[i:e] += g * z[:e - i]
    sf = smp(os.path.join(FIN, 'souffle.mp3')); nz = np.nonzero(np.abs(sf) > 0.03)[0]
    sf = sf[max(0, nz[0] - 480):][:n]; env = np.ones(len(sf)); env[-int(.4 * sr):] = np.linspace(1, 0, int(.4 * sr))
    place(sf * env, 0, 0.3); place(smp(os.path.join(FIN, 'bloop.mp3')), 0.3, 0.45); place(smp(os.path.join(FIN, 'plop2.mp3')), 1.0, 0.45, True)
    s[-int(.15 * sr):] *= np.linspace(1, 0, int(.15 * sr)); s = s / np.abs(s).max() * 0.55 * 1.6
    s.astype(np.float32).tofile(os.path.join(TRAV, 'fin.f32'))
    sh('ffmpeg', '-v', 'error', '-y', '-framerate', '30000/1001', '-i', os.path.join(d, '%04d.png'), '-f', 'f32le', '-ar', str(sr), '-ac', '1',
       '-i', os.path.join(TRAV, 'fin.f32'), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
       '-c:a', 'aac', '-ac', '2', '-shortest', out)


def monter(video, plan_path, out):
    plan = json.load(open(plan_path))
    T = json.load(open(os.path.join(TRAV, 'mots.json')))
    x = audio16k(video)
    onsets(T, x)
    ap = os.path.join(TRAV, 'sous_titres.ass'); ass(T, plan, ap)
    vf = f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,ass={ap}:fontsdir={POLICES},format=yuv420p"
    af = "loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    enc = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-maxrate', '3.3M', '-bufsize', '6.6M', '-r', '30000/1001',
           '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart']
    if plan.get('fin', True):
        fp = os.path.join(TRAV, 'fin.mp4'); fin(video, fp)
        sh('ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', video, '-i', fp, '-filter_complex',
           f"[0:v]{vf}[v0];[0:a:0]{af}[a0];[1:v]setsar=1[v1];[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a1];"
           "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]", '-map', '[v]', '-map', '[a]', *enc, out)
    else:
        sh('ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', video, '-vf', vf, '-af', af, *enc, out)
    print('ok ->', out)


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'transcrire':
        transcrire(sys.argv[2])
    elif len(sys.argv) >= 5 and sys.argv[1] == 'monter':
        monter(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
