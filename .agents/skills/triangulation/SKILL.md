---
name: triangulation
description: Sanity-check analytical findings using segment-first validation, internal consistency, cross-reference, and external plausibility. Use before presenting findings or when results seem surprising.
---

# Triangulation

## Purpose
Validate important findings from multiple angles before they become recommendations.

## Workflow
1. Start with mandatory segment-first validation: check whether aggregate findings hold across key segments and whether Simpson's paradox or mix shift may explain results.
2. Check internal consistency: totals reconcile, denominators match, metric components tie out, and time windows align.
3. Cross-reference against independent sources or alternative query paths where available.
4. Check external plausibility: business constraints, known ranges, historical benchmarks, seasonality, and operational reality.
5. Look for common errors: survivorship bias, timezone boundaries, incomplete windows, denominator changes, duplicate rows, and correlation/causation confusion.
6. Assign finding-level confidence and list caveats and additional validation needed.

## Output contract
Produce a Validation Report with Overall Confidence, Finding-by-Finding Validation, Caveats for Stakeholders, and Recommended Additional Validation.

## Safety
- Never use triangulation to rubber-stamp a preferred answer.
- If validation fails, downgrade confidence or stop before recommendation.
