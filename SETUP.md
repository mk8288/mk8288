# Publish this profile

## Upload

This folder is the contents of your profile repository, **mk8288/mk8288**. Your current default branch is `main`.

1. Keep a copy of your existing profile README before replacing it.
2. Upload `README.md`, the complete `assets/` folder, `scripts/`, `data/`, and `.github/workflows/refresh-profile.yml` to the repository root. Keep the folder structure. Do not upload the enclosing `github-profile-readme` folder itself.
3. Commit to `main`. Review the README on both your repository and profile page.
4. In the repository's **Actions** tab, open **Refresh profile artwork** and run it once. Its scheduled trigger is `23 6 * * *` (06:23 UTC daily); GitHub can delay scheduled runs.
5. If a repository or organisation policy denies the bot write access, permit the workflow's `contents: write` access, or keep the supplied static assets and refresh them locally. Protected branches may also prevent direct bot commits.

The checked-in images already work without Actions. The workflow updates their underlying public-data snapshot. You do not need a personal access token; the workflow uses GitHub's built-in `GITHUB_TOKEN`. No private repository content is collected.

If you use Git locally, copy the package into a checkout of your existing profile repository and review `git diff` before committing. No script in this package publishes or pushes when you run it locally. Only the installed GitHub Actions workflow contains a push step.

## What is animated or interactive

- The original SVG hero types a short command line and animates a packet through a shield-shaped route.
- The three project cards and contact buttons are links.
- Experience, education and contribution sections expand when clicked.
- The contribution graphic scans across real calendar data. It is an animation, not a playable snake game.
- The mini CTF has a hint and a solution reveal. It does not submit flags or record players.
- Light/dark colors follow the reader's color-scheme preference. Compact image compositions are selected on viewports at or below 600px. GitHub's actual selection can follow browser preferences rather than a manually forced site theme.
- The original animated images include a reduced-motion treatment. Their essential information is also available as text or image alt text.

GitHub sanitizes README HTML: scripts, inline styles and custom classes are removed. A genuinely playable browser game needs a separate page or a repository event workflow, such as the issue-driven chess example linked below. This package intentionally creates no public-issue game handlers.

## Local refresh

Python standard library only; no packages to install.

```bash
python3 scripts/build_profile.py
```

This fetches your public GitHub user record, all public owned repository pages, and the public contribution-calendar HTML. It validates the repository and calendar totals before generating images. An optional `GITHUB_TOKEN` environment variable is used only for requests to `api.github.com`. Never place a token in the README or pass it as a command-line argument.

To regenerate artwork without network access using the dated snapshot already included:

```bash
python3 scripts/build_profile.py --offline
```

If GitHub changes the calendar markup or an API request fails, the build fails rather than inventing data. A failed Actions refresh leaves the last committed images available. A stale snapshot remains visibly dated.

## Editing

- Personal text and the small puzzle: `README.md`.
- Artwork, project labels, colors and layout: `scripts/build_profile.py`.
- Automation schedule: `.github/workflows/refresh-profile.yml`.
- Design rationale: `DESIGN.md`.
- Source data and retrieval timestamp: `data/github-public.json`.

Generated graphics are original to this profile. No third-party logos, trophy graphics or stock profile artwork are bundled. Do not replace the checked-in assets with a public image service unless you accept that service's availability and caching behavior.

## References and inspiration

- GitHub profile setup: https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme
- Theme-aware images and expandable sections: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github
- GitHub HTML sanitization: https://github.com/github/markup
- Animated profile example: https://github.com/DenverCoder1/DenverCoder1
- Theme-aware profile example: https://github.com/codeSTACKr/codeSTACKr
- Issue-driven interactive chess: https://github.com/timburgan/timburgan
- Typing SVG tool: https://github.com/DenverCoder1/readme-typing-svg
- Contribution snake alternative: https://github.com/Platane/snk
- Gallery of profile approaches: https://github.com/abhisheknaiidu/awesome-github-profile-readme
- Why the old public stats widget was not used: https://github.com/anuraghazra/github-readme-stats

## Verification boundary

Local generation and preview tests do not prove that a published profile or its scheduled workflow works. After publishing, check the profile page and the latest **Refresh profile artwork** run in this repository's Actions tab. The dated snapshot in `data/github-public.json` identifies the data used for the current generated images.
