---
description: Update the Kontekst Chat guide PDF — takes fresh screenshots, annotates them, and compiles a new PDF via Marp. Run from the project root.
---

# /update-guide

Automates the full Kontekst Chat guide refresh pipeline. When invoked:

1. **Verify prerequisites**
   - Check that `scripts/.env` exists. If not, tell the user to copy `scripts/.env.example` and fill in their credentials, then stop.
   - Check that Python is available (`python --version`). If not, warn the user.

2. **Parse arguments** (from the user's message after `/update-guide`):
   - `-Version <x.y.z>` — override the version string (e.g. `/update-guide -Version v0.3.1`)
   - `-SkipScreenshots` — skip Playwright, use existing raw images
   - `-SkipAnnotate` — skip annotation step, use existing `_ann` images

3. **Run the pipeline** by executing `update-guide.ps1` in the project root with any parsed flags:
   ```powershell
   .\update-guide.ps1
   ```
   Or with flags:
   ```powershell
   .\update-guide.ps1 -Version "v0.3.1" -SkipScreenshots
   ```

4. **Monitor output** and report:
   - If Playwright fails on a selector, show the error and tell the user which selector in `scripts/take-screenshots.js` to update (look for `# SELECTOR:` comments).
   - If the PDF compiled successfully, report the output filename.
   - If Marp is slow on first run (downloading), note that subsequent runs will be faster.

5. **After success**, ask the user if they want to commit and bump the version in git.

## Selector troubleshooting

The most likely failure point is Playwright not finding a UI element. Each interactive step has a `// SELECTOR:` comment in `scripts/take-screenshots.js` explaining what to change. Read the error, find the matching comment, and update the locator string.
