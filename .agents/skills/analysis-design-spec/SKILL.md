---
name: analysis-design-spec
description: Produce a lightweight seven-field analysis design spec before querying data. Use at the start of analytical requests to align question, decision, data, dimensions, time range, output, and success criteria.
---

# Analysis Design Spec

## Purpose
Prevent wasted analytical work by aligning scope before queries or charts.

## Workflow
1. Fill seven required fields:
   - Question: specific, testable ask;
   - Decision: action the answer informs;
   - Data Needed: fields/tables/sources and availability;
   - Dimensions: segments/decompositions and why they matter;
   - Time Range and Granularity;
   - Output Format;
   - Success Criteria.
2. Scale detail to request complexity: quick number pulls get a short spec; deep dives get full sections.
3. Stop and present the spec for user confirmation before substantive querying, unless the request is trivial and assumptions are low risk.
4. Update the spec if the user corrects scope.
5. Use the spec during analysis to avoid rabbit holes and verify done-ness.

## Output contract
Use the heading `Analysis Design Spec` with the seven numbered sections. Flag unknowns and data gaps explicitly.

## Safety
- Do not proceed when the decision, metric, time window, or dataset ambiguity would materially change the answer.
- Do not over-scope simple monitoring questions.
