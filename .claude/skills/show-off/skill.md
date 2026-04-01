# Skill: Show Off

## Purpose
Automatically analyze what the student has built and share a visual showcase
to the AI Analyst Lab community on Slack. Claude does all the work — reads
the git history, understands the code, builds an ASCII diagram, and posts it.

## When to Use
- User says `/show-off` or "share what I built" or "show the community"
- After completing an analysis, pipeline, or building something cool

## Invocation
`/show-off` — share what you've built with the community

## Prerequisites
- Slack MCP server must be configured with the student's user token
- If Slack MCP tools are not available, tell the student:
  "Slack isn't connected yet. Run `/kickoff` first to connect your Slack account."
- Student should have already run `/kickoff` — if not, suggest they do that first

## Instructions

### Step 1: Analyze What They Built

Do NOT ask the student to explain anything. Figure it out yourself.

**Try git first:**
1. **Run `git log --oneline -20`** to see recent commits
2. **Run `git diff --stat HEAD~10`** (or since their first commit) to see what files changed
3. **Read the key files** — new agents, skills, helpers, configs, analysis outputs

**If there are no commits** (student hasn't committed yet, or code has changed but
nothing's been staged), fall back to scanning the workspace:
1. **Run `git status`** to see modified and untracked files
2. **Run `git diff`** to see unstaged changes
3. **List key directories** — `agents/`, `skills/`, `helpers/`, `analysis/`, any output dirs
4. **Read new or modified files** to understand what they contain

**Understand the architecture** — what components exist, how they connect, what data
flows where. Build a mental model of what they created: agents, skills, pipelines,
data sources, outputs, and how they all fit together.

### Step 2: Build the ASCII Diagram

Create an ASCII art diagram that visualizes what they built. This should show
the architecture, data flow, or pipeline they created.

Guidelines:
- Use box-drawing characters for clean boxes: `┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼`
- Use arrows for data flow: `→ ← ↓ ↑` or `-->` for connections
- Label everything clearly
- Keep it compact but readable in Slack (monospace font)
- Show the interesting parts — don't just list files

**Example styles** (for reference, adapt to what they actually built):

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Question   │───→│  SQL Agent   │───→│   Charts    │
│  "Why are   │    │  queries     │    │   3 viz     │
│  sales down"│    │  NovaMart DB │    │   generated │
└─────────────┘    └──────────────┘    └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  Narrative   │
                                       │  "Weekend    │
                                       │  drop-off    │
                                       │  in mobile"  │
                                       └─────────────┘
```

```
    🏗️ My AI Analyst

    User Question
         │
         ▼
    ┌─────────┐   ┌──────────┐   ┌────────────┐
    │ Planner │──→│ Analyst  │──→│ Visualizer │
    └─────────┘   └──────────┘   └────────────┘
         │              │              │
         ▼              ▼              ▼
    plan.md        analysis.md    charts/*.png
                                       │
                                       ▼
                                ┌────────────┐
                                │ Storyteller │──→ report.md
                                └────────────┘
```

### Step 3: Compose the Post

Combine a one-line intro + the ASCII diagram into a Slack message. Format:

```
[One-line description of what they built] [emoji]

[ASCII diagram in a code block]
```

The one-line intro should be specific to what they built. Examples:
- "Built a 4-agent pipeline that goes from question to charts to narrative 🔥"
- "My AI Analyst just analyzed 50K rows of checkout data and found the weekend drop-off 📊"
- "First full pipeline run — question in, report out, 3 agents, zero SQL written by hand 🚀"

### Step 4: Confirm Before Posting

Show the student the full message and ask:
**"Here's your showcase for #show-and-tell. Want me to send it, or change anything?"**

Do NOT post until they confirm.

### Step 5: Post to Slack

Post the message to the `#show-and-tell` channel using the Slack MCP.

Use the channel name `show-and-tell` when calling the Slack MCP send message tool.

Wrap the ASCII diagram in triple backticks so Slack renders it in monospace.

### Step 6: Celebrate

After posting, say something like:
**"Posted! 🎉 Check #show-and-tell to see it live. Keep building — you can `/show-off` again anytime."**

## Rules
1. Always confirm before posting — never auto-send
2. The student should NOT have to explain what they built — Claude figures it out
3. The ASCII diagram is the star of the post — make it clean and impressive
4. Keep the intro line short — one sentence max
5. Works with or without git commits — use `git status` and `git diff` for uncommitted work
6. No limit on show-offs — encourage it every time they build something new
7. If they haven't run `/kickoff` yet, nudge them to do that first
