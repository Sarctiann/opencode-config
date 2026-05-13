# Enable opencode provider - Design

Date: 2026-05-13

Summary
-------
Remove the `disabled_providers` configuration entry from the user's OpenCode configuration so the `opencode` provider is no longer disabled.

Motivation
----------
The user requested that the `opencode` provider be enabled by removing the disabling configuration. This is a minimal change to the configuration file that restores the default behavior for providers.

Approach
--------
1. Remove the `disabled_providers` key entirely from `opencode.jsonc`.
2. Keep the rest of the configuration unchanged.

Trade-offs
----------
- Removing the key is clean and avoids leaving an empty array or commented-out config.
- If the user later wants to preserve history, they can rely on the repo or local file history; no separate comment is added.

Verification
------------
1. Confirm the `opencode.jsonc` file no longer contains `disabled_providers`.
2. Restart or reload OpenCode if needed to pick up the configuration change.

Path
----
`/Users/sebastianrodriguezcapurro/.config/opencode/opencode.jsonc`
