# Neovim Integration Rules

At session start, invoke the `using-neovim` skill to configure editor-integrated behavior.

## Editor Interaction

When `vim_*` tools are available (Neovim MCP active), follow these rules:

- Prefer `neovim_vim_buffer` / `neovim_vim_edit` / `neovim_vim_buffer_save` over native `read` / `write` / `edit` tools.
- After any edit, call `neovim_vim_buffer_save` and leave the edited buffer focused in Neovim.
- When the user refers to "this line", "this file", or "here", call `neovim_vim_status` first to get the active buffer and cursor position.
- For any multi-file search, use `neovim_vim_grep` and then `neovim_vim_command :copen` to populate and show the quickfix list before making changes.
- When opening multiple related files, prefer `neovim_vim_window split` or `vsplit` to show them side by side.
- Always check LSP clients from `neovim_vim_status` (look at `lspInfo` field) before reasoning about symbols, diagnostics, or references.
- **Before any edit operation:** verify the target buffer is active and modifiable via `neovim_vim_status`. If the wrong buffer is active or it's `nomodifiable`, switch buffers or run `:set modifiable` before editing.
