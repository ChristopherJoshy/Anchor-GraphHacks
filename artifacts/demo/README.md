# Anchor narrated demo — review v03

Current edit: **3:35, 1920 × 1080, 30 fps**, with code-drawn cartoon/anime-inspired graphics, selected real app recordings, local AI narration, credited background music, and short sound effects. This is a local review draft, not a submitted or deployed video.

## Review files

- `anchor-demo-v03.mp4` — current narrated edit, including an optional English subtitle track (off by default).
- `anchor-demo-v03.srt` — exact narration text, timed to separately synthesized sentences.
- `anchor-motion-contact-sheet.jpg` — frames extracted from the current export.
- `motion-clips-v03/` — reusable scene clips with the mixed audio.
- `motion/` — editable HyperFrames/SVG/CSS/GSAP source. Edit `scripts/scenes.mjs`, `narration.json`, and `style.css`; `scripts/build.mjs` regenerates HTML, timeline, storyboard and subtitles.
- Local Studio: <http://localhost:3026/#project/motion>. Availability depends on the preview process remaining active.

Older v01/v02 MP4s are previous reviews. Generated media, source crops, voice models, environments, downloads and caches remain outside Git. The existing Medium article is untouched.

## What changed after feedback

The film now explains the scenario before introducing the graph: the customer order, available inventory, shortfall, and foundry outage. Demand squares fill in stages, supply tokens stop at the outage, B/C traces converge on the foundry, allocation bars fill, D's capacity shrinks, E enters the mix, and action/state/read-back flows build in sequence.

Recording windows have their own horizontal bands. Source labels are above them and editorial cards below. No halftone transition covers a recording scene. The app recording is preserved in full within its frame, including map attribution. Subtitles are optional rather than burned over evidence.

The user subsequently requested AI voiceover and researched background music, superseding the earlier no-replacement-speech/no-music defaults. Narration uses local Kokoro `af_heart` at 1.03 speed. Scenes extend to fit the actual voice duration. Music ducks during each voice segment and fades at the ends.

## Timeline and claims

| Edit time | Scene | Evidence / meaning |
| --- | --- | --- |
| 00:00–00:15 | Customer order | Synthetic manufacturer needs 1,000 microcontrollers; inventory contains 350. |
| 00:15–00:28 | Recovery gap | Twenty 50-unit squares; inventory fills seven, leaving thirteen: 650 units. Arithmetic, not a measured benchmark. |
| 00:28–00:43 | Outage | Editorial illustration of interrupted supply after the fictional Taiwan foundry outage. |
| 00:43–00:55 | Real web app | Source 00:02–00:12; brief held frame after the excerpt accommodates narration. No automatic situation/demo or error material. |
| 00:55–01:11 | Shared dependency | Editorial diagram of actual returned B/C → Taiwan foundry paths. Dependency direction differs from physical supply flow. |
| 01:11–01:25 | Path evidence | Earlier CLI source 03:59–04:01, then held frame. Both backups share the same target. |
| 01:25–01:45 | Candidate | Earlier CLI source 05:29–05:31: inventory 350 + D 650, 1,000 planned units, $5,850 synthetic cost, 0 planned unmet demand. |
| 01:45–02:00 | Bounded challenge | Editorial explanation of declared finite modeled scenarios. No universal guarantee or benchmark improvement claimed. |
| 02:00–02:17 | Execution test | New CLI source 02:33–02:35: RECOVERED / verified=true, but both receipts DUPLICATE. Existing allocations confirmed; no new quantities applied in this run. |
| 02:17–02:32 | Changed capacity | Editorial explanation of the recorded D capacity reduction, 650 → 450. Recompute or report shortage. |
| 02:32–02:49 | Revised candidate | New CLI source 03:49–03:51: inventory 350 + D 450 + E 200, $6,550 synthetic cost, 0 planned unmet demand. |
| 02:49–03:07 | Verification mechanism | Editorial execute → persist → read back → compare workflow. |
| 03:07–03:25 | Recorded read-back | New CLI source 03:49–03:51: order ALLOCATED, 12 scheduled days, 0 remaining shortfall. Inventory receipt remains DUPLICATE. Final active mix confirmed in simulation. |
| 03:25–03:35 | Closing / credits | Synthetic simulation, AI voice disclosure and music credit. |

Every supplier, relationship, facility, order, incident, price and quantity is synthetic. Geography supplies context, not evidence of real commercial relationships. Planning, action responses, and persisted-state verification remain separate concepts.

## Source provenance and limits

1. `20261018-1240-06.4842655.mp4`: 8:32.067, 1458 × 1232, 30 fps. Authorized maximum is **06:24**. Only 03:59–04:01 and 05:29–05:31 are used. See `motion/source-cuts.json`.
2. `Recorded video/Screen Recording 2026-10-18 185115.mp4`: 1:10.400, 2046 × 1194, 30 fps. Only 00:02–00:12 is used. See `motion/web-cuts.json`.
3. `Recorded video/Screen Recording 2026-10-18 193237.mp4`: 3:53.200, 1462 × 1228, 30 fps. Three two-second crops show the execution receipt summary, revised allocation, and final read-back. The final two use the same source interval with different crops. See `motion/test-cuts.json`.

The earlier CLI recording has availability flags remaining true despite the foundry outage. Its paths establish shared dependency; the film does not claim it shows an eligibility flag changing. The new CLI recording separately reports a graph-backed exclusion reason despite available/approved flags. These are different recorded runs, not one fabricated continuous transaction.

The new recording includes a reset and initial run before the later test incident. In the later execution test, duplicate receipts mean allocations were already active. The changed-capacity run reports releasing the old 650-unit D allocation and confirms the new active mix; the 350 inventory units were already allocated. This is disclosed in narration and the evidence frames.

