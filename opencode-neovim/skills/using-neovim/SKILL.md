---
name: using-neovim
description: Use when the neovim MCP is available, or when the user mentions neovim, opening/closing/reading files in an editor, buffer navigation, text editing via editor, or any interaction with a text editor integrated session.
---

# Using Neovim MCP

## Overview

When the `neovim` MCP server is available, Neovim IS the primary user interface. Treat it as the canonical view of the user's workspace: always reflect changes there, open relevant files for context, and leverage Vim-native features (quickfix, LSP, marks, etc.) for a seamless editing experience.

## Detecting Neovim MCP Availability

At session start, call `neovim_vim_health` or `neovim_vim_status`. If it succeeds, the Neovim MCP is active — follow this skill for all file and editor interactions.

If it fails or the tool is absent, fall back to standard file tools.

## Core Principle

> **Every meaningful action should be visible in Neovim.**

After any edit, open, or navigation: leave the buffer focused so the user sees the result immediately.

---

## Tools Quick Reference

| Tool | MCP Name | Purpose |
| ---- | -------- | ------- |
| `vim_status` | `neovim_vim_status` | Current buffer, cursor, mode, LSP clients, window layout |
| `vim_buffer` | `neovim_vim_buffer` | Read buffer contents (optionally by filename) |
| `vim_buffer_switch` | `neovim_vim_buffer_switch` | Switch to buffer by name or number |
| `vim_buffer_save` | `neovim_vim_buffer_save` | Save current or named buffer |
| `vim_file_open` | `neovim_vim_file_open` | Open a file into a new buffer |
| `vim_edit` | `neovim_vim_edit` | Insert / replace / replaceAll lines |
| `vim_command` | `neovim_vim_command` | Run any Vim command (`:norm`, `:e`, `:bd`, `!shell`) |
| `vim_search` | `neovim_vim_search` | Regex search within current buffer |
| `vim_search_replace` | `neovim_vim_search_replace` | Find-and-replace in current buffer |
| `vim_grep` | `neovim_vim_grep` | Project-wide vimgrep → populates quickfix list |
| `vim_window` | `neovim_vim_window` | Split, vsplit, close, navigate windows |
| `vim_register` | `neovim_vim_register` | Set register content |
| `vim_macro` | `neovim_vim_macro` | Record / stop / play macros |
| `vim_tab` | `neovim_vim_tab` | Tab management (new, close, next, prev…) |
| `vim_fold` | `neovim_vim_fold` | Code folding (create/open/close/delete/toggle) |
| `vim_jump` | `neovim_vim_jump` | Jump list navigation (back/forward/list) |
| `vim_health` | `neovim_vim_health` | Connection health check |

**Note:** `vim_mark` and `vim_visual` are BROKEN (MCP server bug with type coercion). Use `vim_command` equivalents instead (see below).

---

## ⚠️ Known Issues

### `vim_edit` — Buffer Must Be Active and Modifiable

`neovim_vim_edit` fails with E21 ("Cannot make changes, 'modifiable' is off") on:
- OpenCode's UI buffer (always `nomodifiable`)
- Buffers opened as read-only
- Buffers in terminal mode

**Fix:** Before editing:
1. Verify target buffer is active via `neovim_vim_status` (check `fileName` field)
2. If wrong buffer: `neovim_vim_buffer_switch` to target
3. If `nomodifiable`: `neovim_vim_command(":set modifiable")`

### `vim_edit` replaceAll — Only Works on Active Buffer

`replaceAll` mode silently fails when the target buffer is not the active buffer. Use `replace` mode instead for targeted line replacement.

### `vim_mark` and `vim_visual` — BROKEN

The MCP server has type coercion bugs: it sends `column` as string where Vim expects number. Use `vim_command` equivalents instead.

### `vim_grep` — E480 When No Matches

If the search pattern has no matches, Vim returns error E480. This is expected behavior. Handle gracefully in code.

### `vim_fold` openall/closeall — Fails in Terminal Mode

`neovim_vim_fold` with action `openall` or `closeall` fails with "Can't re-enter normal mode from terminal mode". Use `vim_command` equivalents instead.

---

## `vim_command` Equivalents for Broken Tools

