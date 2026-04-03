# Skill: Experiment Brief

## Purpose
Auto-generate a structured experiment brief when a user expresses intent to test something. This is the "think before you design" safety net — ensuring every experiment starts with a clear hypothesis, north star metric, guardrail metrics, success criteria, and duration estimate before the Experiment Designer agent runs.

## When to Use
Apply this skill when:
1. **The user says "I want to test..."** or "Let's experiment with..." or "Should we A/B test..." or any variant expressing intent to run an experiment
2. **Before invoking the Experiment Designer agent** — the brief is a prerequisite input
3. **When an experiment request is vague** — the user wants to test something but hasn't specified metrics, duration, or success criteria

This skill auto-fires on experiment intent detection. Do NOT wait to be asked.

## Instructions

### What Is an Experiment Brief?

An **experiment brief** is a one-page document that captures the essential decisions BEFORE any statistical design work begins. It answers: What are we testing? Why? How will we know if it worked? What must we not break?

```
EXPERIMENT BRIEF
━━━━━━━━━━━━━━━━
WHAT:       What change are we testing?
WHY:        What business outcome do we expect?
HYPOTHESIS: We believe [change] will [impact metric] because [reason]
NORTH STAR: The ONE metric we're trying to move
GUARDRAILS: Metrics that must NOT degrade
SUCCESS:    What result would make us ship?
DURATION:   Rough estimate of how long we'd need to run
```

**The rule:** Never jump to power analysis or test design without a brief. A well-designed experiment that tests the wrong thing is worse than no experiment at all.

### Briefing Process

#### Step 1: Extract the hypothesis

If the user provides a vague intent ("I want to test regional playlists"), structure it into a proper hypothesis:

> "We believe that **[specific change]** will **[increase/decrease] [specific metric]** because **[mechanism/reason]**."

**Rules for a good hypothesis:**
- Must be falsifiable — the experiment must be able to disprove it
- Must specify a direction — "improve" is not enough; state whether you expect an increase or decrease
- Must include a mechanism — the "because" clause. If you can't articulate WHY the change should work, you don't understand it well enough to test it
- Must be specific enough to measure — "improve user experience" is not measurable; "increase 7-day retention by reducing onboarding steps" is

If the user's intent is too vague to form a hypothesis, ask:
- "What specific behavior do you expect to change?"
- "Why do you think this change will have that effect?"
- "How would you know if it worked?"

#### Step 2: Define the north star metric

Select exactly ONE primary metric using the Metric Spec skill (`.claude/skills/metric-spec/skill.md`):

- The metric the hypothesis predicts will change
- Must be fully specified: numerator, denominator, time window
- Must be measurable with available data
- Only one. If the user wants to optimize for multiple metrics, force a choice: "Which one matters most? The others become secondary or guardrails."

#### Step 3: Define guardrail metrics

Apply the Guardrails Awareness skill (`.claude/skills/guardrails/skill.md`):

- At least one guardrail per experiment
- The guardrail must measure a different dimension of value than the north star
- Common pairs: engagement ↔ churn, conversion ↔ quality, speed ↔ accuracy
- Define an acceptable threshold: "Churn must not increase by more than 0.5 percentage points"

#### Step 4: Define success criteria

Pre-register what "success" looks like BEFORE seeing results:

```
SUCCESS CRITERIA
━━━━━━━━━━━━━━━━
Ship if:     [north star improves by ≥X% AND guardrails are clean]
Kill if:     [north star shows no effect OR guardrails degrade significantly]
Iterate if:  [mixed results — e.g., works for some segments but not others]
```

This prevents post-hoc rationalization. The team decides what they'll do with each outcome before the data arrives.

#### Step 5: Estimate duration and feasibility

Provide a rough estimate (not a formal power analysis — that's the Experiment Designer's job):

- **Traffic:** How many users/day enter the affected flow?
- **Baseline:** What's the current value of the north star metric?
- **MDE:** What's the smallest change worth detecting? (Default: 5% relative for conversion, 10% for revenue)
- **Rough duration:** Based on traffic and MDE, is this a 1-week, 4-week, or 3-month experiment?
- **Feasibility flag:** VIABLE (< 4 weeks), LONG (4-8 weeks), IMPRACTICAL (> 8 weeks — consider alternatives)

### Output Format

```markdown
# Experiment Brief: [Descriptive Name]

## Hypothesis
We believe that **[change]** will **[increase/decrease] [metric]** because **[reason]**.

## North Star Metric
| Metric | Definition | Current Baseline | Target Lift |
|--------|-----------|-----------------|-------------|
| [name] | [numerator / denominator, time window] | [current value] | [≥X% relative] |

## Guardrail Metrics
| Metric | Definition | Current Value | Acceptable Threshold |
|--------|-----------|---------------|---------------------|
| [name] | [definition] | [current] | [must not degrade by >X%] |

## Success Criteria
- **Ship if:** [conditions]
- **Kill if:** [conditions]
- **Iterate if:** [conditions]

## Feasibility Estimate
| Parameter | Estimate |
|-----------|---------|
| Daily traffic | [N users/day] |
| Baseline metric value | [X%] |
| Minimum detectable effect | [Y% relative] |
| Rough duration | [Z weeks] |
| Feasibility | [VIABLE / LONG / IMPRACTICAL] |

## Next Step
→ Pass this brief to the **Experiment Designer agent** for formal power analysis and test design.
```

## Handoff

After generating the brief, the next step is ALWAYS the Experiment Designer agent (`agents/experiment-designer.md`). Pass the hypothesis, metric definitions, and feasibility estimate as inputs.

## Anti-Patterns

1. **Never skip the hypothesis** — "Let's just test it and see what happens" is not an experiment; it's hoping
2. **Never allow multiple north star metrics** — one primary metric. Everything else is secondary or a guardrail
3. **Never omit guardrails** — every optimization creates a trade-off. Name it upfront
4. **Never skip success criteria** — deciding what to do with results AFTER seeing them invites bias
5. **Never let "we'll figure it out" be a success criterion** — pre-register specific thresholds

## Skills Used
- `.claude/skills/metric-spec/skill.md` — for fully specifying the north star metric
- `.claude/skills/guardrails/skill.md` — for selecting and defining guardrail metrics
