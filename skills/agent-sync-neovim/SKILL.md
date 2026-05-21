---
name: agent-sync-neovim
description: Use when agent definitions change and you need to synchronize across opencode.jsonc, agents/*.md, opencode_nvim_mcps.jsonc, and the neovim config directory at ~/.config/nvim/lua/utils/opencode-neovim/. Trigger keywords: "sync agents", "sync neovim agents", "update agent definitions", "propagate agent changes", "sync agent configs".
---

# Agent Sync Neovim

Synchronize agent definition changes across all configuration files and the neovim integration directory. Ensures consistency between opencode.jsonc, agent prompt files, MCP permissions, and the deployed neovim config.

## Architecture

There is **one set of agents** that must be kept in sync across multiple locations:

**All agents** (any agent defined in `opencode.jsonc`):

These agents are configured in:

1. `opencode.jsonc` — model assignments, descriptions, colors, permissions
2. `agents/<name>.md` — prompt definitions (e.g., `agents/z-logic.md`)
3. `opencode-neovim/opencode_nvim_mcps.jsonc` — MCP server config + agent skill permissions
4. `~/.config/nvim/lua/utils/opencode-neovim/` — deployed neovim config copy

The agent names are **identical** in all locations. There are no separate "main" and "neovim" agent families with different names.

**Primary agents** (mode: "primary") — not selectable as sub-agents, used for direct interaction.
**Sub-agent agents** (mode: "subagent") — can be dispatched by other agents.
**All mode agents** (mode: "all") — can be used both ways.

## Configuration Files

| File                                        | Purpose                                            |
| ------------------------------------------- | -------------------------------------------------- |
| `opencode.jsonc`                            | Agent model assignments, descriptions, colors      |
| `agents/<name>.md`                          | Agent prompt definitions                           |
| `opencode-neovim/opencode_nvim_mcps.jsonc`  | MCP server config + agent skill permissions        |
| `~/.config/nvim/lua/utils/opencode-neovim/` | Deployed neovim config copy                        |

## Workflow

### 1. Identify Changed Agents

Determine which agents were modified. Check:

- `opencode.jsonc` agent block for model/description changes
- `agents/*.md` files for prompt/description changes
- Compare timestamps or ask the user which agents changed

### 2. Verify Agent Integrity

Before syncing, verify that all agents are properly defined:

**Check 1: opencode.jsonc → agents/ directory**
- For every agent in `opencode.jsonc` agent block, verify `agents/<name>.md` exists
- If missing, create it with appropriate frontmatter and placeholder content
- Report any missing files

**Check 2: agents/ directory → opencode.jsonc**
- For every `agents/<name>.md` file, verify the agent exists in `opencode.jsonc`
- If an agent file exists but is not in config, it's orphaned — report it
- Do not delete orphaned files automatically; ask the user

**Check 3: Description consistency**
- Compare `agent.<name>.description` in `opencode.jsonc` with frontmatter `description:` in `agents/<name>.md`
- They should match exactly (including `[cost | speed]` prefix)
- If they differ, sync from `opencode.jsonc` to `agents/<name>.md`

**Check 4: Mode validation**
- Verify `mode:` in `agents/<name>.md` frontmatter is one of: `primary`, `subagent`, `all`
- Invalid modes will cause opencode to fail

**Check 5: Model uniqueness**
- Extract all `model` values from `opencode.jsonc` agent block
- Verify no two agents share the same model
- Report any duplicates

### 3. Sync Agent Definitions

For each changed agent:

**If opencode.jsonc model/description changed:**
- Update the corresponding `agents/<name>.md` frontmatter if needed
- Update `opencode_nvim_mcps.jsonc` if permissions changed

**If agent prompt (`agents/<name>.md`) changed:**
- The prompt change only affects the agent definition file
- No other files need updating unless frontmatter changed

**Agent names are identical everywhere:**
```
All agents from opencode.jsonc: build, plan, explore, general, x--free, x-learn, z-logic, z-forge, z-nexus, z-ultra, z-pilot, z-spark
```

### 3. Update opencode.jsonc

If agent models or descriptions changed:

- Update `agent.<name>.model` for each changed agent
- Update `agent.<name>.description` with `[cost | speed]` prefix
- Ensure no duplicate models across agents

### 4. Update opencode_nvim_mcps.jsonc

For each agent, ensure skill permissions are correct:

```jsonc
"agent": {
  "z-logic": {
    "permission": {
      "skill": {
        "using-neovim": "allow",
        "using-quickfix": "allow",
        "using-neovim-lsp": "allow",
        "*": "ask",
      },
    },
  },
  // ... same pattern for z-forge, z-nexus, z-ultra, z-pilot, z-spark
}
```

If new agents were added, add their permission blocks.
If agents were removed, remove their permission blocks.

### 5. Sync to Neovim Config Directory

Copy the updated `opencode-neovim/` folder to the neovim config location:

```bash
rsync -av --exclude='node_modules' --exclude='.git' \
  ~/.config/opencode/opencode-neovim/ \
  ~/.config/nvim/lua/utils/opencode-neovim/
```

Files to sync:

- `opencode_nvim_mcps.jsonc`
- `AGENTS.md`
- `README.md`
- `skills/**/*.md`
- `commands/**/*.md`
- `.gitignore`
- `package.json` (if changed)

### 6. Verify Consistency

Run these checks:

**Agent file integrity:**

- Every agent in `opencode.jsonc` has a corresponding `agents/<name>.md` file
- Every `agents/<name>.md` file has a corresponding entry in `opencode.jsonc`
- No orphaned agent files exist (or if they do, they are reported)

**Description consistency:**

- `opencode.jsonc` descriptions match `agents/<name>.md` frontmatter descriptions
- All descriptions have `[cost | speed]` prefix format

**Model uniqueness:**

- No two agents share the same model

**Name references:**

- All agent references use the same names everywhere

**Skill permissions:**

- All agents have neovim skill permissions in `opencode_nvim_mcps.jsonc`
- No agent is missing from the permissions block

**File sync:**

- `opencode-neovim/` contents match `~/.config/nvim/lua/utils/opencode-neovim/`

### 7. Report Changes

Summarize what was synchronized:

```markdown
## Agent Sync Report

