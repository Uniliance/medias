"""Transcription française horodatée mot par mot (faster-whisper medium).
Préparer l'audio : ffmpeg -i video.mp4 -ac 1 -ar 16000 audio.wav
Usage : python3 transcrire.py   (lit audio.wav, écrit transcript.json)
Domaines à autoriser pour télécharger le modèle : huggingface.co, *.hf.co
"""
import json
from faster_whisper import WhisperModel
import wave, numpy as np
wf=wave.open('audio.wav'); audio=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
m = WhisperModel("medium", device='cpu', compute_type='int8', cpu_threads=2)
segs, info = m.transcribe(audio, language='fr', word_timestamps=True, vad_filter=True, beam_size=5)
out=[]
for s in segs:
    out.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'s':w.start,'e':w.end,'w':w.word} for w in s.words]})
    print(f"[{s.start:6.1f}] {s.text}", flush=True)
json.dump(out, open('transcript.json','w'), ensure_ascii=False, indent=1)
