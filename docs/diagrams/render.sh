#!/usr/bin/env bash
# Render every .mmd diagram in this directory to SVG + PNG using mermaid-cli.
#
# Usage:  ./render.sh            # renders all *.mmd to *.svg and *.png
#         ./render.sh pipeline-dag   # render a single diagram by basename
#
# Requires: Node 18+ (uses npx to fetch @mermaid-js/mermaid-cli on first run)
#           and a local Chrome/Chromium/Edge/Brave install for the headless render.
#
# Note: mermaid-cli renders via a headless browser. In restricted/sandboxed
# shells the browser may be blocked from launching — run this in a normal
# terminal. The inline ```mermaid blocks in ../workflows-and-architecture.md
# render automatically on GitHub and in VS Code with no tooling at all.
set -euo pipefail
cd "$(dirname "$0")"

# --- locate a browser ------------------------------------------------------
find_browser() {
  for p in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
    "$(command -v google-chrome-stable || true)" \
    "$(command -v chromium || true)"; do
    [ -n "$p" ] && [ -x "$p" ] && { echo "$p"; return 0; }
  done
  return 1
}

BROWSER="$(find_browser || true)"
if [ -z "$BROWSER" ]; then
  echo "No Chrome/Chromium found. Install one, or let mermaid-cli download Chromium:"
  echo "  npx puppeteer browsers install chrome"
  PUPPETEER_JSON='{ "headless": "new", "args": ["--no-sandbox"] }'
else
  echo "Using browser: $BROWSER"
  PUPPETEER_JSON="{ \"executablePath\": \"$BROWSER\", \"headless\": \"new\", \"args\": [\"--no-sandbox\", \"--disable-gpu\"] }"
fi

# A local .puppeteerrc.cjs keeps puppeteer's config search from walking up into
# parent directories (which can hit permission errors in some setups).
printf 'module.exports = {};\n' > .puppeteerrc.cjs
echo "$PUPPETEER_JSON" > .puppeteer.runtime.json
trap 'rm -f .puppeteerrc.cjs .puppeteer.runtime.json' EXIT

targets=()
if [ "$#" -gt 0 ]; then
  for name in "$@"; do targets+=("${name%.mmd}.mmd"); done
else
  for f in *.mmd; do targets+=("$f"); done
fi

for f in "${targets[@]}"; do
  base="${f%.mmd}"
  echo "=== $f -> $base.svg / $base.png ==="
  npx -y @mermaid-js/mermaid-cli@11 -i "$f" -o "$base.svg" \
      -c mermaid-config.json -p .puppeteer.runtime.json -b transparent
  npx -y @mermaid-js/mermaid-cli@11 -i "$f" -o "$base.png" \
      -c mermaid-config.json -p .puppeteer.runtime.json -b white -s 2
done

echo "Done. Generated:"
ls -1 *.svg *.png 2>/dev/null || true
