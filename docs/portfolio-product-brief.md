# AI Analyst Plus Product Brief

## One-line summary

AI Analyst Plus is a Codex-enabled product analytics workspace that turns natural-language business questions into validated analysis, charts, narratives, and stakeholder-ready decks.

## Portfolio framing

This project began as a Claude Code-powered analytics system. My contribution was the migration from Claude Code conventions to Codex-compatible operating conventions, preserving the product's analytical workflow while adapting its instructions, skills, and runtime configuration for Codex.

## Problem

Product teams often need fast answers to questions like "Why did conversion drop?" or "Which customer segment is driving retention?" The work usually requires several handoffs: define the question, inspect data quality, write SQL, validate joins and metrics, create charts, explain the findings, and package the results for stakeholders.

That workflow creates three recurring problems:

- **Slow cycle time:** Analysts spend significant time on setup, query boilerplate, formatting, and presentation assembly before they can get to the actual insight.
- **Inconsistent analytical quality:** Without reusable validation steps, agents and humans can skip sanity checks, reuse flawed query patterns, or present fragile numbers as conclusions.
- **Poor handoff from analysis to decision:** Outputs often stop at numbers or charts instead of explaining what changed, why it matters, what action to take, and how to follow up.

The migration added a fourth product problem: the existing system was written around Claude Code-specific assumptions, paths, and runtime behavior. To make it usable in Codex, the operating layer needed to be translated without breaking the analytical product.

## Solution

AI Analyst Plus packages a product analyst's workflow into a Codex-operable system:

- **Skills** define always-on standards such as question framing, data quality checks, chart style, SQL validation, stakeholder communication, and close-the-loop follow-up.
- **Agents** define repeatable analytical workflows such as data exploration, descriptive analysis, root cause investigation, chart making, storytelling, and deck creation.
- **Helpers** provide deterministic Python utilities for data access, SQL validation, chart styling, query logging, provenance, experiments, and causal analysis.
- **Persistent knowledge** stores dataset context, schema docs, quirks, corrections, proven SQL patterns, and archived analyses.

The Codex migration keeps that product model intact while adapting the system to Codex's repo conventions through `AGENTS.md`, `.agents/skills/`, and `.codex/` runtime configuration.

## Target users

- **Product managers** who need decision-ready insight without waiting for a full analytics queue.
- **Product analysts and data scientists** who want an agentic assistant that follows analysis standards, logs provenance, and produces reusable outputs.
- **Startup and growth teams** that need lightweight investigation workflows for funnels, retention, activation, experiments, and root cause analysis.
- **Analytics educators or demo builders** who need guided, visible analytical workflows rather than opaque one-shot answers.

## Product decisions

### Preserve the existing mental model

The migration kept the core abstraction of skills, agents, helpers, and knowledge instead of redesigning the product around Codex. This reduced migration risk because the analytical workflow remained understandable to existing users.

### Separate agent behavior from deterministic code

Prompt-driven agents handle judgment-heavy tasks such as framing, storytelling, and stakeholder communication. Python helpers handle repeatable operations such as SQL checks, chart rendering, query logging, source detection, experiment statistics, and provenance assembly.

### Make validation part of the workflow, not an optional add-on

The product is structured around quality gates: data quality checks before analysis, cross-verification after findings, validation before presentation, and provenance logs for reported numbers. This product decision turns "trust the agent" into "inspect the trail."

### Migrate the operating layer before changing the product layer

Because my role was the Claude-to-Codex migration, I prioritized compatibility: moving instructions from Claude-oriented files into Codex-oriented conventions, preserving skill coverage, and adding Codex runtime hooks. I avoided broad product redesign that would make it unclear whether issues came from the migration or from new behavior.

### Keep portfolio claims scoped to contribution

The product brief intentionally distinguishes the full product capability from my migration contribution. I did not build the original analytical system from scratch; I adapted the product so Codex could operate it.

## Architecture

```text
User question
  |
  v
Codex operating instructions
  - AGENTS.md
  - .agents/skills/
  - .codex/config.toml
  - .codex/hooks.json
  |
  v
Analytical workflow
  - skills select standards and guardrails
  - agents execute multi-step workflows
  - helpers run deterministic Python logic
  |
  v
Data and memory layer
  - warehouse or local data source
  - .knowledge/ dataset context
  - query logs and provenance records
  |
  v
Outputs
  - analysis reports
  - charts
  - narratives
  - Marp decks
  - Google Docs / Slides exports
```

Key architectural components:

