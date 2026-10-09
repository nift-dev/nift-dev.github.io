# NIFT v4.10 — BUILD-SYSTEM WEBSITE DOCUMENTATION

Runtime source verified: `c46c36e78176d37c50576eb184d2c41da3121276`. The workflow contract is unreleased v4.10 and both pages explicitly distinguish it from stable v4.9.

## Audit and information architecture

Existing migrations/rewrites/redesigns describe adoption and preservation. Build Scripts covers lifecycle mechanics, Incremental Builds covers invalidation, Minification covers format policy, Scripting covers APIs, and Text Assets covers native text composition. The missing material was a complete artifact graph and the boundary between orchestration and specialist transformations. Two workflow pages fill that gap; references cross-link instead of duplicating their entire contracts.

WORKFLOWS & PATTERNS pages added: **General build systems** and **Asset pipelines**, first in the existing group. Pages expanded with contextual links: docs overview, Build Scripts, Incremental Builds, Minification, Scripting and Text Assets. Existing low-level tracked/dependency/CLI/filesystem references are linked from both workflows.

## Coverage

General build-system role: YES. Named inputs/outputs, hooks, custom build versus render, incremental reasons, optional `depends`, parallel readiness and failure propagation: documented. Make/Ninja overlap and migration: careful artifact/command/edge mapping, with no automatic conversion or parity promises. Unsupported performance claims: NONE. npm/task-runner sequencing and retained package managers: documented. Human/agent graph visibility: factual, without marketing expansion.

CSS: native text/render/minification or external Sass/PostCSS/Tailwind/Lightning CSS. JavaScript: compatible classic-script composition is distinguished from specialist module bundling/TypeScript/chunking. Assets: manifests, SVG text handling, image encoder recipes and other generated artifacts. Minification: normal project/tracked opt-in configuration; custom `build` bypasses automatic minification and must call native minification explicitly when desired. Hooks cross-linked: YES.

Parallel example: styles/frontend-js/images → asset-manifest → home. Complete build example: generated-api → app-js → manifest. Completion-only `depends` edges are distinguished from ordinary file invalidation; both are included where consumer bytes depend on prerequisite outputs.

One declared output per item: YES. WebP and AVIF use separate tracked items. Extra bundler files require deliberate ownership/cleanup; multiple-output syntax is not documented as current. Future multioutput dogfooding and 10k/50k/100k Nift/Make/Ninja graph comparisons are internal notes in the runtime handover, not website performance claims.

Homepage/about reviewed: existing terminology retained; no identity change requiring review. Battle Tested unchanged: no Make-replacement claim from tests alone.

## Verification

- Two source-only deterministic downloadable archives match the example project files byte-for-byte; tracking JSON and displayed native/general/external recipes match their source.
- Both extracted projects pass targeted builds, full rebuilds, clean no-op metadata checks, same-pass source-change propagation, JSON parsing and Node syntax checks. Asset pipeline additionally propagates CSS edits through manifest and page.
- Real installed Sass (Ruby Sass 3.7.4) and ImageMagick 7.1.2 WebP/AVIF wrappers produce outputs; compiler failure fails the build. Sass documentation points to the current Dart Sass CLI; the local execution is not a Dart Sass certification. esbuild CLI syntax checked against its official reference; executable unavailable locally, so no executed-bundler claim.
- Site build: PASS. Canonical mirrored documents: PASS. Internal references: 19,840 checked. Two documentation menus and route metadata: PASS. Sitemap: 100 URLs. Syntax and script-extension checks: PASS.
- 94-page docs audit: PASS, no accidental orphan pages. Three legacy aliases remain intentional. Site-wide search: no existing search index/implementation to update; both pages appear in sitemap and navigation.
- Browser visual/geometry inspection: both pages at 1280×900 and 390×844 PASS. Mobile documentation menu exposes both workflow links. Document widths 1265/375 pixels respectively; long code scrolls within its block. Inspection caught and fixed an existing mobile intrinsic-width overflow; stylesheet version marker refreshes cached clients. Saved desktop/mobile screenshots accompany this report.

## Publication

Use established generated `public` main commit/push first, then source `stage` commit/push carrying its updated public pointer. These commits contain documentation, example archives and the verified CSS correction. No runtime or release publication is part of this website tranche.

Generated public main published: `c2bd9c47f5cfd37e23a3693f9e3c41ff9a66a7b7`. Source stage publication is the commit containing this report and public pointer.
