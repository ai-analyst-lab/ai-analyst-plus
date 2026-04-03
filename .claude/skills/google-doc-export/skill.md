# Skill: Google Doc Export

## Purpose

Create properly formatted Google Docs via the MCP API. Prevents common issues:
text/image overlap, broken heading hierarchy, excessive whitespace, inconsistent
formatting. The Google Docs equivalent of the Google Slides Export skill.

## When to Apply

Automatically whenever:
- `mcp__google-workspace__batch_update_doc` will be called
- A Google Doc is being designed or built
- The `google-doc-creator` or `google-doc-reviewer` agent is running

---

## Section A: Pre-Flight Checklist

Run this checklist BEFORE building any batch_update requests. Fix all violations first.

- [ ] **Text inserted before images** — all text content must be in the doc
      before any image insertion. Images shift all indices.
- [ ] **Images in dedicated paragraphs** — every image gets its own paragraph.
      Never insert an image into a paragraph that already contains text.
- [ ] **Bottom-to-top image insertion** — insert the last section's image first,
      then work backwards. Prevents index invalidation.
- [ ] **Re-read structure after each image** — call `inspect_doc_structure` after
      every `insert_doc_image` call to get fresh indices.
- [ ] **Heading hierarchy is clean** — exactly one H1, H2 for sections, H3 for
      subsections. No skipped levels.
- [ ] **No more than 2 consecutive empty paragraphs** anywhere in the document.
- [ ] **Drive file IDs used for images** — not tmpfiles.org URLs (they expire).
- [ ] **Image deduplication audit** — before inserting any image, inspect the doc
      structure and check for existing 2-char paragraphs (inline object + newline)
      at the target location. If an image already exists there, skip insertion.
- [ ] **Table spacing** — every table must have 1 empty paragraph before and after
      it. Text must never run directly into a table or start immediately after one.
- [ ] **No stub headings** — never insert a heading without body content beneath it.
      If data for a section doesn't exist, omit the heading entirely.
- [ ] **Both width AND height specified for images** — `insert_doc_image` requires
      both dimensions. Omitting height causes an API error.

---

## Section B: Document Structure Template

### Standard Analysis Document

```
H1: [Document Title]
    [Subtitle — scope, date, author]

H2: Executive Summary
    [3-5 sentence overview]
    [Numbered key findings — max 3]
    [Bottom line statement]

H2: Section 1: [Topic]
    [Chart image — centered, 400pt wide]
    [The Insight: bold label + finding]
    [Supporting evidence paragraphs]
    [Why this matters for product: bold label + implication]

H2: Section 2: [Topic]
    ... (repeat pattern)

H2: Data Quality and Limitations
    [Outlier investigation]
    [Sample size notes]
    [Methodology caveats]

H2: Recommendations
    [Numbered list of actionable recommendations]
    [Each with a bold title + explanation paragraph]

H2: Appendix
    [Summary statistics tables]
```

### Section Spacing Rules

```
After H1:          2 empty paragraphs
After H2:          1 empty paragraph
Before chart:      1 empty paragraph
After chart:       1 empty paragraph
Before table:      1 empty paragraph
After table:       1 empty paragraph
Between sections:  2 empty paragraphs (includes the pre-H2 spacing)
Between paragraphs: 0 empty paragraphs (natural paragraph spacing)
After bullet list:  1 empty paragraph
```

---

## Section C: Image Placement Rules

### Sizing

```
Standard chart:     width=400, height=300  (4:3 ratio)
Wide chart:         width=500, height=280  (16:9 ratio)
Square chart:       width=350, height=350  (1:1 ratio)
Small inline:       width=250, height=200  (for side notes)
```

Always specify both width and height. If only one dimension is known,
calculate the other from the image's aspect ratio.

### Placement Workflow

For each section that needs a chart:

1. **Audit for existing images first** — call `inspect_doc_structure(detailed=true)`
   and scan for 2-char paragraphs (start_index to end_index = 2 chars) near the
   target location. These are inline image objects. Also check if any text paragraph
   has 1 more character than its visible text — that extra char is an old inline
   image. **If an image already exists at the target, SKIP insertion.**

2. **Create a dedicated image paragraph** — insert `"\n\n"` at the target index
   via `batch_update_doc`. The first `\n` becomes the image paragraph, the second
   creates a blank line below the image for spacing. This is an ATOMIC step — do
   it before inserting the image.

3. **Insert the image** at the first `\n`'s start_index (the new empty paragraph):
   ```
   mcp__google-workspace__insert_doc_image(
       document_id=...,
       image_source="<DRIVE_FILE_ID>",
       index=<empty_para_start>,
       width=400,
       height=300
   )
   ```
   **CRITICAL:** Always pass the Drive file ID directly as `image_source`, and
   always specify BOTH `width` and `height`. Omitting height causes an API error.

