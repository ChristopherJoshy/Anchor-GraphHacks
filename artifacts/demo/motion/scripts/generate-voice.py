"""Synthesize the approved editorial script locally, preserving exact sentence boundaries."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent / '.work-motion-graphics'
OUT = ROOT / 'assets/audio'
OUT.mkdir(parents=True, exist_ok=True)
REQUEST = json.loads((ROOT / 'narration.json').read_text(encoding='utf-8'))
FFMPEG = r'C:\Users\Chris\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build-shared\bin\ffmpeg.exe'
model = Kokoro(str(WORK / 'models/kokoro-v1.0.onnx'), str(WORK / 'models/voices-v1.0.bin'))
metadata = {'provider': REQUEST['provider'], 'voice': REQUEST['voice'], 'speed': 1.03, 'lines': {}}
for name, text in REQUEST['lines'].items():
    digest = hashlib.sha256(text.encode()).hexdigest()
    cache = WORK / f'voice-{name}.json'
    target = OUT / f'{name}.wav'
    if cache.exists() and target.exists():
        old = json.loads(cache.read_text())
        if old['text_sha256'] == digest:
            metadata['lines'][name] = old
            continue
    pieces, sentences, offset = [], [], 0.0
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        samples, rate = model.create(sentence, voice=REQUEST['voice'], speed=1.03, lang='en-us')
        assert rate == 24000 and len(samples) > 0
        assert np.isfinite(samples).all()
        duration = len(samples) / rate
        sentences.append({'text': sentence, 'start': round(offset, 4), 'duration': round(duration, 4)})
        pieces.extend([samples, np.zeros(round(rate * .22))])
        offset += duration + .22
    raw = WORK / f'voice-{name}-raw.wav'
    sf.write(str(raw), np.concatenate(pieces), rate)
    subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', str(raw), '-af', 'loudnorm=I=-17:TP=-2:LRA=8', '-ar', '48000', '-c:a', 'pcm_s16le', '-y', str(target)], check=True)
    info = sf.info(str(target))
    assert abs(info.duration - offset) < .02
    entry = {'path': f'assets/audio/{name}.wav', 'duration': round(info.duration, 4), 'text_sha256': digest, 'sentences': sentences}
    metadata['lines'][name] = entry
    cache.write_text(json.dumps(entry, indent=2), encoding='utf-8')
    print(name, round(info.duration, 2), 'seconds', flush=True)
(ROOT / 'narration-timing.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
print('Generated', len(metadata['lines']), 'scene voice tracks. Exact sentence timestamps retained.', flush=True)
