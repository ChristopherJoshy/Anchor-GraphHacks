# Anchor web experience

**Status:** Optional, local companion to the MCP workflow. Verified with the production build on 18 October 2026.

## What an operator sees

Anchor separates the work into three named views:

- **Explore network:** a searchable list of geographic reference locations, an interactive Earth, and a context panel for either the selected record or the recovery guide. Map lines can be toggled for graph dependencies, modeled transport, and computed recovery allocations. Selecting a map or list item opens the corresponding FalkorDB-backed records in the inspector.
- **Recover orders:** three readable questions organize the evidence: what is at risk, what Anchor will do (or did), and whether the action worked. Costs, quantities, lead times, remaining demand, and execution status are shown from returned plan and ERP data. The map is available as a supporting view.
- **Activity & evidence:** persisted incidents and decisions are shown separately from expandable technical payloads.

The initial view presents a short recovery guide and the synthetic order. Advanced graph fields and raw API responses stay behind explicit disclosure controls. The interface uses ordinary language alongside operational labels so a judge or non-coder can follow the same sequence as the backend.

## Research and design decisions

| Source | Verified publication/update date | Design implication for Anchor |
|---|---|---|
| [Google Earth: Manage data layers](https://developers.google.com/maps/documentation/earth/manage-data-layers) | Updated 15 Oct 2026 | Keep layer visibility under a named control and open a feature inspector when a user selects a map item. Anchor adopts these general interaction patterns without copying Google Earth branding or layout. |
| [Google Earth: Add features to projects](https://developers.google.com/maps/documentation/earth/add-features-to-projects?platform=computer) | Updated 16 Oct 2026 | Make placemarks, lines, and selected feature information understandable together. Anchor distinguishes location markers from graph and recovery lines. |
| [Nielsen Norman Group: Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/) | 3 Dec 2006 | Put the frequent recovery steps first and reveal technical JSON, scenario changes, and provenance only when requested. This is published usability guidance, not a usability study of Anchor. |
| [CesiumJS Viewer API](https://cesium.com/learn/cesiumjs/ref-doc/Viewer.html) | Living API reference; accessed 18 Oct 2026 | Use the supported Viewer lifecycle and explicit viewer options. Disable unused globe controls and keep Anchor's own navigation and layers visible. |
| [NASA GIBS access basics](https://nasa-gibs.github.io/gibs-api-docs/access-basics/) | Living API documentation; accessed 18 Oct 2026 | Use NASA's tiled imagery service for global natural-color context; retain attribution and handle unavailable tiles. |
| [OpenStreetMap tile usage policy](https://operations.osmfoundation.org/policies/tiles/) | Living policy; accessed 18 Oct 2026 | Request tiles only for the visible interactive map, retain visible attribution, allow normal browser referrers and caching, and do not prefetch or offer offline tile downloads. The service is best effort and can throttle or block requests. |

## Map meaning and data boundaries

- The Earth is a Cesium ellipsoid with NASA GIBS composite imagery and a bundled Natural Earth overview layer. Anchor does not include 3D buildings or a detailed terrain mesh.
- Street detail uses the standard OpenStreetMap tile endpoint. NASA and OSM tile requests go directly from the browser to those providers; the providers may receive the user's IP address and the tile locations requested. The map can fail to show detailed imagery when those services or the network are unavailable.
- Map coordinates are public geographic reference points for cities/locations. Supplier, facility, inventory, contract, capacity, order, and dependency records are synthetic. These coordinates do not identify real company sites or exact facility/warehouse addresses.
- The map is a geographic rendering of API records. It does not calculate dependencies. The backend's parameterized FalkorDB queries determine graph paths, affected entities, and eligible allocations; missing graph data is shown as missing rather than replaced with a local network.
- A line joins city reference points for records connected by an API relationship. It is not a live shipment path, road route, or proof that a shipment can travel between those places. The inspector states this for modeled transport edges.
- NASA composite imagery has limited city-level detail. Street detail is provided as a separate basemap choice. The locations and commercial relationships remain synthetic at every zoom level.
- Cesium's Earth explorer is loaded as a separate lazy chunk. The production build reports about 4.23 MB raw / 1.15 MB gzip for that chunk; the initial application JavaScript is about 221 KB raw / 71 KB gzip. Build output warns about the Earth chunk size, so opening the map requires a larger first map download.

## Verification performed

- Built with Vite 7.3.7 and TypeScript 5.9.2; the browser uses the same local REST API and graph-derived data as the MCP service.
- Ran the page in the `agent-browser` Chrome session at 1440×1000 and 390×844 viewports; checked global Earth, location selection, supplier selection, city-reference zoom, and recovery.
- Completed the guided synthetic flow in the browser: reset, trigger foundry outage, assess, optimize, execute, and verify. The displayed baseline allocation was 350 inventory units plus 650 units from independent supplier D, at modeled cost USD 5,850; the UI reported ERP read-back verification. These are fixture outputs, not business measurements.
- Axe-core 4.12.1 reported zero WCAG 2.0 A/AA violations in the audited desktop and phone page states, including selected city-reference details. It left one color-contrast check incomplete for map/list content partly obscured by the map viewport. These automated scans are not a full WCAG or assistive-technology evaluation.
- No formal participant usability study or cross-browser/device test was performed.
