---
name: certificate
description: |
  Generate a certificate of completion, prepend it as the first slide in the user's Marp presentation deck, render the full deck to PDF, and open LinkedIn for sharing. Use this skill whenever the user mentions "certificate", "completion certificate", "generate certificate", "add certificate", "I finished", "completed the analysis", "want to share my work", or invokes `/certificate`. This is a celebration moment — the skill handles the full ceremony: finding the user's deck, sourcing their name, generating a beautiful certificate slide, rendering the PDF, previewing it, and helping them share their accomplishment on LinkedIn with a well-crafted caption. Also trigger when users say "I finished my deck", "ready to share", "want to post to LinkedIn", or any context suggesting they've completed a major milestone and want to celebrate it. Treat it with appropriate gravity and celebration.
---

# Skill: Certificate

## Purpose
Generate a certificate of completion, prepend it to the user's Marp slide
deck as the first slide, render the full deck to PDF, and open LinkedIn for
sharing.

The user types `/certificate`, Claude does the rest.

## When to Use
- User says `/certificate` or "generate certificate" or "completion certificate"
- After completing a major analysis and having a finished deck

## Invocation
`/certificate` — generate a certificate of completion and add it to the deck

## Instructions

### Step 1: Find the Deck

Ask the user: **"Where's your output deck? (path to your `.marp.md` file)"**

If the user gives a path, use it. If they say something vague ("the deck",
"my slides"), look for `.marp.md` files:

```bash
find outputs/ -name "*.marp.md" -type f 2>/dev/null | head -5
```

If multiple decks exist, show the list and ask which one.

### Step 2: Get the User's Name

**Important:** If the user provided their name in the initial request (e.g., "my name is Alex Chen"), use that name directly and skip the sources below. The user's explicit input always takes priority.

Otherwise, try these sources in order — use the first one that returns a real name:

1. **Check `.knowledge/user/profile.md`** — look for `Name:` field
2. **Check git config:** `git config user.name`
3. **Ask the user:** "What name should go on the certificate?"

### Step 3: Generate Certificate HTML

