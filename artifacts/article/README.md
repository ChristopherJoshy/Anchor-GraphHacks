# Anchor Medium picture story — 19 October 2026

Published revision: [Two Backup Suppliers, One Hidden Failure](https://medium.com/@christopherjoshy4/two-backup-suppliers-one-hidden-failure-23eb879ac2aa).

Authoring source: `docs/anchor-medium-picture-story.html`. This revision documents the existing prototype; it does not change the implementation, event submission, or demo video. Medium confirmed “Your changes have been published.” The public walkthrough and embedded YouTube player were inspected. The final story has 20 section headings, more than 90 explanatory paragraphs, 11 images, and one embedded video. Public page loading is lazy; not every image is requested on initial load.

## Media provenance

| File | Source | Role and limit |
|---|---|---|
| `web-4.jpg` | `Recorded video/Screen Recording 2026-10-18 185115.mp4`, 00:04 | Network overview. Geographic context and synthetic records. |
| `web-20.jpg` | Same web recording, 00:20 | Selected synthetic facility and inspector. City reference, not a real facility address. |
| `web-52.jpg` | Same web recording, 00:52 | Guided recovery layout. Visible fetch error and empty results are disclosed; no successful execution claimed. |
| `web-64.jpg` | Same web recording, 01:04 | Persisted activity/evidence view, from that session rather than a new recovery following the fetch error. |
| `cli-35.jpg` | `Recorded video/Screen Recording 2026-10-18 193237.mp4`, 00:35 | Reset and baseline network checks. |
| `cli-125.jpg` | Same CLI recording, 02:05 | Shared paths, source exclusions, baseline allocation, seven scenarios, zero added stress iterations. |
| `cli-155.jpg` | Same CLI recording, 02:35 | Duplicate receipts and read-back of existing allocations; not new quantities applied. |
| `cli-231.jpg` | Same CLI recording, 03:51 | Corrected capacity modification, revised allocation, final state. Rejected unsupported input remains visible. |
| `operational-schema.png` | `render-schema.py`, checked against `src/anchor/graph.py` | Implemented relationship subset; schematic, not a live DB screenshot. |
| `decision-schema.png` | Same renderer | Supported history/evidence schema; does not assert that every runtime action has every possible evidence edge. |
| `../anchor-medium-shared-failure.png` | Built-in OpenAI image generation | Conceptual cover art, explicitly disclosed. |

Still frames were extracted with FFmpeg at their original video resolution, without UI reconstruction or alteration of displayed results. No new video edit was made. The article embeds the existing [3:35 demo](https://www.youtube.com/watch?v=pNqod5FVSlY). The post explains that this edited film combines runs and does not demonstrate the separately integration-tested injected rejection branch.

The earlier video-edit choice to omit later web footage is not treated as evidence that those screens succeeded. This article uses the requested real frames with their visible failure/context limitations intact. The source recording files are unchanged and are not committed.

## Verification

- Fresh backend suite: `uv run pytest -q` → **26 passed, 2 skipped, 3 warnings**, 44.78 seconds. Both FalkorDB integration tests skipped because the service was unavailable. This is separate from the dated 18 October benchmark; no latency benchmark was rerun.
- Schema renderer: asserts every depicted relationship exists in the fixed graph templates; both rendered image dimensions checked. Both diagrams visually inspected.
- All 11 image elements loaded successfully in the editor; captions and all 20 sections inspected structurally. Public page verified after publishing, including the demo embed and web walkthrough.
- Public proof screenshots are local review artifacts, not operational evidence or source frames.

## Generated image prompt

Mode: built-in `image_gen.imagegen`; no CLI fallback. Final selected image: `../anchor-medium-shared-failure.png`.

> Create a polished wide editorial illustration for a technical Medium article about Anchor, a synthetic supply-chain recovery agent. 16:9 landscape. Dark navy backdrop, crisp ivory linework, cyan and amber highlights, restrained modern print aesthetic with subtle grain. Show two separate supplier warehouse buildings both connected by dependency lines converging on the same semiconductor foundry marked with an amber disruption symbol; to the side an independent supplier path remains cyan and reaches a small microchip order crate. Make the shared upstream dependency visually unambiguous. Include only these exact labels in clean readable type: 'ANCHOR', 'Two backups. One shared failure.', 'Synthetic supply network'. This is a conceptual editorial illustration, not a screenshot or evidence of real facilities. No company logos, no geographic claims, no invented metrics, no photorealistic disaster.

A second generated conceptual workflow draft was saved locally as `../anchor-medium-recovery-workflow.png` but is not used in the article. The user asked for real recorded UI frames; those carry the walkthrough. The schema diagrams use code-drawn labels checked against source rather than generated UI.