### Agents Updated

- `z-logic`: Model changed to deepseek-v4-pro, description updated
- `z-forge`: Prompt updated, permissions verified

### Files Modified

- `opencode.jsonc`: Agent models and descriptions
- `agents/z-logic.md`: Prompt synced
- `opencode-neovim/opencode_nvim_mcps.jsonc`: Skill permissions verified

### Neovim Config Synced

- Copied to ~/.config/nvim/lua/utils/opencode-neovim/

### Consistency Checks

- Agent file integrity (jsonc ↔ agents/): ✅
- Description consistency: ✅
- Model uniqueness: ✅
- Name references: ✅
- Skill permissions: ✅
- File sync: ✅
```

## Edge Cases

**New agent added:**

1. Verify `agents/<name>.md` exists with proper frontmatter (mode, description with `[cost | speed]` prefix)
2. Verify agent is in `opencode.jsonc` agent block with model, description, color
3. Add permissions to `opencode_nvim_mcps.jsonc`
4. Sync to neovim directory
5. If `mode` is `primary`, note that this agent is not selectable as sub-agent

**Agent removed:**

1. Delete `agents/<name>.md`
2. Remove from `opencode.jsonc`
3. Remove permissions from `opencode_nvim_mcps.jsonc`
4. Update references in other agents' delegation sections
5. Sync to neovim directory

**Model change only:**

- Only update `opencode.jsonc` agent block
- No prompt sync needed
- Still verify uniqueness

**Description mismatch:**

- If `opencode.jsonc` description differs from `agents/<name>.md` frontmatter
- Sync from `opencode.jsonc` to `agents/<name>.md` (source of truth)
- Preserve any non-frontmatter content in the `.md` file

**Missing agent file:**

- If agent exists in `opencode.jsonc` but `agents/<name>.md` is missing
- Create the file with proper frontmatter and a placeholder prompt
- Alert the user that the file was created and needs proper content

**Orphaned agent file:**

- If `agents/<name>.md` exists but agent is not in `opencode.jsonc`
- Report it to the user; do not delete automatically
- Suggest removal if the agent is no longer needed

## Notes

- Agent names are identical in all configuration locations
- Neovim directory sync should exclude `node_modules/`
- Remind user to restart opencode after config changes
- Remind user to restart neovim after neovim config sync