- `AGENTS.md`: Codex-facing operating manual for persona, workflow, rules, development commands, and repository conventions.
- `.agents/skills/`: Codex-accessible skill library migrated from the Claude skill structure.
- `agents/`: Markdown agent templates for pipeline stages such as question framing, data exploration, descriptive analytics, cross-verification, chart generation, storytelling, and deck creation.
- `helpers/`: Python modules for data access, chart styling, SQL dialect handling, validation, experiment statistics, provenance, and exports.
- `.knowledge/`: Persistent analytical context including active dataset, schema, quirks, corrections, query archaeology, and archived work.
- `.codex/`: Runtime configuration and hooks for Codex-specific integration, including MCP configuration and automatic action/query logging.

## Design system

The product design system is optimized for analytical clarity rather than marketing polish.

- **Chart style:** Storytelling with Data-inspired charts with decluttered axes, direct labeling, action titles, and explicit highlighting.
- **Primary palette:** Blue for focus, green for positive movement, red for alerts or negative movement, gray for context, and warm off-white chart backgrounds.
- **Typography:** Helvetica Neue / Helvetica / Arial for readable presentation output; SF Mono / Menlo / Consolas for code and SQL.
- **Presentation themes:** Light analytics theme for business readouts and dark analytics theme for workshops or talks.
- **Reusable helpers:** Chart helpers such as `swd_style()`, `highlight_bar()`, `highlight_line()`, and `action_title()` keep visuals consistent across outputs.
- **Design principle:** Every visual should answer "what changed, why does it matter, and what should we do next?"

## Current capabilities

- Natural-language product analytics questions.
- Quick answers for simple factual or comparison questions.
- Full analysis pipeline from question framing to stakeholder deck.
- Data source support for CSV, DuckDB, Postgres, BigQuery, and Snowflake-oriented workflows.
- Dataset memory through manifests, schema docs, quirks, corrections, and query archaeology.
- SQL validation, dialect handling, query logging, and provenance assembly.
- Data quality checks, structural validation, logical validation, business rules, Simpson's paradox checks, and confidence scoring.
- Funnel, segmentation, trend, root cause, experiment, causal, forecast, and North Star metric workflows.
- Chart generation using a consistent analytics design system.
- Narrative and deck generation with Marp, plus Google Docs and Google Slides export paths.
- Codex migration artifacts: Codex-facing instructions, migrated skills, and Codex runtime hooks.

## Roadmap

### Near term

- Replace remaining Claude-specific README and package metadata with Codex-first language.
- Audit all migrated skill paths for casing consistency, especially `.agents`, `.codex`, and historical `.claude` references.
- Move local MCP credentials into environment-managed secrets and keep generated config files out of portfolio-safe snapshots.
- Add a migration verification checklist that confirms skill discovery, hook execution, query logging, and representative agent workflows.

### Medium term

- Create a Codex-native onboarding flow for connecting data and choosing pace mode.
- Add migration tests that compare Claude-era and Codex-era behavior for key commands.
- Build a portfolio demo run using a public sample dataset with saved outputs, charts, and a final brief.
- Add clearer status reporting for long-running pipeline stages.

### Long term

- Package the Codex version as a reusable analytics workspace template.
- Add deeper multi-model validation workflows where Codex can cross-check analysis against another model or deterministic evaluator.
- Expand export options for portfolio-ready case studies, executive memos, and public demo decks.

## My role

My role was the **Claude-to-Codex migration owner**, not the original product creator.

What I did:

- Translated the operating instructions from Claude Code conventions into Codex-facing `AGENTS.md` guidance.
- Migrated the skill structure into Codex-compatible `.agents/skills/` paths while preserving the product's analytical standards.
- Added Codex runtime configuration under `.codex/`, including MCP and hook configuration for tool/action logging.
- Preserved the existing architecture of skills, agents, helpers, and persistent knowledge so the product could continue to behave like an AI product analyst after migration.
- Reviewed the system from a product perspective and identified follow-up gaps: residual Claude branding, credential handling, migration verification, and portfolio-safe demo packaging.

What I did not do:

- I did not build the original AI Analyst Plus product from scratch.
- I did not author every agent, helper, analytical method, or design theme.
- I did not claim production adoption or measured business impact without evidence.

## Portfolio takeaway

This project demonstrates my ability to migrate an agentic analytics product across AI coding environments while preserving product intent, user workflows, analytical quality gates, and system architecture. The work required understanding both the user-facing product and the underlying operating model: instructions, skills, agents, helper code, data context, validation, provenance, and runtime hooks.

