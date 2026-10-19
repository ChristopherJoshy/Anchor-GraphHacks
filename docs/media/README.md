# README media: sources and interpretation

These assets support the main [Anchor README](../../README.md). Screen captures show the actual synthetic app and recorded Codex summaries. The explanatory SVGs are authored illustrations, not screenshots. Original recordings remain unchanged and outside Git.

## Source excerpts

| README asset | Source recording and time | What it shows |
|---|---|---|
| `network-overview.jpg` | `Screen Recording 2026-10-18 185115.mp4`, 00:03 | Actual web explorer, globe overview, location list, and South Korea inspector |
| `network-inspector.jpg` | Same recording, 00:10 | Actual regional web view with reference locations and dependency lines |
| `web-explorer.mp4` / `web-explorer.gif` | Same recording, 00:02–00:12 | Globe-to-regional-view interaction, without source audio |
| `paths.png` / `paths.mp4` | `20261018-1240-06.4842655.mp4`, 03:59–04:01; still at 04:00 | Recorded Codex summary of Primary, Backup B, and Backup C paths to the foundry |
| `plan.png` / `plan.mp4` | Same first CLI recording, 05:29–05:31; still at 05:30 | Recorded baseline allocation: 350 inventory + 650 D, 585000 USD minor units, zero unmet demand |
| `execution.png` / `execution.mp4` | `Screen Recording 2026-10-18 193237.mp4`, 02:33–02:35; still at 02:34 | Recorded execution summary explicitly showing two `DUPLICATE` receipts |
| `changed-plan.png` / `changed-plan.mp4` | Same later CLI recording, 03:49–03:51; still at 03:50 | Recorded revised allocation: 350 inventory + 450 D + 200 E, USD 6,550 |
| `readback.png` / `readback.mp4` | Same later CLI recording and time, with a different crop | Recorded revised-allocation read-back summary, `ALLOCATED`, 12 scheduled days, and zero shortfall |

The CLI crop rectangles are recorded in [source-cuts.json](../../artifacts/demo/motion/source-cuts.json) and [test-cuts.json](../../artifacts/demo/motion/test-cuts.json). Web source bounds are recorded in [web-cuts.json](../../artifacts/demo/motion/web-cuts.json). These images/clips reuse those selected excerpts. The first CLI recording remains within its previously authorized first 06:24. No additional source interval is represented as inspected.

## Read the evidence accurately

- CLI images are recorded coding-agent summaries, not screenshots of raw FalkorDB query results. The README links the actual query implementations separately.
- The path/baseline clips and later execution/change clips come from different runs. Their IDs differ; they are not a single continuous transaction.
- The initial execution excerpt verifies existing active allocations. `DUPLICATE` is not a new allocation being applied.
- The later changed-capacity execution released the prior 650-unit D reservation, applied D 450 and E 200, and kept the existing inventory allocation. The recorded summary reports the final active allocation state.
- The current code's outage mutation and the older source recording are distinct evidence. The older recording retains available supplier flags; its returned dependency paths support the shared-exposure explanation.
- All commercial data and operations are synthetic. Map coordinates identify geographic reference points, not actual supplier facilities. Map attribution is preserved in the web images and clip.

The broader [demo production notes](../../artifacts/demo/README.md) record the original video edit, narration, assets, recorded limitations, and credits. The YouTube link in the README was supplied by Christopher; it is separate from these short silent source clips.

## Explanatory diagrams

- `anchor-banner.svg`: a conceptual shared-upstream-dependency diagram, with direction explicitly labeled.
- `database-schema.svg`: a map of FalkorDB's record families and the separate SQLite operational tables. Detailed fields and relationship semantics appear in the README and source.

Both are original SVG/CSS-free vector artwork created for the README. Their fixed backgrounds and system fonts keep them readable in light and dark GitHub themes. No synthetic app screenshot or invented execution receipt was generated.

## Encoding and verification

The two web stills are JPEG frames extracted with FFmpeg. The five CLI stills and two-second clips are copied from the existing staged excerpts. The web MP4 is H.264/yuv420p at 1280 pixels wide with fast-start metadata; the GIF is an eight-frame-per-second, 900-pixel-wide loop with a 96-color palette. Source audio is omitted from all excerpts. The originals are unchanged.

Checks for this README edit inspect the source stills, render both SVGs for visual review, verify that PNG/JPEG/GIF files decode, probe and decode the MP4s, confirm the source bounds and clip durations, and check README paths, anchors, query text, and schema names against implementation. This media validation is separate from replaying the product's graph/ERP workflow.
