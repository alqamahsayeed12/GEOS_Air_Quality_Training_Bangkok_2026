# Changelog

## 2026.09.10

- Lock the finalized Day 1 science presentation by commit and SHA-256 checksum.
- Add a separate 12-page training roadmap covering every notebook section,
  participant decision, checkpoint, output, and scientific invariant.
- Add real Module 2 and Module 3 output figures to the roadmap and link it from
  the course portal.
- Reframe the visible Day 1 narrative around people, places, scientific evidence,
  and practical interpretation while preserving technical definitions and sources.
- Remove the short blue underline beneath the centered navigation title.
- Remove navigation arrows and strengthen the visual emphasis of the centered
  current-page title relative to the previous and next page labels.
- Modernize page navigation with a translucent bar, adjacent-page hierarchy,
  animated circular chevrons, and a restrained active-page indicator.
- Replace the training-label and arrow-only navigation with centered current-page
  context and named previous/next page controls.
- Smooth forecast playback by caching wind fields, decoupling wind updates from
  PM2.5 crossfades, avoiding raster-layer reordering, and preventing timer overlap.
- Rename the closing-page navigation label from `Web View` to `Forecast Explorer`.
- Reframe the closing forecast explorer as `From concepts to application`.
- Rename the day-1 ground-network comparison navigation label to `GEOS Performance`.
- Replace the Thai-only local-evaluation scatter with a matched forecast-day-1
  comparison of Thai PCD and Lao PDR AQMS observations.
- Use common axes, consistent QA/QC, shared relative-density coloring, and N,
  IOA, correlation, slope, RMSE, and mean-bias annotations.
- Remove the duplicated figure heading and place the shared density colorbar
  below both scatter panels so neither plot is obstructed.
- Increase small scientific labels, captions, citations, diagram text, and
  forecast-interface text across the Day 1 presentation for room readability.
- Raise the remaining effective minimum font size from 10 px to 14 px in two
  review passes and widen compact map controls to accommodate the larger text.
- Increase every explicit presentation font size by an additional 2 px while
  preserving the existing typographic hierarchy.
- Restore the compact partner-logo header and convert navigation to page-wise
  previous/next controls, a page selector, counter, and slide snapping.
- Limit page navigation to the 11 visible top-level presentation pages and
  exclude hidden hands-on supplemental sections from the page count.
- Add a compact desktop profile for displays up to 1050 px high, reducing excess
  spacing and media height while keeping all 11 pages within the viewport.
- Use immediate page-to-page navigation so slide selection stays aligned with
  the viewport and page counter.
- Simplify the presentation navigation to compact back/next controls and an
  unnumbered current-page title.
- Add concise story-based navigation labels for the visible presentation pages
  while preserving their detailed scientific headings.
- Separate GEOS and The Framework into consecutive presentation pages, giving
  the overview and the processing workflow distinct narrative space.
- Merge initial/boundary-condition material into The Framework as a regional
  coupling view, and rename the Modeling navigation label to GEOS Products.
- Reformat GEOS product timeline bars as two-line labels so descriptors and
  forecast periods remain readable without truncation.
- Realign the downstream navigation labels after merging the coupling page so
  each label matches its visible scientific content.
- Label the smoke, haze, dust, and transport page as Regional Air Quality
  Impacts, and distinguish the later model-evaluation page as Regional Air
  Quality 2.
- Move the PM2.5 atmospheric budget and GEOS-variable mechanism into The
  Framework as a third view, removing it from the standalone page sequence.
- Move Regional Air Quality Impacts directly before the Regional Air Quality 2
  scatter-comparison page to strengthen the narrative transition.

## 2026.09.9

- Preserve the complete NASA smoke/haze and dust scenes in the PM2.5 case-study
  gallery instead of cropping them to wide frames.
- Move case captions below the imagery so labels no longer obscure the maps.

## 2026.09.8

- Add a Day 1 slide explaining primary and secondary PM2.5 formation through
  Southeast Asian smoke/haze and Asian dust case studies.
- Connect local emissions to regional transport, visibility, radiation, cloud,
  and deposition effects using attributed NASA MODIS imagery.

## 2026.09.7

- Add the NSF NCAR atmospheric-process schematic to the Day 1 initial and
  boundary conditions section.
- Preserve the GEOS forcing pathways in a compact side-by-side layout with
  explicit scientific attribution and source links.

## 2026.09.6

- Revise the Day 1 presentation in a professional scientific register.
- Replace conversational prompts and simplified slogans with precise language
  on GEOS products, model coupling, PM2.5 health evidence, and evaluation.

## 2026.09.5

- Shorten the Day 1 presentation to the overview, GEOS, PM2.5, local
  evaluation, and interactive forecast content.
- Remove the hands-on and notebook-training sequence from the presentation
  navigation and rendered page.

## 2026.09.4

- Add the University of Alabama in Huntsville logo to the public course portal
  with responsive desktop and mobile header sizing.

## 2026.09.3

- Execute all four participant notebooks in a clean public-clone audit.
- Add a scheduled GitHub Actions workflow that reruns every notebook with
  bundled recovery data.
- Add stable Jupyter cell IDs and reject workstation paths in saved outputs.

## 2026.09.2

- Canonicalize packaged CSV files to LF so checksums are identical on macOS,
  Linux, GitHub Actions, and Colab.
- Upgrade GitHub Actions to Node 24-compatible major versions.

## 2026.09.1

- Package Modules 0-3 for Google Colab and local Jupyter.
- Bundle compact data, scalar tables, v3.1 models, and presentation assets.
- Add live-first Module 1 acquisition with disclosed offline recovery snapshots.
- Pin the tested Python environment and add static and runtime GitHub checks.
- Add checksums, maintenance instructions, and release recovery guidance.