| Tool | `vim_command` Equivalent |
| ---- | ------------------------ |
| `vim_mark` (set mark 'a' at line 5, col 3) | `:call cursor(5, 3)` then `:normal ma` |
| `vim_visual` (select lines) | `:call cursor(startLine, startCol)` then `:normal v` + cursor movement |
| `vim_fold` openall | `:normal! zR` |
| `vim_fold` closeall | `:normal! zM` |

---

## Edit Protocol (Canonical Workflow)

**Always follow this sequence for any edit operation:**

1. `neovim_vim_status` → confirm `fileName` matches target and `mode` is normal
2. If wrong buffer → `neovim_vim_buffer_switch` to target by name or number
3. If `nomodifiable` → `neovim_vim_command(":set modifiable")`
4. `neovim_vim_buffer` → read current content (always refresh before editing)
5. `neovim_vim_edit` with `replace` mode at the correct `startLine`
6. `neovim_vim_buffer_save` → persist
7. `neovim_vim_buffer` → verify edit applied correctly

**Never edit a buffer you haven't first read and confirmed is active.**

---

## Interaction Patterns

### "What's happening on line X?"

1. `neovim_vim_status` → get active filename and cursor.
2. `neovim_vim_buffer` (no arg) → read current buffer.
3. Use LSP info from `neovim_vim_status` (attached clients) to reason about diagnostics if needed.
4. Respond with context from that file.

### "Modify / fix X"

1. Follow the Edit Protocol above.
2. Leave focus on the edited buffer.

### "Search and replace all references to Y"

1. `neovim_vim_grep` pattern → populates quickfix list (user sees all matches).
2. For buffer-local replace: `neovim_vim_search_replace` with pattern and replacement.
3. For project-wide replace: iterate quickfix results, open each buffer, apply replacement, save.
4. Prefer `vim_grep` first — it improves UX by showing the quickfix list before changes.

### "Open files related to Z"

1. Use `neovim_vim_grep` or existing knowledge to find relevant files.
2. `neovim_vim_file_open` for each file.
3. Use `neovim_vim_window split` / `vsplit` to show multiple files simultaneously when relevant.
4. Call `neovim_vim_status` after to confirm layout.

### "Go to / navigate to X"

- Use `neovim_vim_command` with `:e filename`, `:b bufname`, or `:tag symbol`.
- Use `neovim_vim_jump` for back/forward in jump list.
- Use `neovim_vim_buffer_switch` for known buffer names.

### "Run a shell command"

- `neovim_vim_command` with `!command` prefix (only when `ALLOW_SHELL_COMMANDS=true`).
- Prefer native Vim commands when possible.

---

## LSP Integration

`neovim_vim_status` returns attached LSP clients via `lspInfo` field. If `lspInfo` is "LSP information unavailable", no LSP is attached. Use this to:

- Know which language server is active for the file type.
- Run LSP commands via `neovim_vim_command`: `:lua vim.lsp.buf.definition()`, `:lua vim.lsp.buf.references()`, etc.
- Populate quickfix with LSP diagnostics: `:lua vim.diagnostic.setqflist()`.

---

## Quickfix List — Prefer It for Multi-File Operations

The quickfix list improves discoverability. Always populate it when:

- Doing project-wide search (`neovim_vim_grep`).
- Collecting LSP references or diagnostics.
- Planning multi-file edits (user can navigate with `:cn` / `:cp`).

Open quickfix after populating: `neovim_vim_command(":copen")`.

---

## Common Mistakes

| Mistake | Fix |
| ------- | --- |
| Editing a file with Write tool instead of `vim_edit` | Always use `neovim_vim_edit` + `neovim_vim_buffer_save` when Neovim MCP is active |
| Not opening the file after editing | Call `neovim_vim_file_open` or `neovim_vim_command :e` so user sees the result |
| Skipping quickfix for project-wide ops | Use `neovim_vim_grep` first, then open quickfix |
| Assuming buffer = disk file | Call `neovim_vim_buffer_save` explicitly after edits |
| Ignoring LSP clients | Check `neovim_vim_status` for `lspInfo` before reasoning about code symbols |
| Editing without verifying buffer is active | Follow the Edit Protocol above |
