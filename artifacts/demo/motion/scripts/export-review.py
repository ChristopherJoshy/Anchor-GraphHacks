"""Inspect an exported review and cut its existing timeline into reusable modules."""
from pathlib import Path
import json
import re
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT.parent
WORK = DEMO / '.work-motion-graphics'
MOVIE = DEMO / 'anchor-demo-v03.mp4'
TIMELINE = json.loads((ROOT / 'timeline.json').read_text(encoding='utf-8'))
SPEECH = json.loads((ROOT / 'narration-timing.json').read_text(encoding='utf-8'))
FFMPEG = shutil.which('ffmpeg')
FFPROBE = shutil.which('ffprobe')
assert FFMPEG and FFPROBE, 'Put FFmpeg and FFprobe on PATH.'

def probe(file):
    return json.loads(subprocess.check_output([FFPROBE, '-v', 'error', '-show_entries', 'format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames', '-of', 'json', str(file)]))

def run(args):
    return subprocess.run([FFMPEG, '-hide_banner', '-nostdin', *args], check=True, capture_output=True, text=True)

meta = probe(MOVIE)
if not any(s['codec_type'] == 'subtitle' for s in meta['streams']):
    captioned = WORK / 'captioned-v03.mp4'
    run(['-loglevel', 'error', '-i', str(MOVIE), '-i', str(DEMO / 'anchor-demo-v03.srt'), '-c', 'copy', '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng', '-disposition:s:0', '0', '-movflags', '+faststart', '-y', str(captioned)])
    captioned.replace(MOVIE)
    meta = probe(MOVIE)
video = next(s for s in meta['streams'] if s['codec_type'] == 'video')
assert (video['width'], video['height'], video['r_frame_rate']) == (1920, 1080, '30/1')
assert abs(float(meta['format']['duration']) - TIMELINE['duration']) < .1
assert int(video['nb_frames']) == TIMELINE['duration'] * 30
assert any(s['codec_type'] == 'audio' for s in meta['streams'])
assert any(s['codec_type'] == 'subtitle' for s in meta['streams'])
sentence_count = 0
for scene in TIMELINE['scenes']:
    line = SPEECH['lines'][scene['id']]
    assert .7 + line['duration'] <= scene['duration']
    end = 0
    for sentence in line['sentences']:
        assert sentence['start'] >= end - .001
        end = sentence['start'] + sentence['duration']
        assert end <= line['duration'] + .001
        sentence_count += 1
assert (DEMO / 'anchor-demo-v03.srt').read_text(encoding='utf-8').count(' --> ') == sentence_count
scan = run(['-i', str(MOVIE), '-vf', 'blackdetect=d=0.15:pix_th=0.08', '-af', 'volumedetect', '-f', 'null', '-'])
(WORK / 'media-scan.log').write_text(scan.stderr, encoding='utf-8')
black = re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)', scan.stderr)
peak = re.search(r'max_volume: ([-\d.]+) dB', scan.stderr)
assert not black, f'Unexpected black intervals: {black}'
assert peak and float(peak.group(1)) < 0, 'Audio is clipped or unavailable.'

times = [s['start'] + min(s['duration'] - 2, 9) for s in TIMELINE['scenes']]
sheet = Image.new('RGB', (1920, 5 * 392), '#17172a')
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype(str(ROOT / 'assets/fonts/Bangers-Regular.ttf'), 25)
for i, second in enumerate(times):
    frame_path = WORK / f'output-{second:03d}.jpg'
    run(['-loglevel', 'error', '-ss', str(second), '-i', str(MOVIE), '-frames:v', '1', '-vf', 'scale=640:360', '-q:v', '2', '-y', str(frame_path)])
    x, y = i % 3 * 640, i // 3 * 392
    draw.text((x + 14, y + 3), f'{second//60:02d}:{second%60:02d} / {i+1:02d} {TIMELINE["scenes"][i]["id"]}', font=font, fill='#ffd447')
    sheet.paste(Image.open(frame_path), (x, y + 32))
sheet.save(DEMO / 'anchor-motion-contact-sheet.jpg', quality=94)

clips = DEMO / 'motion-clips-v03'
clips.mkdir(exist_ok=True)
for i, scene in enumerate(TIMELINE['scenes']):
    target = clips / f'{i+1:02d}-{scene["id"]}.mp4'
    run(['-loglevel', 'error', '-ss', str(scene['start']), '-i', str(MOVIE), '-t', str(scene['duration']), '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-g', '30', '-keyint_min', '30', '-sc_threshold', '0', '-c:a', 'aac', '-b:a', '160k', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-y', str(target)])
    assert abs(float(probe(target)['format']['duration']) - scene['duration']) < .1
    print('Exported', target.name, flush=True)
report = {'metadata': meta, 'decode': 'passed for all frames and audio', 'black_intervals_at_least_150ms': black, 'peak_dbfs': float(peak.group(1)), 'proof_times': times, 'modules': len(TIMELINE['scenes']), 'full_source_playback': False, 'full_human_audio_playback': False}
(WORK / 'qa.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
(DEMO / 'quality-report.json').write_text(json.dumps({'version': 'v03', 'duration_seconds': TIMELINE['duration'], 'width': video['width'], 'height': video['height'], 'fps': video['r_frame_rate'], 'frames': int(video['nb_frames']), 'video_codec': video['codec_name'], 'decode': report['decode'], 'black_intervals_at_least_150ms': black, 'audio_peak_dbfs': report['peak_dbfs'], 'caption_sentences': sentence_count, 'optional_subtitle_track': True, 'modules': report['modules'], 'full_source_playback': False, 'full_human_audio_playback': False}, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'duration': meta['format']['duration'], 'frames': video['nb_frames'], 'peak_dbfs': report['peak_dbfs'], 'black_intervals': black, 'modules': report['modules']}))
