# Skill: Slide Transform

## Purpose
Take one bad slide and produce 2-3 redesigned variants, each with an explanation of what changed and why. Each variant optimizes for a different dimension of the Data Story Checklist.

## When to Use
Apply this skill when:
1. **The user asks to fix, improve, or redesign a specific slide** — "fix slide 3", "make this slide better", "transform this slide"
2. **After `/deck-critique` identifies slides scoring below 6/12** — target the worst offenders
3. **The user wants to see multiple approaches** to presenting the same content

This skill can be invoked directly as `/slide-transform` or called by the presentation-doctor orchestrator agent.

## Inputs
- **`{{SLIDE_CONTENT}}`**: The original slide content — either raw text, Marp markdown for one slide, or a slide object from `deck_parser.py`
- **`{{OPTIMIZE_FOR}}`** (optional): Which checklist dimension to prioritize — `SO-WHAT`, `STAKES`, `EVIDENCE`, `ASK`, or `all` (default: `all`)
- **`{{AUDIENCE}}`** (optional): Who the presentation is for
- **`{{CONTEXT}}`** (optional): What decision or meeting this slide supports
- **`{{CRITIQUE}}`** (optional): The per-slide scorecard from `/deck-critique` — if provided, uses the specific scores to guide the transformation

## Instructions

### Transformation Process

#### Step 1: Diagnose the original slide

If `{{CRITIQUE}}` is provided, use those scores. Otherwise, quickly score the slide on all 4 checklist dimensions (SO-WHAT, STAKES, EVIDENCE, ASK) using the scoring rubric from `/deck-critique`.

Identify the **primary problem** — the lowest-scoring dimension. If tied, prioritize: SO-WHAT > ASK > EVIDENCE > STAKES (this order reflects the most common failure modes).

Extract the raw content:
- What data/findings are present?
- What claims are being made (explicitly or implicitly)?
- What's the buried insight (if any)?

#### Step 2: Generate Variant A — Headline Fix

**Goal:** Rewrite the title as an action headline. Keep the body content mostly intact.

**Process:**
1. Identify the most important finding on the slide (even if buried in bullets)
2. Write it as a specific, data-driven headline: "[Subject] [verb] [quantified finding]"
3. Keep the body content similar but reorder to support the new headline
4. Add a subtitle with context (data source, time range, segment)

**Template:**
```markdown
### Variant A: Headline Fix

**Strategy:** Transform the label title into an action headline that states the finding.

**Original title:** "[old title]"
**New title:** "[action headline with specific data]"

---

[Full Marp markdown for the redesigned slide]

---

**What changed:**
- Title rewritten from [label/descriptive] to action headline
- Body reordered to support the headline claim
- [Any other minor changes]

**Checklist improvement:**
- SO-WHAT: [old score] → [new score]
- [Other dimensions if changed]
```

#### Step 3: Generate Variant B — Declutter

**Goal:** Strip to 2-3 key data points. Remove noise. Maximize white space.

**Process:**
1. List every data point on the original slide
2. Rank by relevance to the slide's claim (or the best possible claim)
3. Keep the top 2-3 data points. Move the rest to an "appendix" note
4. Replace bullet walls with focused visual elements
5. If there are multiple charts, pick the ONE that best supports the claim

**Template:**
```markdown
### Variant B: Declutter

**Strategy:** Strip to 2-3 key evidence points. Cut everything that doesn't directly support the headline.

**Cut list:** [items removed and why]
**Kept:** [items retained and why]

---

[Full Marp markdown for the redesigned slide]

---

**What changed:**
- Reduced from [N] bullets/data points to [M]
- [Specific items cut and why]
- Added white space / simplified layout

**Checklist improvement:**
- EVIDENCE: [old score] → [new score]
- [Other dimensions if changed]
```

#### Step 4: Generate Variant C — Story Reframe

**Goal:** Restructure around stakes + ask. May split into 2 slides if the content warrants it.

**Process:**
1. Identify the audience and what decision this slide should inform
2. Reframe the content around: "Why should [audience] care about this?"
3. Add explicit stakes (quantified impact if possible)
4. Add a clear ask or next step
5. If the slide has too much for one frame, split into:
   - Slide 1: The finding + stakes
   - Slide 2: The evidence + ask

**Template:**
```markdown
### Variant C: Story Reframe

**Strategy:** Restructure around stakes and ask. Frame for [audience] making [decision].

**Reframe logic:** [Why this structure better serves the audience]

---

[Full Marp markdown for the redesigned slide(s)]

---

**What changed:**
- Added explicit stakes: [what was added]
- Added clear ask: [what was added]
- [Split into 2 slides if applicable]

**Checklist improvement:**
- STAKES: [old score] → [new score]
- ASK: [old score] → [new score]
- [Other dimensions if changed]
```

#### Step 5: Summary comparison

```markdown
## Comparison

| Dimension | Original | Variant A | Variant B | Variant C |
|-----------|----------|-----------|-----------|-----------|
| SO-WHAT | X/3 | X/3 | X/3 | X/3 |
| STAKES | X/3 | X/3 | X/3 | X/3 |
| EVIDENCE | X/3 | X/3 | X/3 | X/3 |
| ASK | X/3 | X/3 | X/3 | X/3 |
| **Total** | **X/12** | **X/12** | **X/12** | **X/12** |

**Recommended variant:** [A/B/C] — [1-sentence rationale based on audience and context]
```

### Output Format

Save to `working/slide_transform_{{DATE}}.md`:

```markdown
# Slide Transform: [Original Slide Title]

**Date:** {{DATE}}
**Original score:** [X/12]
**Primary problem:** [lowest-scoring dimension]
**Audience:** [if provided]

## Original Slide
[Original Marp markdown or text content]

## Variant A: Headline Fix
[As templated above]

## Variant B: Declutter
[As templated above]

## Variant C: Story Reframe
[As templated above]

## Comparison
[Summary table]
```

### Marp Formatting Rules

All variant slides must be valid Marp markdown:
- Use `---` as slide separators
- Use `<!-- _class: ... -->` for slide classes from the active theme
- Charts referenced as `![](path/to/chart.png)` — note that chart generation is NOT part of this skill; reference existing charts or describe placeholder charts
- Keep bullet lists to 3 items max
- Use bold for key numbers: `**67%**`, `**$2.3M**`

## Handoff

After generating variants:
- The user (or presentation-doctor agent) selects a variant
- If part of a `/deck-rescue` pipeline, the selected variant replaces the original slide in the new deck

## Anti-Patterns

1. **Never generate more than 3 variants** — choice overload defeats the purpose
2. **Never change the underlying data** — transform the presentation, not the findings
3. **Never ignore the original content** — every variant must use the same data/findings, just structured differently
4. **Never produce variants that all look the same** — each must take a meaningfully different approach
