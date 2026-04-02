# Skill: Show Off LinkedIn

## Purpose
Generate a beautiful, screenshot-ready HTML architecture diagram of what the
student built — designed for posting on LinkedIn. Claude analyzes the student's
code, understands their architecture, and generates a custom 1080x1080 visual
in the AI Analyst Lab brand style.

The student does nothing except type `/show-off-linkedin`, confirm the post,
and hit Post on LinkedIn. Claude handles everything else — renders the image,
drafts the caption, opens LinkedIn, and copies the caption to clipboard.

## When to Use
- User says `/show-off-linkedin` or "LinkedIn showcase" or "share on LinkedIn"
- End of Day 1 or Day 2 when students want to share what they built

## Invocation
`/show-off-linkedin` — generate a LinkedIn-ready architecture diagram

## Instructions

### Step 1: Find the Student's Work

Same detection logic as `/show-off`. Do NOT ask the student to explain anything.

1. **Run `git status --short`** to see untracked (`??`) and modified (`M`) files
2. **Run `git diff`** to see what they changed in existing files
3. **Read the new/modified files** to understand what they actually contain

If the student HAS made commits:
4. **Run `git log --oneline --all --not --remotes`** to find local-only commits
5. Combine committed changes with uncommitted work

**Ignore** `.env`, `.gitignore`, `node_modules/`, lockfiles, `__pycache__/`, etc.

**Understand the architecture** — what components exist, how they connect,
what data flows where. Focus on agents, skills, helpers, analysis outputs,
charts, and pipelines. Count things: how many agents, how many charts, how
many tests, how many lines of code they wrote.

### Step 2: Choose a Layout Pattern

Based on what the student built, choose the best layout:

**Pattern A: Engine + Fan-out** (most common)
Use when: Student built a core analysis system that produces multiple outputs.
Structure: Input question → Engine block → Branch to output columns → File tree
Example: "Asked a question → analysis engine → experiment design + charts + deep dives → organized output"

**Pattern B: Linear Pipeline**
Use when: Student built a sequential multi-step pipeline.
Structure: Numbered steps flowing top to bottom, each with a badge (agent/python).
Example: "Data in → clean → analyze → visualize → report out"

**Pattern C: Component Showcase**
Use when: Student built several independent components (agents, skills, helpers)
that don't form a single pipeline.
Structure: Component count chips at top → individual component boxes with details → stats.
Example: "Built 3 agents + 2 helpers + 1 skill, each doing different things"

Most students will fit Pattern A. When in doubt, use Pattern A.

### Step 3: Generate the HTML

Read the design system reference at `references/design-system.html` in this
skill's directory. This file contains:
- All CSS classes and their visual styling
- A complete working example (Pattern A: engine + fan-out)
- Color variants for each component type

**Generate a complete, self-contained HTML file** using the CSS from the design
system. Copy the full `<style>` block from the reference, then write custom HTML
in the `<div class="content">` section for this specific student's build.

#### Available CSS components

**Layout:**
- `.slide` — 1080x1080 container (always use this)
- `.top-bar`, `.grid-bg`, `.glow`, `.brand` — background effects (always include)
- `.content` — padded flex column for all content
- `.section-divider` — subtle gradient line between sections
- `.flow-arrow` — centered `▼` between sections

**Header (always include):**
- `.eyebrow` — "BUILT WITH AI ANALYST LAB"
- `.title` + `.accent` — main headline with amber accent word
- `.subtitle` — one-line description

**Core blocks:**
- `.input-question` — the prompt/question that started the analysis
- `.engine-block` — the hero component (amber double-border, gradient fill)
  - `.engine-label` — uppercase label
  - `.engine-stack` — horizontal row of tool chains
  - `.engine-item` — individual tool chain (`.tool` for names, `.arrow` for →)

**Fan-out/Fan-in:**
- `.branch` container with `.branch-center-in` + `.branch-lines` + `.branch-drop`
- `.output-row` — flex row of output boxes
- Converge: `.converge-lines` + `.converge-drop` + `.converge-center-out`

**Output boxes** (5 color variants):
- `.output-box.agent` — indigo/purple (for AI agents)
- `.output-box.helper` — emerald/green (for Python helpers)
- `.output-box.output` — amber (for charts, reports, deliverables)
- `.output-box.data` — cyan (for data sources, databases)
- `.output-box.skill` — blue (for skills)
- Inside: `.box-label`, `.box-title`, `.box-items` (with `li` and `li.highlight`), `.box-count`

**File tree box:**
- `.file-tree-box` — shows organized output directory structure
- `.file-tree` with `.dir`, `.file`, `.count`, `.check` spans

**Component chips** (Pattern C):
- `.component-row` — horizontal row
- `.component-chip` with variants `.agent`, `.helper`, `.skill`, `.output`
- Inside: `.chip-count` (big number) + `.chip-label` (small label)

**Numbered steps** (Pattern B):
- `.steps-col` — vertical column
- `.step` with variants `.agent-step`, `.python-step`, `.output-step`
- Inside: `.step-node` (number), `.step-content` (`.step-title` + `.step-desc`), `.step-badge`

