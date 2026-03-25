# PeiDocker v2.0.0 Release Notes

## Release Overview

PeiDocker v2.0.0 is a major release that consolidates the work done since
`v1.2.7` into a cleaner examples layout, a rewritten documentation structure,
more consistent installer behavior, safer runtime entrypoint behavior, and
automatic verification of the packaged basic examples.

## Highlights

- Reorganized packaged examples into structured `basic/` and `advanced/`
  catalogs in both the repository and the packaged assets.
- Rewrote the documentation structure around a clearer manual, examples index,
  and developer internals sections.
- Added automatic verification for the packaged basic examples, including
  Docker-backed runtime checks and docs/example parity tests.
- Improved environment variable handling, including compose-time passthrough
  support and clearer separation between configure-time and compose-time
  substitution.
- Migrated canonical installer implementations toward stage-1 system scripts,
  with stage-2 wrappers clarified and aligned.
- Hardened runtime entrypoint behavior and expanded functional coverage around
  startup behavior and non-interactive execution.

## Breaking and Migration Notes

- Example locations changed. If you previously relied on the old flat example
  files under `src/pei_docker/examples/*.yml`, use the structured examples
  under `examples/basic/`, `examples/advanced/`, and the packaged copies under
  `src/pei_docker/examples/basic/` and `src/pei_docker/examples/advanced/`.
- Compose-time environment passthrough is now an explicit part of the config
  model. Use `${...}` for configure-time substitution and `{{...}}` for
  compose-time passthrough semantics.
- Canonical installer implementations now live primarily under
  `stage-1/system/...`. If you maintained custom references to stage-2 system
  installer paths, review them and prefer the stage-1 canonical scripts where
  applicable.
- The docs navigation and page layout changed substantially. If you linked to
  older monolithic docs pages, update your links to the current pages under
  `docs/manual/`, `docs/examples/`, and `docs/developer/`.

## Validation Summary

This release was prepared against the release-triggered GitHub Actions PyPI
workflow and validated with the standard local quality gates. The packaged
basic examples now also have dedicated automatic verification coverage.

## Install / Upgrade

```bash
uv tool install pei-docker==2.0.0
# or
pip install pei-docker==2.0.0
```

## Older Releases

### v1.2.7

- Fixed `nvm` initialization in login shells so Node.js commands are available
  immediately.
- Added support for custom installer URLs and China mirrors.
- Simplified and refreshed parts of the documentation.

### v1.2.6

- Fixed entrypoint argument and variable handling issues.
- Added Bun-based agent installation and Bun installer support.
- Resolved GID conflicts for `ssh_users`.
- Added `unzip` to essential packages.
