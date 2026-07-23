---
name: business
description: Browse, search, and summarize organization business context from `.knowledge/organizations`: glossary, products, metrics, objectives, and teams. Use when users ask about business terms, products, OKRs, teams, or documented organizational knowledge.
---

# Business Context

## Purpose
Show documented organizational knowledge, not live data analysis.

## Scope boundary
This skill reads `.knowledge/organizations/{org}/business/` files. It does not query datasets, analyze product tables, show user profiles, or browse analysis history.

## Workflow
1. Resolve the organization from `.knowledge/setup-state.yaml` or by inspecting `.knowledge/organizations/`.
2. Use `helpers.business_context` functions when possible: `load_business_context`, `get_glossary`, `get_products`, `get_metrics`, `get_objectives`, and `get_teams`.
3. Choose the mode:
   - overview: counts and available categories;
   - glossary/products/metrics/objectives/teams: category table;
   - lookup/search: search across categories.
4. If formal context is sparse, optionally summarize implicit knowledge from `.knowledge/analyses/index.yaml` and active dataset quirks, clearly labeled as inferred.
5. Provide next steps to add or formalize missing context.

## Output contract
Use concise tables and identify the source file/category. For empty categories, say where to add entries.

## Safety
- Do not query database tables for business context.
- Do not invent definitions; distinguish documented vs inferred knowledge.
