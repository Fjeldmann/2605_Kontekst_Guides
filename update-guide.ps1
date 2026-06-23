<#
  update-guide.ps1
  Full pipeline: screenshots → annotate → compile PDF

  Usage:
    .\update-guide.ps1 [-Version "v0.3.0"] [-SkipScreenshots] [-SkipAnnotate]

  Flags:
    -Version        New version string for the output PDF (e.g. "v0.3.0").
                    Defaults to bumping the patch of the latest existing PDF.
    -SkipScreenshots  Skip the Playwright step (use existing raw images)
    -SkipAnnotate     Skip the Python annotation step
#>

param(
  [string]$Version = "",
  [switch]$SkipScreenshots,
  [switch]$SkipAnnotate
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

# ── Version detection ─────────────────────────────────────────────────────────
if (-not $Version) {
  $existing = Get-ChildItem $Root -Filter "kontekst-chat-guide v*.pdf" |
    Sort-Object Name | Select-Object -Last 1
  if ($existing) {
    if ($existing.Name -match 'v(\d+)\.(\d+)\.(\d+)') {
      $patch = [int]$Matches[3] + 1
      $Version = "v$($Matches[1]).$($Matches[2]).$patch"
    } else {
      $Version = "v0.3.0"
    }
  } else {
    $Version = "v0.3.0"
  }
}
$OutPdf = "kontekst-chat-guide $Version.pdf"
Write-Host "`nBuilding guide $Version → $OutPdf" -ForegroundColor Cyan

# ── 1. Screenshots ────────────────────────────────────────────────────────────
if (-not $SkipScreenshots) {
  Write-Host "`n[1/3] Taking screenshots with Playwright..." -ForegroundColor Yellow

  $EnvFile = Join-Path $Root "scripts\.env"
  if (-not (Test-Path $EnvFile)) {
    Write-Error "Missing scripts\.env — copy scripts\.env.example and fill in your credentials."
  }

  Push-Location (Join-Path $Root "scripts")
  try {
    if (-not (Test-Path "node_modules")) {
      Write-Host "  Installing npm dependencies..."
      npm install
      npx playwright install chromium
    }
    node take-screenshots.js
  } finally {
    Pop-Location
  }
} else {
  Write-Host "`n[1/3] Skipping screenshots (--SkipScreenshots)" -ForegroundColor DarkGray
}

# ── 2. Annotate images ────────────────────────────────────────────────────────
if (-not $SkipAnnotate) {
  Write-Host "`n[2/3] Annotating images..." -ForegroundColor Yellow
  python (Join-Path $Root "annotate_images.py")
} else {
  Write-Host "`n[2/3] Skipping annotation (--SkipAnnotate)" -ForegroundColor DarkGray
}

# ── 3. Compile PDF with Marp ──────────────────────────────────────────────────
Write-Host "`n[3/3] Compiling PDF with Marp..." -ForegroundColor Yellow
$MdFile = Join-Path $Root "kontekst-chat-guide.md"
$PdfOut = Join-Path $Root $OutPdf

Push-Location $Root
try {
  npx --yes @marp-team/marp-cli@latest "$MdFile" --pdf --allow-local-files -o "$PdfOut"
} finally {
  Pop-Location
}

Write-Host "`nDone! Output: $OutPdf" -ForegroundColor Green
