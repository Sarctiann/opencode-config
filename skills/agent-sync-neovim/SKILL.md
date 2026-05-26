---
name: agent-sync-neovim
description: Use when synchronizing Neovim integration files between opencode-neovim/ and ~/.config/nvim/lua/utils/opencode-neovim/. Trigger keywords: "sync agents", "sync neovim agents", "update agent definitions", "propagate agent changes", "sync agent configs".
---

# Agent Sync Neovim

Synchronize only the Neovim integration files that live inside `opencode-neovim/` with their deployed Neovim mirror.

## Hard Scope Boundary

This skill may write only inside these two directories:

1. `~/.config/opencode/opencode-neovim/`
2. `~/.config/nvim/lua/utils/opencode-neovim/`

Files outside those directories are **read-only inputs**. Do not create, modify, delete, copy, or synchronize any file outside the two allowed directories.

Forbidden write targets include, but are not limited to:

- `~/.config/opencode/opencode.jsonc`
- `~/.config/opencode/agents/*.md`
- `~/.config/opencode/skills/*`
- any path outside `opencode-neovim/` in this repository
- any path outside `~/.config/nvim/lua/utils/opencode-neovim/` in the Neovim config

If a requested sync requires changing a forbidden path, stop and report that the file is outside this skill's sync boundary.

## Architecture

There are two zones:

| Zone | Paths | Access |
| ---- | ----- | ------ |
| Neovim integration source (source of truth) | `~/.config/opencode/opencode-neovim/` | read/write — **all changes go here first** |
| Neovim integration mirror | `~/.config/nvim/lua/utils/opencode-neovim/` | **read-only during edits**, synced only after commit |
| External opencode config | `~/.config/opencode/opencode.jsonc`, `~/.config/opencode/agents/*.md` | read-only |

The only bidirectional sync is between the source and mirror zones. External opencode config can be inspected to understand desired agent names or permissions, but it must never be updated by this skill.

**Key principle:** The mirror is a deployment target, not an edit location. All modifications happen in the source, are committed, and only then propagated to the mirror.

## Files Eligible for Sync

Only files under `opencode-neovim/` are eligible:

- `opencode-neovim/opencode_nvim_mcps.jsonc`
- `opencode-neovim/AGENTS.md`
- `opencode-neovim/README.md`
- `opencode-neovim/skills/**`
- `opencode-neovim/commands/**`
- `opencode-neovim/.gitignore`
- other files physically inside `opencode-neovim/`

The matching mirror path is always the same relative path under `~/.config/nvim/lua/utils/opencode-neovim/`.

## Workflow

### 1. Pre-Flight Path Guard

Before any write operation, verify the target path starts with one of the allowed prefixes:

- `/Users/sebastianrodriguezcapurro/.config/opencode/opencode-neovim/`
- `/Users/sebastianrodriguezcapurro/.config/nvim/lua/utils/opencode-neovim/`

If the target path is outside both prefixes, do not write it. Report the blocked path.

### 2. All Changes Go to Source First

**Always make changes in `opencode-neovim/` first.** This is the source of truth.

- Edit files only inside `~/.config/opencode/opencode-neovim/`
- Do NOT write directly to `~/.config/nvim/lua/utils/opencode-neovim/` unless the user explicitly requests it
- The mirror is read-only during normal edit workflows

### 3. Identify Neovim Integration Changes

After changes are made to `opencode-neovim/`, determine what needs to be synced:

- Compare `opencode-neovim/` with `~/.config/nvim/lua/utils/opencode-neovim/`
- Check timestamps or diffs for files inside those directories only
- If the user mentions `opencode.jsonc` or `agents/*.md`, treat them as read-only references, not sync targets

### 4. Commit Phase (User-Triggered)

When the user asks to commit changes:

1. Create a git commit for changes in `opencode-neovim/`
2. Only **after** the commit is created, proceed to sync the mirror

### 5. Mirror Sync (Post-Commit Only)

Sync from repo source to Neovim mirror **only after a commit has been made**:

```bash
rsync -av --exclude='node_modules' --exclude='.git' \
  ~/.config/opencode/opencode-neovim/ \
  ~/.config/nvim/lua/utils/opencode-neovim/
```

Do not add extra rsync sources or destinations.

**Reverse sync** (mirror → source) is only performed when the user explicitly requests it:

```bash
rsync -av --exclude='node_modules' --exclude='.git' \
  ~/.config/nvim/lua/utils/opencode-neovim/ \
  ~/.config/opencode/opencode-neovim/
```

### 6. Update Neovim MCP Permissions When Needed

If agent-related Neovim permissions must change, edit only:

- `opencode-neovim/opencode_nvim_mcps.jsonc`
- its mirror file at `~/.config/nvim/lua/utils/opencode-neovim/opencode_nvim_mcps.jsonc` (only during post-commit sync)

You may read `opencode.jsonc` to identify current agent names, but do not modify `opencode.jsonc` or `agents/*.md`.

### 7. Verify Consistency

Run these checks:

- Every modified path is inside one of the two allowed directories
- After sync: `opencode-neovim/` contents match `~/.config/nvim/lua/utils/opencode-neovim/`
- `opencode_nvim_mcps.jsonc` remains valid JSONC-compatible opencode config
- No `opencode.jsonc` or `agents/*.md` file was created, modified, deleted, copied, or synchronized
- Mirror was not modified before commit (unless user explicitly requested it)

### 8. Report Changes

Summarize only files inside the allowed directories:

```markdown
## Agent Sync Report

### Neovim Integration Files Updated (Source)

- `opencode-neovim/opencode_nvim_mcps.jsonc`: Skill permissions updated
- `opencode-neovim/skills/...`: Skill definition updated

### Commit Status

- Changes committed: ✅ (or pending if not yet committed)

### Mirror Sync Status

- `~/.config/nvim/lua/utils/opencode-neovim/`: Synced (or pending until commit)

### Consistency Checks

- Allowed path guard: ✅
- Source/mirror match: ✅ (after sync)
- No writes outside `opencode-neovim/`: ✅
- Mirror not modified before commit: ✅
```

## Edge Cases

**Agent added or removed outside `opencode-neovim/`:**

- Read `opencode.jsonc` if necessary to update Neovim permissions inside `opencode-neovim/opencode_nvim_mcps.jsonc`
- Do not create, delete, or modify `agents/<name>.md`
- Do not modify `opencode.jsonc`

**Description, model, or prompt mismatch outside `opencode-neovim/`:**

- Report the mismatch as outside this sync workflow
- Do not reconcile it automatically

**User asks to sync all config files:**

- Sync only files under `opencode-neovim/` and its mirror
- Explicitly state that files outside `opencode-neovim/` are excluded

## Common Rationalizations to Reject

| Rationalization | Required response |
| ---------------- | ----------------- |
| "`opencode.jsonc` is agent config, so it should be synced too." | No. It is outside `opencode-neovim/` and is read-only for this skill. |
| "Fixing `agents/*.md` would make consistency checks pass." | No. Report the mismatch; do not write outside the boundary. |
| "The Neovim mirror needs a copy of an external file." | No. Only files physically inside `opencode-neovim/` are mirrored. |
| "This is just a small metadata update." | No. Scope is path-based, not size-based. |
| "I'll update the mirror directly to save time." | No. All changes go to source first, then commit, then sync. |
| "The mirror is already read/write in the workflow." | No. Mirror is read-only during edits. Sync happens post-commit only. |

## Notes

- Neovim directory sync should exclude `node_modules/` and `.git/`
- Remind the user to restart opencode after skill/config changes
- Remind the user to restart Neovim after Neovim integration sync
