# Skill: Deck Rescue

## Purpose
Take a bad deck end-to-end and produce a complete rewrite: new narrative arc, new action headlines, decluttered evidence, and clear asks. Outputs a new Marp deck plus a before/after comparison document.

## When to Use
Apply this skill when:
1. **A deck scores D or F on `/deck-critique`** — needs a complete rewrite, not slide-level fixes
2. **The user asks to "rescue", "rewrite", or "redo" an entire deck** from scratch
3. **The presentation-doctor agent prescribes a full rescue** based on diagnosis severity

This skill can be invoked directly as `/deck-rescue` or called by the presentation-doctor orchestrator agent.

## Inputs
- **`{{DECK_SOURCE}}`**: Path to original Marp `.marp.md` file OR Google Slides presentation ID/URL
- **`{{AUDIENCE}}`**: Who the presentation is for (required for rescue — cannot rewrite without knowing the audience)
- **`{{CONTEXT}}`** (optional): What decision or meeting this deck supports
- **`{{CRITIQUE}}`** (optional): Path to the deck critique from `/deck-critique` — saves re-diagnosis time
- **`{{STORY}}`** (optional): Path to story extraction from the story-extractor agent — if provided, skips Step 2
- **`{{THEME}}`** (optional): Marp theme to apply — defaults to `analytics-dark`

## Instructions

### Rescue Pipeline

The full rescue is a 7-step pipeline. If `{{CRITIQUE}}` or `{{STORY}}` are provided, the corresponding steps are shortened or skipped.

#### Step 1: Diagnose (or load critique)

**If `{{CRITIQUE}}` is provided:** Read the critique file and extract the per-slide scores, anti-patterns, and prescription. Skip to Step 2.

**If not:** Run the `/deck-critique` skill on `{{DECK_SOURCE}}`. Save to `working/deck_critique_{{DATE}}.md`.

Confirm the grade is D or F. If the grade is B or C, suggest `/slide-transform` instead — a full rescue may be overkill.

#### Step 2: Extract raw content

Parse every slide using `helpers/deck_parser.py` and extract ALL data, findings, and claims from the original deck — separate signal from noise:

**Signal (keep):**
- Specific numbers, percentages, rates
- Named segments, cohorts, time periods
- Charts with data (note what the chart shows, not just that a chart exists)
- Any finding, even if poorly stated

**Noise (discard):**
- Generic filler ("as you can see", "in summary")
- Redundant data points (same finding stated 3 ways)
- Decorative elements that add no information
- Appendix data that wasn't referenced in the main deck

Save the extracted content inventory to `working/content_inventory_{{DATE}}.md`.

#### Step 3: Find the story (or load story extraction)

**If `{{STORY}}` is provided:** Read the story extraction and use the #1 story as the narrative spine. Skip to Step 4.

**If not:** Run the story-extractor agent (`agents/story-extractor.md`) on the content inventory. The agent identifies the 1-3 stories worth telling and the #1 story to lead with.

The #1 story becomes the narrative spine for the new deck.

#### Step 4: Build the narrative arc

Using the extracted story, build a new narrative following **Context → Tension → Resolution**:

```
NARRATIVE ARC
━━━━━━━━━━━━
CONTEXT:    What's the baseline? What does the audience already know?
TENSION:    What changed? What's the surprising finding? What's at risk?
RESOLUTION: What should we do? What's the ask? What's the expected impact?
```

Map the narrative arc to slides:

| Slide | Role | Checklist Target |
|-------|------|-----------------|
| Slide 1 | **Title + SO-WHAT** — The main finding IS the title | SO-WHAT: 3/3 |
| Slide 2 | **STAKES** — Why should the audience care? Quantify the impact | STAKES: 3/3 |
| Slide 3 | **EVIDENCE (pattern)** — The key evidence supporting the finding | EVIDENCE: 3/3 |
| Slide 4 | **EVIDENCE (cause)** — Root cause or deeper explanation | EVIDENCE: 3/3 |
| Slide 5 | **RESOLUTION** — Recommendation with expected impact | ASK: 3/3 |
| Slide 6 | **ASK** — Specific decision request with timeline and risk | ASK: 3/3 |

This is the default 6-slide structure. Adjust based on content:
- **Simple story (1 evidence point):** 4-5 slides
- **Complex story (multiple evidence threads):** 6-8 slides
- **Never exceed 8 slides** for a rescue — the original was already too long

#### Step 5: Generate the new deck

Write each slide as Marp markdown following these rules:

**Title rules:**
- Every slide title is an action headline (SO-WHAT score ≥ 2)
- Read all titles top-to-bottom — they must tell the complete story
- No label titles ("Overview", "Analysis", "Results")

