# Skill: Build Data Product

## Purpose
Orchestrate the full data product build cycle — from a product idea to a
complete, implementation-ready spec — by running the PM Orchestrator and its
6 specialist sub-agents in sequence.

## When to Use
- User says `/build-data-product`, "build a data product", "I want to build a [dashboard/tool/product]"
- User describes a product they want to create using the active dataset

## Invocation
`/build-data-product [product idea]`

## Instructions

### Step 1: Greet and Confirm
Tell the user:
> "Starting the data product build. I'll act as your PM and coordinate 6
> specialist agents: Designer, Data Analyst, Backend Dev, Frontend Dev, QA,
> and DevOps. Each will produce a spec — I'll synthesize them into a full
> Product Build Plan at the end."
>
> "This takes about 10-15 minutes for the full run. You can interrupt at any
> phase to redirect."

### Step 2: Run PM Orchestrator
Read `agents/pm-orchestrator.md` and execute it fully:
- Collect the 4 clarifying questions (Phase 0)
- Write the PRD (Phase 1)
- Run all 6 sub-agents in order (Phase 2)
- Synthesize the Product Build Plan (Phase 3)

Pass user's product idea as `{{PRODUCT_IDEA}}`.

### Step 3: Present the Summary
After all agents complete, present a concise summary:

```
✓ PRD written          → working/prd_{{DATE}}.md
✓ Design spec          → working/design_spec_{{DATE}}.md
✓ Data model           → working/data_model_{{DATE}}.md
✓ Backend spec         → working/backend_spec_{{DATE}}.md
✓ Frontend spec        → working/frontend_spec_{{DATE}}.md
✓ QA test plan         → working/qa_test_plan_{{DATE}}.md
✓ Infrastructure spec  → working/devops_spec_{{DATE}}.md
✓ Product Build Plan   → outputs/product_build_plan_{{DATE}}.md
```

### Step 4: Offer Next Steps
Ask the user:
> "The full spec is ready. What would you like to do next?"
> - "A) Start implementing — I'll help write actual code for any component"
> - "B) Run the data analysis first — explore the dataset before building"
> - "C) Build a prototype deck to pitch this product to stakeholders"
> - "D) Review a specific spec (Design / Data / Backend / Frontend / QA / DevOps)"

## Rules
1. Never skip the PRD — sub-agents depend on it
2. Never fabricate data availability — always check `.knowledge/active.yaml`
3. Keep each sub-agent's output in `working/` until the final plan is assembled
4. If a sub-agent produces a blocker (e.g., required data is missing), surface it to the user before continuing
5. The Product Build Plan in `outputs/` is the deliverable — not the individual working files
