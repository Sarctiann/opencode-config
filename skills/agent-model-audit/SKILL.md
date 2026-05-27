---
name: agent-model-audit
description: Use when auditing agent models, reviewing provider offerings, optimizing model assignments by cost and speed, or updating agent descriptions with cost/speed indicators. Trigger keywords: "audit agents", "audit models", "update agent models", "review models", "optimize agents".
---

# Agent Model Audit

Audit connected providers, analyze model offerings (cost, speed, usage limits), and optimize agent-to-model assignments. Produces a dated audit report and updates agent configurations.

> **Important:** The current model assignments in `opencode.jsonc` are the **output** of this process, not the input. Discard them at the start. All assignments will be determined fresh from the data gathered in steps 1–5.

## Priority Mode

The optimization priority is determined by an optional argument passed to the command:

| Argument (EN/ES)                              | Priority Order          |
| --------------------------------------------- | ----------------------- |
| `skill` / `ability` / `habilidad` _(default)_ | Role fit → Cost → Speed |
| `price` / `cost` / `precio` / `barato`        | Cost → Role fit → Speed |
| `speed` / `fast` / `velocidad` / `rapido`     | Speed → Role fit → Cost |

If no argument was provided, use **`skill`** mode (role fit first).

## Workflow

### 1. Discover Available Models

Run the following command to get the authoritative list of models available in opencode:

```bash
opencode models
```

This returns the full list of `provider/model` identifiers actually configured and accessible. **This is the only source of truth** — do not use general knowledge or assumptions about what models exist.

From the output:

- Note every `provider/model` identifier
- Group by provider
- Identify which providers are active (not in `disabled_providers` in `opencode.jsonc`)

> **Critical:** Only models that appear in `opencode models` output are candidates for agent assignment.
>
> **⚠️ Model identifiers must match EXACTLY — character for character.**
> Pay close attention to punctuation. Model names use hyphens, not dots:
>
> - ✅ `opencode/claude-sonnet-4-6` (correct — hyphens)
> - ❌ `opencode/claude-sonnet-4.6` (incorrect — dot)
> - ✅ `opencode/gpt-5.4` (correct — dot is part of the version)
> - ❌ `opencode/gpt-5-4` (incorrect — hyphen instead of dot)
>
> **Never guess or normalize model names.** Always copy-paste the exact identifier
> from the `opencode models` output. This applies to all steps that reference
> model names (steps 2, 3, 5, 6, 7, and 8).

Also read `opencode.jsonc` to collect **agent names and their roles** (from descriptions and `agents/*.md` files). Ignore current model assignments — those will be replaced.

### 2. Research Model Characteristics and Validate URLs

For each model listed in step 1, gather from provider documentation:

- **Cost per request** — from provider pricing pages
- **Requests per time window** — from rate limit docs
- **Speed/latency** — fast / normal / slow
- **Context window** — maximum input tokens
- **Best use case** — reasoning, coding, analysis, quick tasks, etc.

**Key sources per provider:**

- **opencode-go**: `https://opencode.ai/docs/go/#usage-limits`
- **opencode-zen**: `https://opencode.ai/docs/zen/#pricing`
- **GitHub Copilot (pricing)**: `https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing`
- **GitHub Copilot (multipliers)**: `https://docs.github.com/en/copilot/reference/copilot-billing/model-multipliers-for-annual-plans`
- **OpenRouter / Zen**: `https://openrouter.ai/models`
- **Other providers**: consult their official documentation

**URL Validation — REQUIRED:**

For every URL listed above that you navigate to:

1. If the page loads successfully → use it as-is.
2. If the page returns 404 or redirects to an unrelated page → search for the correct URL, then **update this SKILL.md** with the correct URL before continuing. This ensures future executions use the correct URL.

### 3. Classify Models

Assign each confirmed-available model a quality, cost and speed rating using **only** the data gathered in step 2.

**Quality scale** (based on popular consensus of model intelligence/capability):

- `   -` — Basic (entry-level or free models)
- `󰫣   ` — Good (capable models for most tasks)
- `󰫣󰫣  ` — Very good (strong reasoning and coding ability)
- `󰫣󰫣󰫣 ` — Excellent (top-tier models, best-in-class reasoning)

**Cost scale:**

- `Free` — Free tier (no quota cost)
- `   ` — Economic (highest requests per window, lowest cost per request)
- `  ` — Normal (balanced cost/performance)
- ` ` — Expensive (lowest requests per window, highest cost per request)

**Speed scale:**

- `-   ` — Unknown (no benchmark data available)
- `󱐋   ` — Slow (extended thinking, deep reasoning, high latency)
- `󱐋󱐋  ` — Normal (balanced speed)
- `󱐋󱐋󱐋 ` — Fast (low latency, quick responses)

### 4. Identify Agent Roles

Read each `agents/*.md` file and `opencode.jsonc` agent descriptions. For each agent, determine its role:

| Role archetype         | Needs                                     |
| ---------------------- | ----------------------------------------- |
| Reasoning/architecture | Deep thinking, extended context           |
| Implementation         | Precision, balanced speed                 |
| Quick tasks            | Fast, low latency                         |
| Large context analysis | High context window                       |
| Execution/terminal     | Reliable, fast, good at structured output |
| General purpose        | Balanced across all dimensions            |

### 5. Propose Optimized Assignments

Assign each agent a model from the step-1 list. Apply the **Priority Mode** from the top of this skill to determine the ordering of trade-offs.

**Default (`skill` mode) — Role fit → Cost → Speed:**

