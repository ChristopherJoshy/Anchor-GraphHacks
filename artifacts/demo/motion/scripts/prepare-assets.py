"""Freeze licensed assets and stage only allowlisted source excerpts locally."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent / '.work-motion-graphics'
ASSETS = ROOT / 'assets'
FFBIN = Path(r'C:\Users\Chris\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build-shared\bin')
LIMIT = 384
CUTS = [
    {'id': 'paths', 'start': 239, 'duration': 2, 'crop': [18, 908, 1060, 92]},
    {'id': 'plan', 'start': 329, 'duration': 2, 'crop': [18, 876, 1420, 122]},
]
TEST_CUTS = [
    {'id': 'execution', 'start': 153, 'duration': 2, 'crop': [20, 606, 1420, 278]},
    {'id': 'changed-plan', 'start': 229, 'duration': 2, 'crop': [20, 712, 1420, 176]},
    {'id': 'readback', 'start': 229, 'duration': 2, 'crop': [20, 900, 1420, 132]},
]
URLS = {
    'interface.zip': 'https://kenney.nl/media/pages/assets/interface-sounds/fa43c1dd4d-1677589452/kenney_interface-sounds.zip',
    'impact.zip': 'https://kenney.nl/media/pages/assets/impact-sounds/87b4ddecda-1677589768/kenney_impact-sounds.zip',
    'Bangers-Regular.ttf': 'https://raw.githubusercontent.com/googlefonts/bangers/main/fonts/ttf/Bangers-Regular.ttf',
    'Bangers-OFL.txt': 'https://raw.githubusercontent.com/googlefonts/bangers/main/OFL.txt',
    'Plex-Regular.woff2': 'https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans@5.3.0/files/ibm-plex-sans-latin-400-normal.woff2',
    'Plex-Bold.woff2': 'https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans@5.3.0/files/ibm-plex-sans-latin-700-normal.woff2',
    'Plex-OFL.txt': 'https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans@5.3.0/LICENSE',
    'gsap.min.js': 'https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js',
    'HyperFrames-LICENSE.txt': 'https://raw.githubusercontent.com/heygen-com/hyperframes/main/LICENSE',
}

def self_check():
    for cut in CUTS:
        assert 0 <= cut['start'] < cut['start'] + cut['duration'] <= LIMIT
        x, y, width, height = cut['crop']
        assert x >= 0 and y >= 0 and x + width <= 1458 and y + height <= 1232
        assert width % 2 == height % 2 == 0
    assert sum(c['duration'] for c in CUTS) == 4
    for cut in TEST_CUTS:
        assert 0 <= cut['start'] < cut['start'] + cut['duration'] <= 233.2
        x, y, width, height = cut['crop']
        assert min(x, y) >= 0 and x + width <= 1462 and y + height <= 1228
        assert width % 2 == height % 2 == 0

def download(name, url):
    dest = WORK / name
    if not dest.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'Anchor-local-motion-production/1.0'})
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read()
        assert len(data) > 100, f'Empty download: {name}'
        dest.write_bytes(data)
    return dest

def assets():
    WORK.mkdir(parents=True, exist_ok=True)
    audit = []
    for name, url in URLS.items():
        print('Resolve', name, flush=True)
        src = download(name, url)
        if name.endswith('.zip'):
            with zipfile.ZipFile(src) as archive:
                for entry in archive.infolist():
                    assert not Path(entry.filename).is_absolute() and '..' not in Path(entry.filename).parts
                archive.extractall(WORK / name.removesuffix('.zip'))
            print(name, 'downloaded', flush=True)
        else:
            kind = 'vendor' if name in ('gsap.min.js', 'GSAP-LICENSE.txt', 'HyperFrames-LICENSE.txt') else 'fonts'
            target = ASSETS / kind / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        audit.append({'file': name, 'url': url, 'sha256': hashlib.sha256(src.read_bytes()).hexdigest()})
    (ASSETS / 'downloads.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    (ASSETS / 'vendor' / 'GSAP-NOTICE.txt').write_text('GSAP 3.14.2. Copyright GreenSock. Original source banner retained.\nLicense: https://gsap.com/standard-license/\nDownloaded from the official npm package via jsDelivr.\n', encoding='utf-8')
    sound_dir = ASSETS / 'sfx'
    sound_dir.mkdir(exist_ok=True)
    for name in ['click_003.ogg', 'bong_001.ogg', 'confirmation_002.ogg', 'error_003.ogg', 'open_002.ogg', 'maximize_001.ogg', 'switch_002.ogg']:
        matches = list((WORK / 'interface').rglob(name))
        assert len(matches) == 1, name
        shutil.copy2(matches[0], sound_dir / name)
    license_file = next((WORK / 'interface').rglob('License.txt'))
    shutil.copy2(license_file, sound_dir / 'Kenney-License.txt')
    punch = next((WORK / 'impact').rglob('impactPunch_medium_002.ogg'))
    shutil.copy2(punch, sound_dir / 'impactPunch_medium_002.ogg')
    shutil.copy2(next((WORK / 'impact').rglob('License.txt')), sound_dir / 'Kenney-Impact-License.txt')
    durations = {}
    for sound in sound_dir.glob('*.ogg'):
        probe = subprocess.check_output([str(FFBIN / 'ffprobe.exe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(sound)])
        durations[sound.name] = float(json.loads(probe)['format']['duration'])
    (sound_dir / 'durations.json').write_text(json.dumps(durations, indent=2) + '\n', encoding='utf-8')
    print('Frozen fonts, animation dependency, and', len(durations), 'licensed sound effects.')

def stage(source):
    dest = ASSETS / 'footage'
    dest.mkdir(parents=True, exist_ok=True)
    for cut in CUTS:
        x, y, w, h = cut['crop']
        target = dest / (cut['id'] + '.mp4')
        cmd = [str(FFBIN / 'ffmpeg.exe'), '-hide_banner', '-loglevel', 'error', '-ss', str(cut['start']), '-i', str(source), '-t', str(cut['duration']), '-vf', f'crop={w}:{h}:{x}:{y},setsar=1', '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-g', '30', '-keyint_min', '30', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-y', str(target)]
        subprocess.run(cmd, check=True)
        probe = subprocess.check_output([str(FFBIN / 'ffprobe.exe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(target)])
        assert abs(float(json.loads(probe)['format']['duration']) - cut['duration']) < 0.1
        subprocess.run([str(FFBIN / 'ffmpeg.exe'), '-hide_banner', '-loglevel', 'error', '-ss', '1', '-i', str(target), '-frames:v', '1', '-y', str(dest / (cut['id'] + '.png'))], check=True)
        print('Staged', cut['id'], cut['start'], cut['duration'], flush=True)
    (ROOT / 'source-cuts.json').write_text(json.dumps({'source': source.name, 'limit_seconds': LIMIT, 'cuts': CUTS, 'audio': 'muted in graphics review; original file untouched'}, indent=2) + '\n', encoding='utf-8')

def stage_web(source):
    target = ASSETS / 'footage' / 'network.mp4'
    target.parent.mkdir(exist_ok=True, parents=True)
    subprocess.run([str(FFBIN / 'ffmpeg.exe'), '-hide_banner', '-loglevel', 'error', '-ss', '2', '-i', str(source), '-t', '10', '-an', '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', '-g', '30', '-keyint_min', '30', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-y', str(target)], check=True)
    (ROOT / 'web-cuts.json').write_text(json.dumps({'source': source.name, 'cuts': [{'id': 'network', 'start': 2, 'duration': 10}], 'excluded': 'All material after 00:12, including empty/error map and automatic recovery/demo views', 'audio': 'muted; supplied narration pending'}, indent=2) + '\n', encoding='utf-8')
    subprocess.run([str(FFBIN / 'ffmpeg.exe'), '-hide_banner', '-loglevel', 'error', '-ss', '9', '-i', str(target), '-frames:v', '1', '-y', str(target.with_suffix('.png'))], check=True)
    print('Staged clean web excerpt 00:02–00:12.')

def stage_test(source):
    dest = ASSETS / 'footage'
    dest.mkdir(exist_ok=True, parents=True)
    for cut in TEST_CUTS:
        x, y, w, h = cut['crop']
        target = dest / (cut['id'] + '.mp4')
        subprocess.run([str(FFBIN / 'ffmpeg.exe'), '-hide_banner', '-loglevel', 'error', '-ss', str(cut['start']), '-i', str(source), '-t', str(cut['duration']), '-vf', f'crop={w}:{h}:{x}:{y},setsar=1', '-an', '-c:v', 'libx264', '-crf', '16', '-preset', 'fast', '-g', '30', '-keyint_min', '30', '-sc_threshold', '0', '-pix_fmt', 'yuv420p', '-y', str(target)], check=True)
        probe = subprocess.check_output([str(FFBIN / 'ffprobe.exe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(target)])
        assert abs(float(json.loads(probe)['format']['duration']) - cut['duration']) < .1
        subprocess.run([str(FFBIN / 'ffmpeg.exe'), '-hide_banner', '-loglevel', 'error', '-ss', '1', '-i', str(target), '-frames:v', '1', '-y', str(dest / (cut['id'] + '.png'))], check=True)
    (ROOT / 'test-cuts.json').write_text(json.dumps({'source': source.name, 'cuts': TEST_CUTS, 'audio': 'muted; original untouched', 'caveat': 'Execution verifies existing duplicate allocations; changed-capacity readback reports final active allocations.'}, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path)
    parser.add_argument('--web-source', type=Path)
    parser.add_argument('--test-source', type=Path)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    self_check()
    if args.download:
        assets()
    if args.source:
        stage(args.source)
    if args.web_source:
        stage_web(args.web_source)
    if args.test_source:
        stage_test(args.test_source)
    print('Asset/source-bound checks passed.')
