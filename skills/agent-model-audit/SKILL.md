---
name: agent-model-audit
description: Use when auditing agent models, reviewing provider offerings, optimizing model assignments by cost and speed, or updating agent descriptions with cost/speed indicators. Trigger keywords: "audit agents", "audit models", "update agent models", "review models", "optimize agents".
---

# Agent Model Audit

Audit connected providers, analyze model offerings (cost, speed, usage limits), and optimize agent-to-model assignments. Produces a dated audit report and updates agent configurations.

## Workflow

### 1. Discover Connected Providers

Run `/providers` in the TUI or check `opencode.jsonc` for configured providers. Identify which providers are active (not in `disabled_providers`).

For each active provider, list available models using `/models` or the provider's model endpoint.

### 2. Research Model Characteristics

For each model in use or under consideration, gather:

- **Cost per request** — from provider documentation or usage dashboards
- **Requests per time window** — from rate limit docs (e.g., opencode Go: requests per 5h/week/month)
- **Speed/latency** — from benchmarks or provider docs (fast/normal/slow)
- **Context window** — maximum input tokens
- **Best use case** — reasoning, coding, analysis, quick tasks, etc.

Key sources:
- opencode Go: `https://opencode.ai/docs/es/go/#usage-limits`
- Provider docs for other providers

### 3. Classify Models

Assign each model a cost and speed rating:

**Cost scale:**
- `$   ` — Economic (highest requests per window, lowest cost per request)
- `$$  ` — Normal (balanced cost/performance)
- `$$$ ` — Expensive (lowest requests per window, highest cost per request)
- `Free` — Free tier models

**Speed scale:**
- `!  ` — Slow (extended thinking, deep reasoning, high latency)
- `!! ` — Normal (balanced speed)
- `!!!` — Fast (low latency, quick responses)

### 4. Analyze Current Agent Assignments

Read `opencode.jsonc` agent block and each `agents/*.md` file. For each agent:

- Note current model assignment
- Check for duplicate models across agents
- Evaluate if the model matches the agent's role

### 5. Propose Optimizations

Apply these principles:

- **No duplicate models** — Each agent should use a unique model when possible
- **Role-model fit** — Match model strengths to agent responsibilities:
  - Reasoning/architecture → Deep thinking models (`!` speed, `$$-$$$` cost)
  - Implementation → Balanced models (`!!` speed, `$$` cost)
  - Quick tasks → Fast models (`!!!` speed, `$` cost)
  - Large context analysis → High context window models
  - Execution/terminal → Reliable, fast models
- **Budget awareness** — Distribute expensive models only where needed

### 6. Create Audit Report

Write to `docs/agent-audits/YYYY-MM-DD.md`:

```markdown
# Agent Model Audit — YYYY-MM-DD

## Providers Connected

| Provider | Models Available | Notes |
|----------|-----------------|-------|
| opencode-go | 12 | Go subscription active |

## Model Analysis

| Model | Cost | Speed | Requests/5h | Best For |
|-------|------|-------|-------------|----------|
| deepseek-v4-flash | $ | !!! | 31,650 | Quick tasks |
| minimax-m2.5 | $ | !!! | 6,300 | Fast execution |
| qwen3.5-plus | $ | !!! | 10,200 | General tasks |
| qwen3.6-plus | $$ | !! | 3,300 | Balanced work |
| deepseek-v4-pro | $$ | !! | 3,450 | Reasoning |
| minimax-m2.7 | $$ | !!! | 3,400 | Fast refactoring |
| mimo-v2.5-pro | $$$ | ! | 1,290 | Precision coding |
| kimi-k2.6 | $$$ | ! | 1,150 | Large context |
| glm-5.1 | $$$ | ! | 880 | Deep planning |

## Current Assignments

| Agent | Model | Cost | Speed | Role Fit |
|-------|-------|------|-------|----------|
| build | qwen3.6-plus | $$ | !! | Good |
| z-spark | deepseek-v4-flash | $ | !!! | Excellent |
| ... | ... | ... | ... | ... |

## Changes Made

- Changed `z-forge` from `qwen3.6-plus` to `mimo-v2.5-pro` (eliminate duplicate, better precision)
- Changed `explore` from `kimi-k2.6` to `minimax-m2.5` (eliminate duplicate, faster for exploration)
- Updated agent descriptions with `[cost | speed]` indicators (padded to fixed width)

## Uniqueness Check

All agents now use unique models: ✅
```

### 7. Update Configurations

**opencode.jsonc:**
- Update `agent.<name>.model` for changed assignments
- Add/update `agent.<name>.description` with `[cost | speed]` prefix

**agents/*.md:**
- Update frontmatter `description:` with `[cost | speed]` prefix
- Keep existing description text after the indicator

Format: `[cost | speed] Original description text` where cost is padded to 3 chars and speed to 3 chars, e.g., `[$$  | !! ]` or `[$   | !!!]`.

### 8. Verify

- No duplicate models across agents
- All agent descriptions have indicators
- Audit report saved
- Config is valid JSON/JSONC

## Notes

- `docs/agent-audits/` should be gitignored (working documents)
- Actual config changes (`opencode.jsonc`, `agents/`) should be committed
- Remind user to restart opencode after config changes
