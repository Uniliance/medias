#!/usr/bin/env bash
# Montage final d'une vidéo courte du Château Intérieur (1080x1920) :
# miniature 0,4 s en ouverture + vidéo sous-titrée + plan de fin fixe 3 s (fondu 0,3 s).
# Usage : bash montage.sh brute.mp4 subs.ass miniature.jpg sortie.mp4
set -euo pipefail
RAW="$1"; ASS="$2"; MINI="$3"; OUT="$4"
FIN="$(dirname "$(readlink -f "$0")")/../modeles/plan-de-fin-chateau.png"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$RAW")
OFF=$(python3 -c "print(round(0.4+$D-0.3,3))")   # début du fondu vers le plan de fin
AF=$(python3 -c "print(round(0.4+$D-0.6,3))")    # début du fondu sonore
ffmpeg -y -loop 1 -t 0.4 -i "$MINI" -i "$RAW" -loop 1 -t 3.3 -i "$FIN" \
  -f lavfi -t 0.4 -i anullsrc=r=48000:cl=stereo -f lavfi -t 3.0 -i anullsrc=r=48000:cl=stereo \
  -filter_complex "[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p,settb=1/30[c];\
[1:v]scale=1080:1920,subtitles=$ASS,fps=30,setsar=1,format=yuv420p,settb=1/30[m];\
[2:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p,settb=1/30[e];\
[c][m]concat=n=2:v=1:a=0,settb=1/30[cm];[cm][e]xfade=transition=fade:duration=0.3:offset=$OFF[vo];\
[1:a]aresample=48000,aformat=channel_layouts=stereo[ma];\
[3:a][ma][4:a]concat=n=3:v=0:a=1,afade=t=out:st=$AF:d=0.6[ao]" \
  -map "[vo]" -map "[ao]" -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -movflags +faststart "$OUT"
ls -la "$OUT"   # doit rester sous 100 Mo (limite GitHub)
