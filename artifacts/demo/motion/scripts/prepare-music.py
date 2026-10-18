"""Freeze the attributed music selection and prepare a quiet narration bed."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent / '.work-motion-graphics'
SOURCE = WORK / 'Cipher2.mp3'
FFMPEG = r'C:\Users\Chris\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build-shared\bin\ffmpeg.exe'
TIMELINE = json.loads((ROOT / 'timeline.json').read_text())
duration = TIMELINE['duration']
assert 196 <= duration <= 240
assert SOURCE.stat().st_size > 1_000_000
out = ROOT / 'assets/audio/cipher-bed.wav'
subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-stream_loop', '-1', '-i', str(SOURCE), '-t', str(duration), '-af', f'highpass=f=100,equalizer=f=1800:t=q:w=1:g=-4,loudnorm=I=-24:TP=-9:LRA=11,afade=t=in:d=1,afade=t=out:st={duration-2}:d=2', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', '-y', str(out)], check=True)
credit = 'Cipher — Kevin MacLeod (incompetech.com). Licensed under Creative Commons Attribution 4.0 International. https://creativecommons.org/licenses/by/4.0/\nAdapted: trimmed/looped to the edit, EQ, loudness, fades and narration ducking.\n'
(ROOT / 'MUSIC-CREDIT.txt').write_text(credit, encoding='utf-8')
(ROOT / 'music-source.json').write_text(json.dumps({'title': 'Cipher', 'composer': 'Kevin MacLeod', 'page': 'https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100844', 'download': 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/Cipher2.mp3', 'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/', 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'date_checked': '2026-10-18', 'prepared_duration': duration, 'music_lufs_before_ducking': -24}, indent=2)+'\n', encoding='utf-8')
print('Prepared credited music bed:', duration, 'seconds.')
