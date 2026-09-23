# About page — full-bleed artwork, corrected example and code surfaces

## Current scope / artwork provenance

This pass starts from `nift-about-layout-code-repair(1).zip` (source `1f58b70`,
public `851e991`). It retains the existing site template, favicon, navigation,
footer, typography and `#02090e` site background.

The artwork is **retouched/recomposed from the approved raster poster**, not a
set of twelve independently AI-generated illustrations. Individual-image requests
again produced full-page mockups; those generated mockups are not deployment
assets. No SVG illustrations replace the original glass/neon/mountain artwork.

`docs/artwork/about-poster-reference.png` is the original source reference and
is not published by Nift. `scripts/prepare_about_artwork.py` derives the hero and
ten card scenes reproducibly (optional Pillow/numpy/OpenCV asset-editing tools).
It removes poster copy and outer card rules, restores the original frontend and
terminal lower corners, and adds sky / shallow reflection margin without
stretching the subjects. The final WebPs retain the original raster detail;
they are not claimed to be newly generated high-resolution art. The existing
closing WebP is unchanged byte-for-byte.

The hero is now a 1024×376 text-free panorama, rather than the old 405×275 inset.
The title, description, values and small motto are actual HTML over/alongside it.
On small screens the main copy precedes the artwork.

## Layout contract

- Keep the two-column capability grid on desktop. Below 1101px it becomes one
  column; below 701px each card stacks its copy above the artwork.
- Card scenes fill the entire inner card surface, right up to the single CSS
  border. There is no extra raster frame or padded inset-image box.
- The left region of each desktop scene is intentionally dark/empty for copy.
  Foreground objects must not cross into that copy region.
- `object-fit: cover` may crop **landscape margins**, never the complete panes,
  terminal, files, controller or other main subjects. The render test checks
  native subject bounds, not just the image element's bounding box.
- Avoid excessively long card paragraphs which force tall, narrow crops. The
  card copy remains practical and links to the full relevant documentation.
- Terminal/data labels remain HTML. Their positions are mapped from native
  image coordinates, including `object-fit` offsets, by one ResizeObserver in
  the existing site script. Keep coordinates and intrinsic image dimensions
  synchronized with any replacement artwork.

## Code surfaces and example

- Shared warm-neutral code background: **`#20201e`** (darkened from `#242422`).
- Control background: `#2a2a27`; border: `#454540`. No blue bias in these fills.
- The About example remains one semantic `pre > code` with the normal token
  highlighter. It starts with **`@for(post : posts)`**, not `post in posts`.
- The code-copy button is attached to `.about-code-panel`, which is its
  positioned ancestor, and sits 10px from its inner top/right edges. Do not
  move it back into the narrower inner code-column wrapper.
- Copying produces only the six-line template; no gutter numbers, captions or
  generated highlighting markup enter the clipboard.
- `check_about_example.py` executes that exact displayed example with two data
  records using the supplied compiled Nift binary.

## Validation

The unmodified supplied Nift source compiled and reports **Nift v4.5.0**.
No Nift source/version/tag changes belong to this website pass.

```sh
make -C ../nift -j4
../nift/nift build --all
../nift/nift build
../nift/nift status
python3 scripts/check_about_example.py --nift ../nift/nift
python3 scripts/check_handover_display.py
python3 scripts/check_script_extensions.py
python3 scripts/check_syntax_highlight.py
node --check public/assets/js/script.js
python3 scripts/check_about_render.py --chromium /usr/bin/chromium
```

The full build covers 96 tracked files; the subsequent incremental build is a
no-op. Optional render QA covers 34 width/theme combinations from 320–1600px,
full-bleed boundaries, main-object/copy separation and subject containment,
image loading, HTML labels, literal template/highlighting, top-right button
geometry and its copy payload, and the shared menu/theme controls. It also
checks effective neutral code backgrounds on four other website surfaces.

Render tests use the actual local built HTML/CSS/JS/images in an offline
Chromium document. They do not test Vantage/WebKit, HTTP/file origin behavior,
persistent localStorage, OS clipboard integration, or the external syntax
highlight CDN. Preview PNGs from the render test are actual browser renders,
not generated design mockups. Optional QA dependencies are not site runtime
dependencies.

## Publication / packaging

Commit generated `public/main` first, then source `stage` including its updated
Git-linked `public` entry. Preserve both `.git` directories. Verify Git HEADs,
status and object integrity after unpacking the archive into a fresh directory.
No push or tag is part of this task.
