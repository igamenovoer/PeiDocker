## Context

In the current config processor, `storage` and `mount` definitions are merged into a single map keyed by name. When a mount key matches a storage prefix (`app`, `data`, `workspace`), the resolver applies prefix-based destination rules and ignores explicit `dst_path`, producing incorrect container mount paths. The intended behavior is to treat storage and mount entries as distinct: name collisions are irrelevant, only destination path collisions matter.

Constraints: keep the user-facing config schema unchanged, preserve existing storage prefix behavior for `storage`, and avoid introducing GUI-only behavior differences.

## Goals / Non-Goals

**Goals:**
- Always honor explicit `mount.dst_path` regardless of mount key name.
- Treat `storage` and `mount` namespaces independently; only flag conflicts when resolved container `dst_path` collide.
- Provide clear, deterministic resolution rules for storage vs mount destinations.

**Non-Goals:**
- Introducing new config fields or breaking YAML formats.
- Changing storage prefix behavior for `storage` entries.
- Adding GUI features; any GUI impacts should be limited to reflecting the same resolution rules.

## Decisions

- **Separate resolution paths for storage vs mount:** Resolve `storage` destinations using prefix rules, and resolve `mount` destinations strictly from explicit `dst_path`. This avoids key-based conflicts entirely.
  - *Alternative considered:* Keep a merged map with metadata tags (source=storage/mount). Rejected as it adds complexity without user benefit.
- **Warn on destination conflicts, do not block:** If multiple entries resolve to the same container path, emit a warning using simple string matching but do not reject the configuration.
  - *Alternative considered:* Proactive conflict detection with explicit errors. Rejected to avoid duplicating Docker’s own validation and to reduce strictness.

## Risks / Trade-offs

- **[Risk]** Existing configs relying on name-based override behavior might now error on duplicate mount keys.
  → **Mitigation:** Provide a clear error message and keep rules deterministic; update docs/specs to clarify duplicate handling.
- **[Risk]** Warning-only detection could be missed or ignored.
  → **Mitigation:** Make warning messages explicit about the conflicting destination paths.
- **[Risk]** GUI adapter assumptions about prefix behavior could become inconsistent.
  → **Mitigation:** Ensure GUI conversions (if any) treat mount destinations explicitly and do not infer by name.