1. Find the model whose capabilities best match the agent's role archetype (step 4)
2. Among models equally suited to the role, prefer the cheaper one
3. Among equally cheap models, prefer the faster one

**`price` mode — Cost → Role fit → Speed:**

1. Start with the cheapest models and work up
2. Among equally cheap models, pick the one that best fits the role
3. Among equally good fits at the same price, prefer the faster one

**`speed` mode — Speed → Role fit → Cost:**

1. Start with the fastest models
2. Among equally fast models, pick the one that best fits the role
3. Among equally good fits at the same speed, prefer the cheaper one

**All modes — non-negotiable constraints:**

- **No duplicate models** — each agent must use a unique model
- **Only models from step 1** — never assign a model not confirmed available
- **No assignment left blank** — every agent must have a model
- **Exact identifier match** — model names must be copied verbatim from step 1 output, including all hyphens, dots, and version numbers. Never modify, normalize, or guess identifiers.

### 6. Create Audit Report

Write to `docs/agent-audits/YYYY-MM-DD.md`:

```markdown
# Agent Model Audit — YYYY-MM-DD

## Priority Mode

`skill` (role fit first)

## Providers Connected

| Provider    | Models Available | Notes                  |
| ----------- | ---------------- | ---------------------- |
| opencode-go | 12               | Go subscription active |

## Model Analysis

| Model             | Quality | Cost | Speed | Requests/5h | Best For         |
| ----------------- | ------- | ---- | ----- | ----------- | ---------------- |
| deepseek-v4-flash |        |     | 󱐋󱐋󱐋   | 31,650      | Quick tasks      |
| minimax-m2.5      |        |     | 󱐋󱐋󱐋   | 6,300       | Fast execution   |
| qwen3.5-plus      |        |     | 󱐋󱐋󱐋   | 10,200      | General tasks    |
| qwen3.6-plus      |       |    | 󱐋󱐋    | 3,300       | Balanced work    |
| deepseek-v4-pro   |       |    | 󱐋󱐋    | 3,450       | Reasoning        |
| minimax-m2.7      |       |    | 󱐋󱐋󱐋   | 3,400       | Fast refactoring |
| mimo-v2.5-pro     |       |   | 󱐋     | 1,290       | Precision coding |
| kimi-k2.6         |       |   | 󱐋     | 1,150       | Large context    |
| glm-5.1           |       |   | 󱐋     | 880         | Deep planning    |
| claude-sonnet-4-6 |      |   | 󱐋󱐋    | 1,000       | Top reasoning    |

## Proposed Assignments

| Agent   | Model             | Quality | Cost | Speed | Role Fit  | Rationale           |
| ------- | ----------------- | ------- | ---- | ----- | --------- | ------------------- |
| build   | qwen3.6-plus      |       |    | 󱐋󱐋    | Good      | Balanced for coding |
| z-spark | deepseek-v4-flash |        |     | 󱐋󱐋󱐋   | Excellent | Fast & cheap        |
| ...     | ...               | ...     | ...  | ...   | ...       | ...                 |

## Changes from Previous Config

- Assigned `z-forge` → `mimo-v2.5-pro` (precision coding, best role fit)
- Assigned `explore` → `minimax-m2.5` (fast exploration, lowest cost)
- Updated all agent descriptions with `[quality | cost | speed]` indicators

## Uniqueness Check

All agents use unique models: ✅
```

### 7. Update Configurations

All model assignments must come **exclusively** from models confirmed in step 1.

> **⚠️ CRITICAL:** Before writing any model identifier to `opencode.jsonc`,
> verify it character-for-character against the `opencode models` output from step 1.
> Common mistakes: replacing hyphens with dots (`claude-sonnet-4-6` → `claude-sonnet-4.6`)
> or vice versa. Always copy-paste, never type from memory.

**`opencode.jsonc`:**

- Set `agent.<name>.model` for every agent from the proposed assignments in step 6
- Set `agent.<name>.description` with `[quality | cost | speed]` prefix

**`agents/*.md`:**

- Do NOT add or modify `description` in agent `.md` frontmatter.
- The `description` field with `[quality | cost | speed]` indicators must ONLY exist in `opencode.jsonc`.
- Agent `.md` files contain the agent's behavioral instructions (mode, tools, system prompt).
- Duplicating descriptions in both places creates drift and confusion.

**Format:** `[quality | cost | speed] Description text`

- Quality padded to 4 chars: `󰫣`, `  `, ` `, ``
- Cost padded to 4 chars: `Free`, `   `, `  `, ` `
- Speed padded to 4 chars: `?  `, `󱐋  `, `󱐋󱐋 `, `󱐋󱐋󱐋`
- Example: `[ |   | 󱐋󱐋 ] Reasoning architect for decomposition and design decisions`
- ⚠️ Do not add a space between "Free" and "|" the expected format is: `[Free| ?  ]`

### 8. Verify

- No duplicate models across agents ✅
- All agent descriptions have `[quality | cost | speed]` indicators ✅
- All assigned models came from `opencode models` output ✅
- **All model identifiers match `opencode models` output character-for-character** ✅
- Audit report saved to `docs/agent-audits/YYYY-MM-DD.md` ✅
- `opencode.jsonc` is valid JSONC ✅

## Notes

- `docs/agent-audits/` should be gitignored (working documents, not committed)
- Config changes (`opencode.jsonc`) should be committed
- Agent `.md` files should only be committed if their behavioral content (mode, tools, system prompt) was modified — not for description changes
- Remind user to restart opencode after config changes