**Stats row (always include):**
- `.stats-row` with `.stat-item` containing `.stat-dot` + `.stat-text` (with `.num` spans)

#### Design rules

1. **Always 1080x1080.** This is LinkedIn's square format. The `.slide` class handles this.
2. **Tell a story top-to-bottom.** Input at top, output at bottom. The eye follows the flow.
3. **The engine block is the hero.** If they built a core system, give it the `.engine-block` treatment.
4. **Use color to distinguish component types.** Don't make everything amber — use purple for agents, green for helpers, cyan for data.
5. **Include real details.** Don't just say "charts" — list what charts. Don't just say "agent" — say what it does.
6. **Keep it tight but breathable.** Everything must fit in 1080x1080 without scrolling. But don't cram — whitespace makes it professional.
7. **Count things for the stats row.** Agents, charts, tests, lines of code — concrete numbers make it impressive.

### Step 4: Render to PNG

Save the HTML file to the repo root as `showcase.html`, then render it to
a crisp PNG using the render script:

```bash
node scripts/render-showcase.mjs showcase.html showcase.png
```

This produces a 2160x2160 retina PNG (2x scale of 1080x1080) — perfect for
LinkedIn's image quality. The first run installs puppeteer and downloads
Chromium (~280MB), subsequent runs are instant.

Also copy the PNG to the student's Desktop so they can find it easily:

```bash
cp showcase.png ~/Desktop/showcase.png
```

If the render script fails (missing Node.js, Chromium issues), fall back to
opening the HTML in the browser and telling the student to screenshot manually.

### Step 5: Draft the LinkedIn Caption

Write a short LinkedIn post (3-5 sentences, first person) that:
- Opens with what they built today — specific, not vague
- Mentions it was at the **AI Analyst Lab** bootcamp
- Names concrete details (number of agents, what data they analyzed, what they found)
- Conveys genuine excitement without being cringe
- Ends with a takeaway or reflection
- Does NOT use hashtags, emojis, or "day 1/30" style formatting

**Example captions** (for tone, don't copy):

> Built an AI-powered analysis engine today at the AI Analyst Lab bootcamp.
> It takes a business question, queries real data with DuckDB, runs power
> analysis with scipy, and outputs 18 production-quality charts. The whole
> thing is orchestrated by Claude Code — I wrote the architecture, Claude
> wrote the code. Took about 4 hours.

> Spent the day at AI Analyst Lab building a checkout funnel analyzer.
> Asked it "should we redesign mobile checkout?" and it came back with a
> full experiment design, sample size calculations, and 14 visualizations.
> I'm a PM. I've never written a line of Python. This is wild.

> Just built my first agentic analysis pipeline. Three AI agents that
> coordinate to go from question to insight to report — with actual
> statistical rigor, not just vibes. Built at the AI Analyst Lab bootcamp
> with Claude Code. Already thinking about how to use this at work.

### Step 6: Confirm Before Posting

Show the student:
1. The rendered PNG (open it: `open showcase.png`)
2. The LinkedIn caption

Ask: **"Here's your LinkedIn showcase and caption. Want me to open LinkedIn
so you can post it, or change anything first?"**

Do NOT proceed until they confirm.

### Step 7: Open LinkedIn with Caption Pre-filled + Image on Clipboard

Two things happen simultaneously:

1. **Caption goes in the URL** — LinkedIn's `shareActive` parameter pre-fills the compose box
2. **Image goes on the clipboard** — macOS `osascript` copies the PNG so the student can Cmd+V

```bash
python3 -c "
import urllib.parse, subprocess, webbrowser, os

caption = '''CAPTION_TEXT_HERE'''

# Copy the PNG to clipboard (macOS)
png_path = os.path.abspath('showcase.png')
subprocess.run(['osascript', '-e', 'set the clipboard to (read (POSIX file \"' + png_path + '\") as «class PNGf»)'])

# Open LinkedIn with caption pre-filled
url = 'https://www.linkedin.com/feed/?shareActive=true&text=' + urllib.parse.quote(caption)
webbrowser.open(url)
"
```

LinkedIn opens with the compose box active and the caption already typed in.
The showcase PNG is on the clipboard ready to paste.

Then tell the student:

**"LinkedIn is open with your caption already filled in and your image
copied to your clipboard. Just hit Cmd+V to paste the image, then Post!"**

One paste, one click.

**Fallback:** If pasting the image doesn't work in LinkedIn's composer (some
browsers handle clipboard images differently), tell the student to click the
image icon in the composer and select `showcase.png` from their project folder.

### Step 8: Clean up

After they've posted (or decided not to), the `showcase.html` and
`showcase.png` files can be deleted — they're not part of the project:

```bash
rm -f showcase.html showcase.png
```

Don't auto-delete — ask first or just mention they can clean up.

## Rules
1. The student should NOT have to explain what they built — Claude figures it out
2. Every showcase must be exactly 1080x1080 pixels
3. Copy the FULL CSS from the design system reference — don't write custom CSS
4. Only customize the HTML structure inside `.content`
5. Always include: header, main architecture section, stats row, brand watermark
6. Use real data from the student's code — never make up file names or counts
7. The visual should look like a product launch page, not a homework assignment
