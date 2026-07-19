# Architecture Diagrams

Mermaid source for the diagrams in
[`../workflows-and-architecture.md`](../workflows-and-architecture.md). The doc
embeds these as inline ` ```mermaid ` blocks, so **they render automatically on
GitHub and in VS Code (Markdown Preview) with no tooling.** These `.mmd` files
and the render script exist for when you want standalone SVG/PNG image files.

| File | Diagram |
|------|---------|
| `pipeline-dag.mmd` | The `full_presentation` agent DAG — tiers, AND/OR gates, checkpoints (§3.9) |
| `validation-flow.mmd` | The 4-layer validation → confidence-score data flow (§4.5) |
| `experiment-decision-tree.mmd` | The `/experiment interpret` Ship/Abort/Learn/Invalid tree (§5.4) |

## Render to SVG + PNG

```bash
cd docs/diagrams
./render.sh                 # render all *.mmd
./render.sh pipeline-dag    # render just one
```

`render.sh` auto-detects a local Chrome/Chromium/Edge/Brave and uses
`npx @mermaid-js/mermaid-cli` (fetched on first run). Requires Node 18+.

> Rendering uses a headless browser under the hood. It works in a normal
> terminal but may be blocked in restricted/sandboxed shells (the browser
> process can't launch). If so, rely on the inline GitHub/VS Code rendering,
> or paste a `.mmd` file into <https://mermaid.live> to export an image.

## Editing

Edit the `.mmd` file **and** the matching inline block in
`../workflows-and-architecture.md` together so the doc and the standalone
sources stay in sync. `mermaid-config.json` holds shared render settings
(theme, flowchart options).
