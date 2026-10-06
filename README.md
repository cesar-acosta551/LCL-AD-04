# LCL-AD-04 — Lenker Display Ads

A lightweight static review gallery and handoff library for the approved Lenker display-ad campaign: **4 concepts × 6 formats = 24 standalone HTML executions**. No framework, build step, npm dependencies, or external asset service is required.

**Repository:** [cesar-acosta551/LCL-AD-04](https://github.com/cesar-acosta551/LCL-AD-04)  
**Public gallery (deployment target):** [LCL-AD-04 gallery](https://cesar-acosta551.github.io/LCL-AD-04/)

Publication is pending. These URLs identify the intended release; local validation does not establish a successful public deployment.

## Creative concepts

| Concept | Name | CTA |
|---|---|---|
| A | The Number | Why me? |
| B | We did our job | See how |
| C | We found you | Show me |
| D | No waste | See how |

- **A:** “This ad is for about 400 people.” Support: “Marketing leaders in Minnesota. You're one.”
- **B:** “If you're seeing this, we did our job.” Support: “Precise targeting, measured all the way to revenue. This ad is the demo.”
- **C:** “We found the 400 marketing leaders worth reaching.” Support: “Imagine what we'd do with your audience.”
- **D:** “No wasted impressions.” Support: “Not on you, and not on your customers.”

Source wording, line breaks, typography, colors, image assignments, crops, and animation are preserved.

## Formats

Each concept includes **300×250, 336×280, 160×600, 300×600, 1080×1080, and 1200×628**. These are exact standalone canvas dimensions. Gallery previews scale down to fit their cards without changing the production HTML. Use **Open ad** for a native-size review.

## Directory structure

```text
LCL-AD-04/
├── .github/workflows/pages.yml
├── ads/                       # Lenker_{A|B|C|D}_{width}x{height}.html
├── assets/                    # Four approved images + gallery.css/gallery.js
├── scripts/validate.py
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .nojekyll
├── README.md
├── NOTICE.md
├── index.html
└── manifest.json
```

## Preview locally

From the repository root:

```bash
python3 -m http.server 8000
```

Visit `http://localhost:8000/`. Stop with Ctrl+C. Test desktop and mobile gallery widths and open individual ads at their native dimensions; avoid relying solely on `file://` previews.

To emulate the GitHub Pages project prefix, serve the parent directory instead:

```bash
python3 -m http.server 8000 --directory ..
```

Then visit `http://localhost:8000/LCL-AD-04/`.

## Validate

```bash
python3 scripts/validate.py
```

Python 3.10+ and the standard library are sufficient. The validator checks the complete 24-unit inventory, manifest metadata, exact declared canvas dimensions, gallery links and iframe inventory, local HTML/CSS asset references, required root files, and invalid production paths. It returns a non-zero status on failure and reports counts. Static validation does not substitute for visual/browser QA.

## GitHub Pages deployment

The workflow validates the release, stages only the public site files, uploads a Pages artifact, and deploys it. It runs on pushes to `main` and manual dispatch. The root `index.html`, ads, assets, manifest, notice, and `.nojekyll` are included; Git history, scripts, and local QA artifacts are excluded from the site artifact.

1. Publish this independent repository as **public** at `cesar-acosta551/LCL-AD-04`.
2. In **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**.
3. Push `main` or run **Deploy LCL-AD-04 to GitHub Pages** from Actions.
4. Verify the workflow and deployment succeed, then test the actual public gallery and direct ad URLs.

The workflow follows [GitHub's custom Pages workflow conventions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). Relative URLs support `/LCL-AD-04/`; no domain-root routing is assumed.

Representative direct URL after publication:
`https://cesar-acosta551.github.io/LCL-AD-04/ads/Lenker_A_300x250.html`.

## clickTag behavior

Clicking anywhere in an ad opens a new tab. Destination priority is `window.clickTag`, then the `clickTag` query parameter, then the preserved fallback `https://www.lenker.com/`.

Example: `ads/Lenker_A_300x250.html?clickTag=https%3A%2F%2Fexample.com`.

Gallery previews retain the same behavior; **Open ad** opens the standalone unit without triggering its campaign destination. Confirm the destination and platform click macro before trafficking.

## Assets and production notes

The approved images are `A.jpeg`, `B.jpeg`, `C.jpeg`, and `D.png`. Each concept uses its matching image across six formats. No hero images are regenerated or recompressed. Images, CSS, and JavaScript used by the gallery live in this repository; ads use system font fallbacks and require no font download. See [NOTICE.md](NOTICE.md) for usage terms; public source availability is not a reuse license.

The original creative uses subtle continuous image animation and small supporting text in compact formats. These treatments are preserved and should be reviewed against the destination platform's animation, accessibility, and legibility requirements. This repository is an ad review library, not a platform-specific trafficking ZIP. Verify platform payload limits and packaging requirements: the four source images are roughly 0.9–2.6 MiB each.

## Future revisions

Work in this repository on a revision branch. Preserve the approved source imagery and creative unless a change is explicitly approved. Keep all six exact formats per concept; update the manifest and gallery if inventory changes. Run the validator, then inspect all 24 standalone units and the gallery over HTTP at desktop and mobile sizes, including the project prefix. Review the diff, commit, and publish through the Pages workflow. Confirm the actual public URLs after every deployment. Never force-push or replace unrelated remote content.

If GitHub CLI is unavailable, install it and authenticate with `gh auth login`, then confirm `gh auth status`. Inspect `cesar-acosta551/LCL-AD-04` before creating or connecting the remote; do not overwrite a non-empty repository.
