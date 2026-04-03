# Skill: Deck Critique

## Purpose
Score any presentation slide-by-slide against the **Data Story Checklist** (SO-WHAT, STAKES, EVIDENCE, ASK). Returns a diagnosis report with per-slide scorecards, anti-pattern flags, an overall grade, and a prioritized prescription for fixes.

## When to Use
Apply this skill when:
1. **The user asks to review, critique, or diagnose a deck** — "review my deck", "what's wrong with these slides", "critique this presentation"
2. **Before running `/deck-rescue`** — the critique is a prerequisite input for the full rescue pipeline
3. **The user provides a Marp `.marp.md` file or a Google Slides URL/ID** for evaluation

This skill can be invoked directly as `/deck-critique` or auto-fires when the presentation-doctor orchestrator agent runs.

## Inputs
- **`{{DECK_SOURCE}}`**: Path to a Marp `.marp.md` file OR a Google Slides presentation ID/URL
- **`{{AUDIENCE}}`** (optional): Who the presentation is for — informs STAKES scoring
- **`{{CONTEXT}}`** (optional): What decision or meeting this deck supports

## Instructions

### The Data Story Checklist Scoring System

Every slide is scored on 4 dimensions, each 0-3 points (max 12 per slide):

#### SO-WHAT (0-3): Does the title state a finding?
| Score | Criteria | Example |
|-------|----------|---------|
| 3 | **Action headline** — states a specific finding with data | "Incomplete onboarding drives 67% of enterprise churn" |
| 2 | **Descriptive headline** — describes what's shown but not what it means | "Churn by onboarding status" |
| 1 | **Label** — generic category name | "Churn Analysis" |
| 0 | **Missing or generic** — no title, or "Q3 Results" | "Q3 Update" |

#### STAKES (0-3): Does the audience know why this matters?
| Score | Criteria | Example |
|-------|----------|---------|
| 3 | **Explicit impact** — quantified business consequence | "$2.3M ARR at risk, growing 15% QoQ" |
| 2 | **Implied impact** — consequence is suggested but not quantified | "This is our fastest-growing churn segment" |
| 1 | **Generic** — vague importance claim | "This is important for the business" |
| 0 | **None** — no reason given for audience to care | (just data, no framing) |

#### EVIDENCE (0-3): Is the evidence focused?
| Score | Criteria | Example |
|-------|----------|---------|
| 3 | **Focused** — 2-3 key data points supporting the claim | Two charts: survival curve + revenue waterfall |
| 2 | **Moderate** — 4-6 data points, slightly broad | Table with 6 rows of relevant data |
| 1 | **Data dump** — 7+ points, multiple charts, unfocused | Wall of 12 bullets, 3 charts crammed together |
| 0 | **No evidence** — claims without supporting data | "We believe churn is a problem" |

#### ASK (0-3): Is there a clear action or decision?
| Score | Criteria | Example |
|-------|----------|---------|
| 3 | **Specific ask** — named action, owner, timeline | "Approve 2 engineers for 6 weeks to rebuild onboarding" |
| 2 | **Vague recommendation** — directional but not actionable | "We should invest in onboarding" |
| 1 | **Implied** — action is suggested indirectly | "Onboarding seems like a priority area" |
| 0 | **None** — no ask, no recommendation, no next step | "Questions?" |

### Diagnosis Process

#### Step 1: Parse the deck

**For Marp files:**
Use `helpers/deck_parser.py` → `parse_marp(path)` to split the deck into slide objects. Each slide object contains: index, title, body_text, bullets, bullet_count, has_chart, has_data_table, word_count, slide_class.

**For Google Slides:**
Use `helpers/deck_parser.py` → `parse_google_slides(presentation_id)` with the Google Workspace MCP to extract slide content.

#### Step 2: Score each slide

For every slide, assign scores on all 4 dimensions. Write the reasoning for each score — not just the number.

```
Slide N: "[title]"
  SO-WHAT:  [0-3] — [reasoning]
  STAKES:   [0-3] — [reasoning]
  EVIDENCE: [0-3] — [reasoning]
  ASK:      [0-3] — [reasoning]
  Total:    [X/12]
  Anti-patterns: [list any detected]
```

#### Step 3: Flag anti-patterns

