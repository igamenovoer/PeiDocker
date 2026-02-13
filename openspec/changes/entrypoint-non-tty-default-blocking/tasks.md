## 1. Entrypoint Fallback Logic

- [ ] 1.1 Add TTY-aware default fallback logic to stage-1 entrypoint (`exec /bin/bash` for TTY, `exec sleep infinity` for non-TTY)
- [ ] 1.2 Add equivalent TTY-aware default fallback logic to stage-2 entrypoint in all no-command fallback branches
- [ ] 1.3 Preserve runtime command precedence and custom-entrypoint argument precedence while applying the new fallback

## 2. Tests and Verification

- [ ] 2.1 Add automated tests that assert both entrypoint scripts contain and use the non-TTY-safe fallback behavior
- [ ] 2.2 Add/adjust tests to verify runtime command passthrough behavior remains unchanged
- [ ] 2.3 Manually verify container behavior for interactive (`-it`) and non-interactive no-command runs

## 3. Documentation and Follow-up

- [ ] 3.1 Update relevant docs/comments to reflect non-TTY default blocking behavior
- [ ] 3.2 Run project checks (`pixi run test` and any targeted checks) and resolve issues introduced by this change