Read the certificate template from this skill's references:
`references/certificate-template.html` (in this skill's directory)

Copy the **entire** HTML file and replace the two placeholders:
- `{{STUDENT_NAME}}` — the user's full name
- `{{DATE}}` — today's date formatted as `Month Day, Year` (e.g., "April 1, 2026")

Save the filled template as `certificate.html` in the repo root.

### Step 4: Render Certificate to PNG

```bash
node scripts/render-certificate.mjs certificate.html certificate.png
```

This produces a 3840x2160 retina PNG (2x scale of 1920x1080) — matches the
16:9 Marp slide dimensions exactly.

**If the render script fails** (missing Node.js, Chromium issues), use this fallback:

```bash
open certificate.html
```

Then tell the user: **"The certificate is open in your browser. Take a screenshot (Cmd+Shift+4 on Mac, Win+Shift+S on Windows), crop to exactly 1920x1080 pixels, save as `certificate.png` in the repo root, then let me know and I'll continue with the deck integration."**

### Step 5: Prepend Certificate to Deck

Read the user's `.marp.md` file. Find the end of the YAML frontmatter
(the closing `---`). Insert the certificate slide immediately after it,
**before** the first content slide:

```markdown
<!-- _paginate: false -->
<!-- _footer: "" -->

![bg](certificate.png)

---
```

This uses Marp's background image syntax to fill the entire slide with the
certificate PNG. The `_paginate: false` and `_footer: ""` directives hide
the page number and footer on the certificate slide only.

**Important:** The `certificate.png` path must be relative to the `.marp.md`
file location. If the deck is in `outputs/`, copy the PNG there too:

```bash
cp certificate.png outputs/certificate.png
```

### Step 6: Render Full Deck to PDF

Detect the theme from the deck's YAML frontmatter (`theme:` field), then
resolve the actual CSS file before rendering. Marp CLI cannot follow CSS
`@import` chains in custom themes, so you must resolve to the real stylesheet.

**Theme resolution:** Read `themes/DETECTED_THEME.css`. If the file only
contains an `@import` (e.g., `@import 'analytics-light'`), follow the import
and use the target file instead. Repeat until you reach a CSS file with actual
style rules.

```bash
# Example: frontmatter says theme: analytics
# themes/analytics.css contains only: @import 'analytics-light';
# → Resolve to themes/analytics-light.css (the real stylesheet)

npx @marp-team/marp-cli --no-stdin --pdf --html --allow-local-files \
  --theme themes/RESOLVED_THEME.css \
  DECK_PATH \
  -o "Certificate of Completion.pdf"
```

For example, if the deck is `outputs/deck_novamart_2026-04-01.marp.md` with
`theme: analytics` (which imports `analytics-light`):

```bash
npx @marp-team/marp-cli --no-stdin --pdf --html --allow-local-files \
  --theme themes/analytics-light.css \
  outputs/deck_novamart_2026-04-01.marp.md \
  -o "Certificate of Completion.pdf"
```

### Step 7: Copy PDF to Desktop and Open It

```bash
cp "Certificate of Completion.pdf" ~/Desktop/
open ~/Desktop/"Certificate of Completion.pdf"
```

Tell the user: **"Your Certificate of Completion is on your Desktop — take
a look!"**

This is the moment. Let them see the full deck with their certificate as the
first slide. Give them a beat before moving to LinkedIn.

### Step 8: Confirm Before LinkedIn

Draft a short LinkedIn caption that showcases what they built. The caption must be under 200 characters.

**Step 8a: Count the deliverables**

Extract a specific number to include in the caption:

1. **Count slides in the deck**: `grep -c '^---$' DECK_PATH` (subtract 1 for the frontmatter separator to get actual slide count)
2. **Count charts** (if charts/ directory exists): `ls -1 charts/ 2>/dev/null | wc -l`
3. **Use the more impressive metric**: If the deck has 43 slides, lead with that. If there are 18 charts but only 8 slides, lead with charts.

**Step 8b: Extract the analysis topic**

Read the deck's title to make the caption contextual (not generic):

```bash
head -50 DECK_PATH | grep '^# ' | head -1 | sed 's/^# //'
```

Use this topic in the caption. For example:
- "Checkout Feature Impact Analysis" → "analyzed checkout feature impact"
- "Q4 Conversion Trends" → "Q4 conversion analysis"

**Caption construction**:
1. Lead with the topic + the deliverable count
2. Add context about what they built (the AI analyst capability)
3. End with an engagement hook (question or curiosity gap)
4. Keep it under 200 characters — verify with: `echo -n "CAPTION" | wc -c`

**Caption rules**:
- Lead with what they built (the analysis topic + specific number)
- Include one concrete, specific number from the deliverables (slides, charts, or datasets)
- No hashtags, no emojis, no "I'm thrilled to announce"
- End with a short engagement hook
- Mention AI Analyst Lab naturally if it fits, but prioritize the work itself

**Example construction**:
- Topic: "NovaMart Checkout Feature Impact"
- Slide count: 43 slides
- Hook: "Want to see the full analysis?"
- Result: "Analyzed NovaMart checkout feature impact — 43 slides from question to recommendation. Here's my certificate. Want to see the analysis?" (140 chars)

**More examples** (adapt to actual numbers):
- "Built an AI analyst that generates experiment designs and impact forecasts. 18 charts from plain English questions. Here's the certificate."
- "Went from business question to 42-slide validated deck in 2 hours. Funnel breakdowns, root cause investigation, impact sizing. Done."

Ask: **"Here's the caption for LinkedIn. Want me to open LinkedIn so you can
post it, or change anything first?"**

Do NOT proceed until they confirm.

**Note for automated/test scenarios:** If user interaction isn't available (e.g., running in a test harness), document the confirmation step in your output and proceed with the drafted caption as the default.

### Step 9: Post to LinkedIn

```bash
# Copy certificate PNG to Desktop for upload
cp certificate.png ~/Desktop/certificate.png

# Copy the caption text to clipboard
echo -n "CAPTION_TEXT" | pbcopy

# Open LinkedIn with caption pre-filled
open "https://www.linkedin.com/feed/?shareActive=true&text=URL_ENCODED_CAPTION"
```

Tell the user:
**"LinkedIn is open with your caption pre-filled. Click the image icon in the
composer and upload `certificate.png` from your Desktop, then hit Post!"**

### Step 10: Clean Up

After they've posted (or decided not to), the temporary files can be deleted:

```bash
rm -f certificate.html certificate.png
```

Don't auto-delete — ask first or just mention they can clean up.
The `Certificate of Completion.pdf` on the Desktop is theirs to keep.

## Rules
1. The certificate must be exactly 1920x1080 (16:9) to match Marp deck slides
2. Always use the full HTML template from `references/certificate-template.html`
3. The certificate slide must be the FIRST slide in the deck (after frontmatter)
4. The rendered PDF must be named `Certificate of Completion.pdf`
5. Always open the PDF for preview, not the PNG
6. Always confirm with the user before opening LinkedIn
7. The LinkedIn caption must be under 200 characters
8. Never fabricate the user's name — always source it from profile, git, or ask
9. The certificate has three instructor signatures — do not modify the instructor names