**Evidence rules:**
- Maximum 3 bullet points per slide
- Maximum 1 chart per slide
- Bold key numbers: `**67%**`, `**$2.3M ARR**`
- If data was in the original deck, reference it specifically

**Ask rules:**
- Final slide must have a specific ask with: action, owner (if known), timeline, risk mitigation
- "Questions?" is never the final slide — it can follow the ask slide

**Marp formatting:**
- Use the `{{THEME}}` theme (default: `analytics-dark`)
- Apply appropriate slide classes from the theme
- Use `<!-- _class: lead -->` for the title slide
- Use `<!-- _class: impact -->` for single-statement emphasis slides
- Reference charts as `![](outputs/charts/...)` — describe what chart should be created but do NOT generate charts (Chart Maker handles that)

Save the new deck to `working/deck_rescue_{{DATE}}.marp.md`.

#### Step 6: Build the before/after comparison

For each original slide, show what replaced it and why:

```markdown
## Before/After Comparison

### Original Slide 1 → New Slide 1
**Before:** "Q3 Churn Analysis" (label title, no finding)
**After:** "Incomplete Onboarding Drives 67% of Enterprise Churn" (action headline)
**Why:** The original title told the audience nothing. The new title IS the finding.
**Score change:** 2/12 → 11/12

[Repeat for each slide mapping]
```

Note: Not every original slide maps 1:1 to a new slide. Some original slides are merged, some are cut entirely. Document this.

Save to `working/before_after_{{DATE}}.md`.

#### Step 7: Generate speaker notes

For each new slide, write brief speaker notes covering:
- **The talking track** — what to say when this slide is on screen (2-3 sentences)
- **The transition** — how to bridge to the next slide
- **Anticipated question** — one question the audience might ask, with a prepared answer

Add speaker notes as Marp comments below each slide:

```markdown
<!--
TALKING TRACK: [what to say]
TRANSITION: [bridge to next slide]
ANTICIPATED Q: [question] → [answer]
-->
```

### Output Format

The rescue produces 3 files:

1. **`working/deck_rescue_{{DATE}}.marp.md`** — The complete new Marp deck
2. **`working/before_after_{{DATE}}.md`** — Slide-by-slide comparison with score changes
3. **`working/content_inventory_{{DATE}}.md`** — Raw content extraction (signal vs noise)

Plus a summary printed to the user:

```markdown
# Deck Rescue Complete

**Original:** [N] slides, grade [X], avg score [Y/12]
**Rescued:** [M] slides, projected grade [A/B], avg score [Z/12]

## Story
[1-sentence summary of the narrative spine]

## Slide Map
| New Slide | Title | From Original | Score |
|-----------|-------|--------------|-------|
| 1 | "[action headline]" | Slides 1,4 (merged) | 11/12 |
| 2 | "[action headline]" | Slide 2 (rewritten) | 10/12 |
| ... | ... | ... | ... |

## Files Created
- New deck: `working/deck_rescue_{{DATE}}.marp.md`
- Comparison: `working/before_after_{{DATE}}.md`
- Content inventory: `working/content_inventory_{{DATE}}.md`

## Next Steps
1. Review the new deck and comparison doc
2. Run `/deck-critique` on the rescue to verify all slides score 9+/12
3. Run Chart Maker for any chart placeholders
4. Render with Marp: `npx @marp-team/marp-cli working/deck_rescue_{{DATE}}.marp.md --pdf --theme-set shared/themes/{{THEME}}.css`
```

## Handoff

After the rescue:
- **Verify quality:** Run `/deck-critique` on the new deck to confirm all slides score 9+/12
- **Generate charts:** If the new deck references chart placeholders, invoke Chart Maker for each
- **Render:** Use Marp CLI to produce the PDF
- The presentation-doctor orchestrator handles all of this automatically

## Anti-Patterns

1. **Never rescue a B/C deck** — suggest `/slide-transform` instead. A rescue means starting over.
2. **Never keep the original structure** — the whole point is a new narrative arc. If the original order was right, it wouldn't need rescuing.
3. **Never add new data** — rescue uses ONLY what was in the original deck. The story was there; it was just buried.
4. **Never exceed 8 slides** — if you need more, the story isn't focused enough
5. **Never end without an ask** — the final slide must request a specific decision or action

## Skills Used
- `.claude/skills/deck-critique/skill.md` — for initial diagnosis (Step 1)
- `.claude/skills/presentation-themes/skill.md` — for Marp theme application
- `agents/story-extractor.md` — for finding the buried story (Step 3)
- `helpers/deck_parser.py` — for parsing the original deck