4. **Center the image paragraph:**
   ```
   update_paragraph_style(
       start_index=<image_para_start>,
       end_index=<image_para_end>,
       alignment="CENTER"
   )
   ```

5. **Re-read structure** — `inspect_doc_structure` again before the next image.

6. **Work bottom-to-top** — insert the last section's image first, then work
   backwards. This prevents earlier insertions from shifting later indices.

### Detecting Duplicate Images

An inline image in Google Docs is a single replacement character (U+FFFC). The
`inspect_doc_structure` tool shows it as a 2-char paragraph (`[image_char]\n`)
with text_preview `"\n"`. To detect old inline images embedded in text:

```
Expected text length = len("paragraph text content") + 1  (for \n)
Actual paragraph length = end_index - start_index
If actual > expected: the paragraph contains an inline image character
```

To remove: delete 1 char at the paragraph's start_index (the inline object).
The text remains intact.

### Image URL Format

```
OK:  https://drive.google.com/uc?id={FILE_ID}&export=download
OK:  https://tmpfiles.org/dl/{ID}/chart.png  (temporary — expires in 1 hour)
BAD: data:image/png;base64,...  (not supported)
BAD: http://localhost:...  (not accessible by Google servers)
```

Always prefer Drive file IDs. Upload to Drive first, then use the Drive URL.

---

## Section D: Text Formatting Rules

### Heading Styles

| Level | Use for | Applied via |
|-------|---------|-------------|
| H1 | Document title (exactly one) | `update_paragraph_style(heading_level=1)` |
| H2 | Major sections | `update_paragraph_style(heading_level=2)` |
| H3 | Subsections within a section | `update_paragraph_style(heading_level=3)` |
| Normal | Body text, bullets, data | Default (no heading_level needed) |

### Bold Labels

These phrases should always be bold when they appear at the start of a paragraph:
- "The Insight:"
- "Why this matters for product:"
- "Bottom line:"
- "Key context:"
- "Data quality flag:"
- "Sample size warning:"
- "The creative angle:"
- "The interpretation:"

Apply bold via `modify_doc_text` with bold=true on the label text range.

### Lists

- Use `update_paragraph_style(list_type="UNORDERED")` for bullet lists
- Use `update_paragraph_style(list_type="ORDERED")` for numbered lists
- Nest with `list_nesting_level=1` for sub-items

### Tables (All Types)

Google Docs tables require a specific creation workflow to avoid index errors:

**Table Creation Pattern:**
1. **Insert the table** via `insert_table` at a known index (after an empty paragraph)
2. **Read cell indices** via `debug_table_structure` — never guess cell positions
3. **Populate cells bottom-to-top** (highest cell index first) to avoid index shifts
4. **Bold header row** — format the first row with bold + slightly larger font (12pt)
5. **Add spacing** — ensure 1 empty paragraph before and after the table

**Table Spacing Rule (MANDATORY):**
After every table, there MUST be at least 1 empty paragraph (`\n`) before the
next text paragraph begins. Without this, text runs directly into the table
bottom border, which looks broken.

**Header Row Formatting:**
All table header cells should be bold with font_size=12. Apply via `format_text`
on each header cell's text range after population.

### Appendix Tables

For summary statistics, prefer Google Docs tables over plain text.
Numeric columns should be right-aligned.

---

## Section E: Common Pitfalls

| Pitfall | What happens | Prevention |
|---------|-------------|------------|
| Insert image into text paragraph | Image overlaps with text, unreadable | Always insert into empty dedicated paragraph |
| Insert images top-to-bottom | Later indices are wrong, images land in wrong spots | Always insert bottom-to-top |
| Don't re-read structure after image | Subsequent operations use stale indices | Re-read after every image insertion |
| Use tmpfiles.org URL in doc | Image disappears after 1 hour | Upload to Drive first, use Drive URL |
| Skip heading formatting | Document has no structure, looks like a wall of text | Apply heading styles immediately after text insertion |
| Too many empty paragraphs | Excessive whitespace, unprofessional | Max 2 consecutive empty paragraphs |
| Bold entire paragraphs | Hard to read, loses emphasis effect | Bold only labels/key phrases, not full paragraphs |
| No spacing after tables | Text runs into table bottom border | Always 1 empty paragraph after every table |
| Re-insert images on session resume | Duplicate charts appear side by side | Audit for existing images before inserting |
| Insert image at text paragraph start | Image becomes inline char, text flows after it | Always create dedicated empty paragraph first |
| Stub headings with no body | Orphaned headings confuse readers | Only insert headings that have content beneath |
| Populate table cells top-to-bottom | Index shifts corrupt later cells | Always populate cells bottom-to-top (highest index first) |
| Omit height in insert_doc_image | API error: "height must be greater than 0" | Always specify both width AND height |