Check each slide and the deck overall for these common anti-patterns:

| Anti-Pattern | Detection | Severity |
|-------------|-----------|----------|
| **Wall of bullets** | bullet_count > 6 on a single slide | High |
| **Chart-as-title** | Title is a chart type name ("Pie Chart", "Bar Graph") | High |
| **Orphan data** | Data presented with no interpretation or context | Medium |
| **No narrative arc** | Slides are unconnected; could be reordered without impact | High |
| **Missing transitions** | No logical flow from one slide to the next | Medium |
| **Data dump** | 3+ charts or tables on a single slide | High |
| **Label titles** | All slide titles are category labels, not findings | High |
| **Pie charts** | Any pie chart present (banned per SWD principles) | Medium |
| **No ask** | Final slide has no recommendation or decision request | High |
| **"Questions?" closer** | Deck ends with a "Questions?" slide instead of a clear ask | High |
| **Appendix bloat** | More than 3 appendix slides (suggests content wasn't curated) | Low |

#### Step 4: Calculate overall grade

**Deck Score** = average of all slide scores (out of 12)

| Grade | Avg Score | Diagnosis |
|-------|-----------|-----------|
| A | 10-12 | Excellent — clear story, focused evidence, specific ask |
| B | 8-9.9 | Good — minor improvements needed (tighten headlines or evidence) |
| C | 6-7.9 | Mediocre — story exists but is buried; needs restructuring |
| D | 4-5.9 | Poor — data dump with no clear story or ask |
| F | 0-3.9 | Failing — no story, no stakes, no ask; needs complete rewrite |

#### Step 5: Generate the prescription

Produce a prioritized list of fixes, ordered by impact:

1. **Critical fixes** (would change the grade) — e.g., "Rewrite all titles as action headlines"
2. **High-impact fixes** (improve audience comprehension) — e.g., "Add a clear ask to the final slide"
3. **Polish fixes** (improve professionalism) — e.g., "Replace pie charts with horizontal bars"

### Output Format

Save to `working/deck_critique_{{DATE}}.md`:

```markdown
# Deck Critique: [Deck Title or Filename]

**Date:** {{DATE}}
**Source:** [file path or Slides ID]
**Audience:** [if provided]
**Context:** [if provided]

## Overall Grade: [A-F]

**Diagnosis:** [1-sentence summary — e.g., "This deck has data but no story. 6 of 8 slides fail the SO-WHAT check."]

**Deck Score:** [X.X/12 average]

## Per-Slide Scorecard

### Slide 1: "[title]"
| Check | Score | Reasoning |
|-------|-------|-----------|
| SO-WHAT | X/3 | [why] |
| STAKES | X/3 | [why] |
| EVIDENCE | X/3 | [why] |
| ASK | X/3 | [why] |
| **Total** | **X/12** | |

**Anti-patterns:** [list or "None"]

[Repeat for each slide]

## Anti-Pattern Summary

| Anti-Pattern | Slides Affected | Severity |
|-------------|----------------|----------|
| [pattern] | [slide numbers] | [High/Medium/Low] |

## Prescription (Prioritized Fixes)

### Critical
1. [fix description — what to change and why]

### High-Impact
1. [fix description]

### Polish
1. [fix description]

## Recommendation
- **Grade B-C:** Run `/slide-transform` on the [N] worst-scoring slides
- **Grade D-F:** Run `/deck-rescue` for a complete rewrite
```

## Handoff

After generating the critique:
- **Grade B-C:** Suggest `/slide-transform` on the lowest-scoring slides
- **Grade D-F:** Suggest `/deck-rescue` for a full rewrite
- The presentation-doctor orchestrator agent handles this routing automatically

## Anti-Patterns (for this skill)

1. **Never score without reasoning** — every score needs a "why"
2. **Never inflate grades** — a deck with label titles and no ask is not a B
3. **Never critique visual design here** — this skill evaluates story structure, not fonts or colors. The Visual Design Critic agent handles aesthetics.
4. **Never skip the prescription** — the critique is only useful if it comes with actionable fixes

## Skills Used
- `helpers/deck_parser.py` — for parsing deck formats into slide objects
- `.claude/skills/stakeholder-communication/skill.md` — for evaluating audience-appropriateness of stakes and asks
