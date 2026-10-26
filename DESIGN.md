# GitHub profile design

## 0. Research log

Consulted live: DenverCoder1/DenverCoder1 (animated SVG headline, visual project links), codeSTACKr/codeSTACKr (theme-aware images and collapsed sections), timburgan/timburgan (issue-triggered interactive game), Platane/snk (animated contribution graphics), GitHub's writing quickstart and github/markup (allowed markup and sanitization). No third-party profile artwork is copied.

The original github-readme-stats repository currently says it is unmaintained and warns that its public endpoint is unreliable. Generate first-party images from live public GitHub data instead. Game moves that create issues are deliberately omitted: the requested profile should not require visitor-created issues or write-capable handlers for untrusted events.

Queried OMH local palette, font and UX reference data for dev-tool and portfolio contexts. Borrow the mono/display distinction and legible layered surfaces; use the identity-specific palette below.

## 1. Atmosphere and identity

Primary direction: bold / expressive, with restrained security-console details. Precise, technical, composed. Audience: engineering collaborators and security recruiters. Signature: an animated command line beneath an oversized name, paired with a packet-route shield illustration. No hacker stock imagery, emoji, view counters, false terminal output or invented performance figures.

## 2. Color

Dark: background #0D1117, surface #161D27, border #303B49, text #F0F6FC, secondary #AAB8C7, cyan #64D8ED, mint #72E1B3. Light: background #F6F8FA, surface #FFFFFF, border #CBD5E1, text #182434, secondary #526171, cyan #096B80, mint #16704B. Accent budget under 15% of image area. Text uses high-contrast tokens; subdued grid lines are decorative only. GitHub owns surrounding Markdown colors.

## 3. Typography

Display and prose in SVG: system-ui, -apple-system, Segoe UI, sans-serif. Console labels: ui-monospace, SFMono-Regular, Consolas, monospace. Native Markdown uses GitHub's typography. Desktop hero name 68px; compact hero 48px. Card titles 32px desktop / 27px compact. Body 20px desktop / 18px compact. Native Markdown carries the essential content and project descriptions for accessible reading and image failure.

## 4. Spacing and layout

Base unit 8px; padding 32/40px desktop and 24px compact. SVGs responsive at full available width; separate compact compositions selected with picture at 600px, not miniature desktop text. Native Markdown sections and disclosures avoid table-based side-by-side layouts. Validate at 1440, 768 and 375px without horizontal page overflow. Root README, assets, scripts and workflow form the publishable repository; evidence stays outside it.

## 5. Components

Hero: theme-aware SVG with original geometric artwork and an animated typing/reveal line. Navigation: linked 128x36 SVG buttons for portfolio, LinkedIn and email, wrapping naturally. Projects: full-width clickable original SVG cards plus native-text descriptions. Tools: compact text badges, no unlicensed logos. Disclosures: native details/summary for experience, activity, hint and solution. No custom form or disabled/loading controls. Broken assets retain descriptive alt text; data refresh fails loudly and keeps last committed assets.

## 6. Motion and interaction

Hero command reveals over 2 seconds and cycles on a 14-second loop; cursor blink slower than 1Hz. Contribution scanner traverses the real calendar over 14 seconds; it is an animation, not a playable snake. Reduced-motion picture sources select explicitly static SVG variants; CSS media queries inside image documents alone were insufficient in the tested browser. Static variants remove motion nodes and force the complete command line to remain visible. Avoid animation on body paragraphs. Clicking cards opens the actual repository. Disclosures work with mouse, touch and keyboard. Mini-puzzle answers are reveals, not an online flag checker.

## 7. Depth and surface

Flat bordered panels. No glass, glow, blur, generic gradient or blanket shadows. A small cyan edge and packet-routing diagram establish the security theme.

## 8. Accessibility and accepted limits

Alt text on every image; native summary and anchor semantics; essential facts repeated as native text. Graphics contain title and description. Native links preserve GitHub focus styling. The README cannot host JavaScript, embedded forms or custom CSS. Theme and responsive image behavior are tested in a browser, but GitHub-hosted rendering remains unverified until the user publishes. Auto-refresh workflow is prepared and its Python generator exercised locally; no remote Actions run is claimed. Performance budget: no third-party runtime image calls, under 500KB total README image assets, no JavaScript on the rendered profile.