The new recording also contains a rejected modification using unsupported `kind: supplier`, followed by the supported `supplier_capacity` request. The cropped result evidence begins after that correction. This is not portrayed as an injected reservation rejection, automatic bounded retry, or an uncut clean run. The recorded stress summary lists seven modeled scenarios and `stress_iterations: 0`; no claim of an additional counterexample-search iteration or a universal resilience result is made.

Sources were inspected with timestamped stills and short selected cuts. No full source playback was performed. Source audio is muted; original files are untouched. Captions reproduce the generated narration, not a transcription of the terminal recordings.

## Research, assets and credits — 18 October 2026

**Music:** “Cipher” — Kevin MacLeod ([official track page](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100844)). Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Official catalog identifies `Cipher2.mp3`, 3:51, 150 BPM. Selected for a bright electronic pulse compatible with the graphic style. Adapted by trimming to the edit, EQ, normalization, fades and narration ducking. Full attribution is also in `motion/MUSIC-CREDIT.txt`; source URL/hash in `motion/music-source.json`. Include that credit if sharing the video later.

**AI voice:** [Kokoro-82M](https://github.com/hexgrad/kokoro), local inference through [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), version 0.5.0, voice `af_heart`. No voice cloning, paid speech service, or user recording impersonation. `narration.json` contains the exact script; `narration-timing.json` records actual synthesized sentence boundaries. Model files remain local and are not vendored into Git.

**SFX:** [Kenney Interface Sounds](https://kenney.nl/assets/interface-sounds) and [Impact Sounds](https://kenney.nl/assets/impact-sounds), CC0. Creator [usage guidance](https://kenney.nl/support) permits commercial use and makes credit optional. Selected files and original license notices are in `motion/assets/sfx/`.

**Typography:** [Bangers](https://github.com/googlefonts/bangers) by Vernon Adams / Bangers Project, and IBM Plex Sans 5.3.0, SIL Open Font License. Local fonts and licenses are included.

**Code tools:** [GSAP](https://gsap.com/docs/v3/GSAP/Timeline/) 3.14.2 under its [standard license](https://gsap.com/standard-license/), with original source banner retained; [HyperFrames](https://github.com/heygen-com/hyperframes) 0.8.171, Apache 2.0. Deterministic halftone scene handoffs adapt its catalog component idea. The downloaded notices and source hashes are included. [LottieFiles motion principles](https://github.com/LottieFiles/motion-design-skill) informed staging and easing; no third-party anime characters or artwork are used.

Project guidance: [Graph Hacks rules](https://www.wemakedevs.org/hackathons/falkordb/rules), [official RiskWise winner page](https://microsoft.github.io/AI_Agents_Hackathon/winners/), [FalkorDB Atrium recap](https://www.falkordb.com/blog/memory-meets-motion-the-falkordb-standouts/). The editorial structure follows the requested concrete failure → evidence changes the decision → verified outcome arc. It does not imply a competition result.

All other artwork is code-drawn SVG/CSS. No image generation, generated video, stock footage or characters were needed. Codex assisted with the edit, script, animation and production code. Team review remains necessary before any submission.

## Local production

Tools: FFmpeg/FFprobe 9.0.2, Node.js, HyperFrames 0.8.171, installed Google Chrome on Windows, Python/Pillow, isolated Kokoro/ONNX runtime. This machine's bundled headless shell did not start; the renderer uses installed Chrome through `HYPERFRAMES_BROWSER_PATH`.

From `artifacts/demo/motion`, with FFmpeg on PATH and an appropriate Python interpreter:

```powershell
$env:HYPERFRAMES_BROWSER_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
python scripts/prepare-assets.py --download --source '<first CLI.mp4>' --web-source '<web.mp4>' --test-source '<new CLI test.mp4>'
python scripts/generate-voice.py
node scripts/build.mjs
python scripts/prepare-music.py
npm run check
npm run render
python scripts/export-review.py
```

Voice generation requires `kokoro-onnx==0.5.0`, `soundfile` and the public v1.0 ONNX model/voice embeddings from the upstream release in `artifacts/demo/.work-motion-graphics/models/`. Music preparation expects the official `Cipher2.mp3` in that work directory. Scripts currently point to this machine's installed FFmpeg path; change it when reproducing elsewhere. Local generated audio and staged footage must be regenerated after cloning.

Build checks cover source bounds, crop bounds, recorded arithmetic, narration coverage, sentence counts and overall duration. Generated HTML is replaced by the builder; keep durable edits in authored source files.

## Quality record

- Visual review: multi-beat v02 storyboard and v03 evidence/credit frames inspected; source windows remain separate from explanation cards.
- Final HyperFrames checks: lint/runtime/layout each have 0 errors and 0 warnings; contrast 63/63 sampled checks passed. There is one informational connector-timing note during the stress-card entrance. The motion-audit feature was disabled; these results are not an independent choreography score.
- Export: all 6,450 video frames and the complete audio stream decoded successfully; 215.000 seconds, 1920 × 1080, 30 fps, H.264/AAC. No black interval of at least 150 ms at the configured threshold. Audio peak −1.0 dBFS, mean level −18.2 dBFS; no sample clipping detected. This is a technical level check, not a human listening verdict.
- Optional `mov_text` subtitle track is embedded and off by default; all 55 exact narration sentences have checked timing bounds. All 14 module durations were checked. The exported contact sheet was inspected, in addition to the multi-beat storyboard. Machine-readable results are in `quality-report.json`.
- No complete human listening/viewing pass has been claimed. Synthetic voice pronunciation and the subjective music/voice balance remain for user review. No product tests or real operational writes were performed for this media edit.
