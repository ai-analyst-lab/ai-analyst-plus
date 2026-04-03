# Skill: Auth Preflight

## Purpose

Verify Google Workspace MCP authentication at the start of any session that
needs Google APIs. Catches auth issues immediately instead of discovering them
mid-workflow after significant work has been done.

## When to Apply

Automatically at session start when:
- The task involves Google Docs, Slides, or Drive
- Any `mcp__google-workspace__*` tool will be called
- The user mentions "Google Doc", "Google Slides", "upload to Drive", etc.

---

## Preflight Steps

### Step 1: Check stored credentials

```bash
ls ~/.google_workspace_mcp/credentials/
```

If no files exist → auth has never been completed. Skip to Step 3.

If files exist → note the exact email in the filename. This is the email
that MUST be used for all MCP calls.

**CRITICAL:** The email in the filename may differ from what you expect.
Gmail treats dots as equivalent (`a.b@gmail.com` = `ab@gmail.com`) but the
MCP server stores tokens by EXACT string. Always use the email from the
credential filename.

### Step 2: Test with a lightweight API call

Make a simple read-only call to verify the token is still valid:

```
mcp__google-workspace__get_doc_content(
    user_google_email="{email_from_credentials_file}",
    document_id="18MTagnf_z5Gn3MFWXARrzNbUk8FBFFZYLQADMn_h434"
)
```

(Use any known document ID. The MS Case Study doc above is a safe test target.)

**If successful:** Auth is valid. Proceed with the task. Report:
"Google Workspace auth verified for {email}."

**If auth error:** Proceed to Step 3.

### Step 3: Re-authenticate

Present the auth URL to the user with these instructions:

1. **Copy-paste the URL** into your browser. Do NOT cmd-click — terminal
   cmd-click can corrupt the URL by appending extra text.

2. Select your Google account when prompted.

3. If you see "Access blocked: app not verified" → you need to add yourself
   as a test user in your Google Cloud Console:
   - Go to console.cloud.google.com → APIs & Services → OAuth consent screen
   - Under "Test users", add your email
   - Then try the auth URL again

4. After successful auth, tell me "done" and I'll verify.

### Step 4: Verify after re-auth

After the user confirms auth, make the same test call from Step 2.

**If successful:** Proceed with the task.
**If still failing:** Check:
- Is the MCP server running? `lsof -i :8000`
- Did a new credential file appear? `ls ~/.google_workspace_mcp/credentials/`
- Does the email in the new credential match what we're using?

---

## Known Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Email mismatch | Auth succeeds but API calls fail | Use email from credential filename, not user's input |
| Token expired | "Authentication Needed" on every call | Re-auth via Step 3 |
| App not verified | "Access blocked" after account selection | Add email as test user in Google Cloud Console |
| URL corruption | 400 error on auth URL | Copy-paste URL manually, don't cmd-click |
| MCP server down | No process on port 8000 | Restart Claude Code session (MCP server auto-starts) |

---

## Sravya's Auth Details

- **Email for MCP calls:** `madipalli.sravya@gmail.com`
- **Google Cloud project client ID:** `501145746678-...`
- **Credential file:** `~/.google_workspace_mcp/credentials/madipalli.sravya@gmail.com.json`
- **MCP server:** `workspace-mcp --tools docs slides drive` on port 8000

---

## Rules

1. **Run preflight BEFORE any Google work.** Don't discover auth issues after
   generating 8 charts and writing 2000 words of narrative.

2. **Always use the email from the credential file.** Never assume the email
   format — read it from disk.

3. **One auth attempt, then explain.** If re-auth fails, explain the likely
   cause (test user, URL corruption, etc.) rather than looping.

4. **Report auth status clearly.** At the end of preflight, state:
   "Auth: OK (madipalli.sravya@gmail.com)" or "Auth: FAILED — [reason]"
