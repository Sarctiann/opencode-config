---
name: agent-sync
description: Use when agent definitions change and you need to synchronize across opencode.jsonc, agents/*.md, agents/z-*.md, opencode_nvim_mcps.jsonc, and the neovim config directory at ~/.config/nvim/lua/utils/opencode-neovim/. Trigger keywords: "sync agents", "sync neovim agents", "update agent definitions", "propagate agent changes", "sync agent configs".
---

# Agent Sync

Synchronize agent definition changes across all configuration files and the neovim integration directory. Ensures consistency between main agents, neovim agents (z-*), MCP permissions, and the deployed neovim config.

## Architecture

There are two agent families that must stay in sync:

**Main agents** (used in standard opencode sessions):
- `logic`, `forge`, `nexus`, `ultra`, `pilot`, `spark`, `build`, `plan`, `explore`, `general`, `free`

**Neovim agents** (prefixed with `z-`, used when opencode runs inside neovim):
- `z-logic`, `z-forge`, `z-nexus`, `z-ultra`, `z-pilot`, `z-spark`

Each z-* agent mirrors its main counterpart but with:
- Neovim-specific tool permissions (bash, write, edit enabled/disabled differently)
- References to other z-* agents in delegation sections (not main agent names)
- Skills permission for neovim MCP tools in `opencode_nvim_mcps.jsonc`

## Configuration Files

| File | Purpose |
|------|---------|
| `opencode.jsonc` | Main agent model assignments, descriptions, colors |
| `agents/<name>.md` | Main agent prompt definitions |
| `agents/z-<name>.md` | Neovim agent prompt definitions (mirrors main) |
| `opencode-neovim/opencode_nvim_mcps.jsonc` | MCP server config + z-* agent skill permissions |
| `~/.config/nvim/lua/utils/opencode-neovim/` | Deployed neovim config copy |

## Workflow

### 1. Identify Changed Agents

Determine which agents were modified. Check:
- `opencode.jsonc` agent block for model/description changes
- `agents/*.md` files for prompt/description changes
- Compare timestamps or ask the user which agents changed

### 2. Sync Main ↔ Neovim Agent Definitions

For each changed main agent that has a z-* counterpart:

**If main agent changed → update z-* agent:**
- Copy the prompt body from `agents/<name>.md` to `agents/z-<name>.md`
- Update agent name references: `logic` → `z-logic`, `forge` → `z-forge`, etc.
- Preserve z-* specific frontmatter (tools, mode settings)
- Keep neovim-specific content intact

**If z-* agent changed → update main agent:**
- Copy the prompt body from `agents/z-<name>.md` to `agents/<name>.md`
- Update agent name references: `z-logic` → `logic`, `z-forge` → `z-forge`, etc.
- Preserve main agent frontmatter

**Agent name mapping:**
```
logic ↔ z-logic
forge ↔ z-forge
nexus ↔ z-nexus
ultra ↔ z-ultra
pilot ↔ z-pilot
spark ↔ z-spark
```

### 3. Update opencode.jsonc

If agent models or descriptions changed:
- Update `agent.<name>.model` for each changed agent
- Update `agent.<name>.description` with `[cost | speed]` prefix
- Ensure no duplicate models across agents
- Add z-* agent entries if new agents were created

### 4. Update opencode_nvim_mcps.jsonc

For each z-* agent, ensure skill permissions are correct:

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

If new z-* agents were added, add their permission blocks.
If z-* agents were removed, remove their permission blocks.

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
- No two agents (main or z-*) share the same model
- Exception: `free` agent can share with main agents if needed

**Name references:**
- Main agents reference main agent names (`logic`, `forge`, etc.)
- z-* agents reference z-* agent names (`z-logic`, `z-forge`, etc.)

**Skill permissions:**
- All z-* agents have neovim skill permissions in `opencode_nvim_mcps.jsonc`
- No z-* agent is missing from the permissions block

**File sync:**
- `opencode-neovim/` contents match `~/.config/nvim/lua/utils/opencode-neovim/`

### 7. Report Changes

Summarize what was synchronized:

```markdown
## Agent Sync Report

### Agents Updated
- `logic` / `z-logic`: Model changed to deepseek-v4-pro, description updated
- `forge` / `z-forge`: Prompt synced, delegation references updated

### Files Modified
- `opencode.jsonc`: Agent models and descriptions
- `agents/z-logic.md`: Prompt synced from logic.md
- `agents/z-forge.md`: Prompt synced from forge.md
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
2. Create `agents/z-<name>.md` with neovim variant
3. Add to `opencode.jsonc` agent block
4. Add z-* permissions to `opencode_nvim_mcps.jsonc`
5. Sync to neovim directory

**Agent removed:**
1. Delete `agents/<name>.md` and `agents/z-<name>.md`
2. Remove from `opencode.jsonc`
3. Remove z-* permissions from `opencode_nvim_mcps.jsonc`
4. Update references in other agents' delegation sections
5. Sync to neovim directory

**Model change only:**
- Only update `opencode.jsonc` agent block
- No prompt sync needed
- Still verify uniqueness

## Notes

- Always sync in both directions (main ↔ z-*) to prevent drift
- The z-* prefix is the only difference in agent names between families
- Neovim directory sync should exclude `node_modules/`
- Remind user to restart opencode after config changes
- Remind user to restart neovim after neovim config sync
