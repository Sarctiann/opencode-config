---
name: agent-sync-neovim
description: Use when agent definitions change and you need to synchronize across opencode.jsonc, agents/*.md, opencode_nvim_mcps.jsonc, and the neovim config directory at ~/.config/nvim/lua/utils/opencode-neovim/. Trigger keywords: "sync agents", "sync neovim agents", "update agent definitions", "propagate agent changes", "sync agent configs".
---

# Agent Sync Neovim

Synchronize agent definition changes across all configuration files and the neovim integration directory. Ensures consistency between opencode.jsonc, agent prompt files, MCP permissions, and the deployed neovim config.

## Architecture

There is **one set of agents** that must be kept in sync across multiple locations:

**Agents:** `z-logic`, `z-forge`, `z-nexus`, `z-ultra`, `z-pilot`, `z-spark`

These same agents are configured in:

1. `opencode.jsonc` — model assignments, descriptions, colors, permissions
2. `agents/<name>.md` — prompt definitions (e.g., `agents/z-logic.md`)
3. `opencode-neovim/opencode_nvim_mcps.jsonc` — MCP server config + agent skill permissions
4. `~/.config/nvim/lua/utils/opencode-neovim/` — deployed neovim config copy

The agent names are **identical** in all locations. There are no separate "main" and "neovim" agent families with different names.

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

### 2. Sync Agent Definitions

For each changed agent:

**If opencode.jsonc model/description changed:**
- Update the corresponding `agents/<name>.md` frontmatter if needed
- Update `opencode_nvim_mcps.jsonc` if permissions changed

**If agent prompt (`agents/<name>.md`) changed:**
- The prompt change only affects the agent definition file
- No other files need updating unless frontmatter changed

**Agent names are identical everywhere:**
```
z-logic, z-forge, z-nexus, z-ultra, z-pilot, z-spark
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

**Model uniqueness:**

- No two agents share the same model

**Name references:**

- All agent references use the same names everywhere (`z-logic`, `z-forge`, etc.)

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

- Model uniqueness: ✅
- Name references: ✅
- Skill permissions: ✅
- File sync: ✅
```

## Edge Cases

**New agent added:**

1. Create `agents/<name>.md` with prompt
2. Add to `opencode.jsonc` agent block
3. Add permissions to `opencode_nvim_mcps.jsonc`
4. Sync to neovim directory

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

## Notes

- Agent names are identical in all configuration locations
- Neovim directory sync should exclude `node_modules/`
- Remind user to restart opencode after config changes
- Remind user to restart neovim after neovim config sync
