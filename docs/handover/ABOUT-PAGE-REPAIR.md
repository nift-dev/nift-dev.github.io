# About page: layout and code repair — artwork regeneration still pending

## Scope and honest status

This repair starts from `nift-about-poster-page(2).zip`: source branch `stage`
at `21e9d37`, generated checkout `public/main` at `af48d37`, with the supplied
uncommitted About-page/theme/navigation work retained.

**The requested twelve independently generated, high-resolution raster
illustrations have NOT been completed.** The image generator repeatedly returned
full-page website mockups, including after an isolated hero reference was supplied.
Those mockups were not used. No SVG replacements or vector reinterpretations
were introduced.

The current twelve WebPs are **retouched versions of the supplied raster assets**.
Their original dimensions/resolution and subjects are retained; they are not new
standalone generations and are not upscaled. Border pixels and stray poster
caption fragments were inpainted, and the outer backdrop pixels were softly
feathered. The terminal and document lettering is now real HTML positioned inside
the artwork column, not baked into the image. The N emblem and pictorial UI
symbols remain part of the artwork.

The retouching is an interim cleanup, not a substitute for the requested complete
artwork regeneration. Original poster-derived framing and low resolution remain
limitations. Do not describe these files as newly generated or fully reconstructed.

## Completed page/code repairs

- Preserve the existing general page template, site header/footer/navigation,
  typography, favicon and `#02090e` site background.
- Keep the same hero → introduction/example → two-column capability grid →
  closing structure. No poster is embedded as a single page image.
- Give copy and images independent grid cells. Below 901px the capability grid
  becomes one column; below 541px each card stacks copy above its illustration.
  There are no absolute-positioned background images under the card copy.
- All twelve illustration elements use `object-fit: contain`, automatic height,
  intrinsic width/height attributes, and separate layout space. The page does not
  crop them with `cover`. This does not reconstruct content missing in the source
  poster-derived raster files.
- Each card owns one CSS border; its artwork container has no additional border
  or overlay. Removed baked-in right-edge poster border pixels as part of retouching.
- Dark code surface: **`#181816`**, warm-neutral charcoal. Controls: `#242420`;
  borders: `#363630`; inline chips: `#252521`. No blue bias in these backgrounds.
  Includes documentation, examples, quickstart, homepage demo and install command.
- The About example is one semantic `<pre><code>` block, not six inline-code
  chips or an image. Gutter and caption are outside the code/copy payload.
- The Nift build engine escapes markup inside code examples. Do not place
  highlighting `<span>` elements in the source example: they render literally.
  `data-about-template` enables a narrow DOM-based three-token highlighter in the
  existing script, retaining the exact underlying code text and working offline.
- Copying the example returns the literal six-line template with `$[post.title]`
  and `$[post.excerpt]`, not line numbers, captions or HTML span tags.

## Asset replacement contract

The image files are ordinary directly maintained public assets, in
`public/assets/images/about/`. Keep these names for a later real artwork pass:

`hero.webp`, `websites.webp`, `frontend.webp`, `automation.webp`, `shell.webp`,
`data.webp`, `game.webp`, `desktop.webp`, `agents.webp`, `packages.webp`,
`creators.webp`, `closing.webp`.

Generate the complete subjects with space around them, no card frames, no baked
headings/captions and no cropped subject extremities. Preserve the approved
cinematic glass/neon/mountain style. Hero needs the moonlit lake and three-layer
Nift stack; closing needs its own wide mountain/lake scene. Keep the existing
logo/favicon. Do not try another full-page mockup → crop or SVG shortcut.

Update the image width/height attributes when replacing assets. Terminal/data
HTML labels are positioned for the present artwork and must be adjusted or
removed if a new composition differs; do not let them drift outside the image.

## Validation

The supplied Nift source compiled successfully and reports **Nift v4.5.0**.
No Nift engine/version/source changes were made as part of this website repair.
The command in this supplied version is `nift build --all`, not `build-all`.

```sh
make -C ../nift -j4
../nift/nift build --all
../nift/nift build
../nift/nift status
python3 scripts/check_handover_display.py
python3 scripts/check_script_extensions.py
python3 scripts/check_syntax_highlight.py
node --check public/assets/js/script.js
python3 scripts/check_about_render.py --chromium /usr/bin/chromium
```

The render check uses the actual built HTML/CSS/JS/image bytes offline and covers
22 width/theme combinations (320–1440px, dark and light), ten card copy/art
separations, image containment, single CSS borders, image loading, HTML art-label
containment, literal code contents, token highlighting, copy payload, and menu /
theme controls. It also checks the effective dark code backgrounds on the
homepage, examples, getting-started and lambdas/closures pages.

The container's Chromium policy rejected direct file/loopback navigation. No
policy was disabled. The test embeds the actual local assets into a blank
browser document, with in-memory localStorage for theme state, and blocks all
network requests. This validates layout and local scripting, **not** HTTP/file
origin behaviour, the remote highlighter CDN, storage persistence, or Vantage /
WebKit itself. Screenshots made by this test are actual HTML renders, not mockups.

The optional render test needs Python `playwright`, `beautifulsoup4` and a
Chromium binary; it does not add runtime dependencies to the website.

## Repository/publication

Commit `public/main` first, then `stage` including the updated Git-linked public
entry. Keep both `.git` directories when packaging; unzip into a separate
location and verify both Git statuses and HEADs. No push or tag is part of this
repair.
