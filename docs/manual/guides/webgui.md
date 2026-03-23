# Web GUI

The Web GUI is part of the repository, but the current `pei-docker-gui` command exits with a deprecation message in 2.0. This page documents the interface model that still exists in the codebase and the YAML mapping it was designed to edit.

## Current Status

```bash
pei-docker-gui --help
```

Today this reports that the Web GUI is deprecated and unavailable. Treat the GUI as a paused interface, not a supported workflow.

## Intended Launch Modes

Historically the launcher supported:

- Browser mode with an auto-selected port
- `--project-dir` to load or initialize a project
- `--jump-to-page` for a specific tab
- `--native` for a desktop window via `pywebview`

## Tab To YAML Mapping

| GUI tab | Main YAML sections |
| --- | --- |
| Project | `stage_1.image`, `stage_2.image` |
| SSH | `stage_1.ssh` |
| Network | `stage_1.proxy`, `stage_1.apt`, `stage_1.ports`, `stage_2.ports` |
| Environment | `stage_1.environment`, `stage_2.environment` |
| Storage | `stage_2.storage`, `stage_1.mount`, `stage_2.mount` |
| Scripts | `stage_1.custom`, `stage_2.custom` |
| Summary | Read-only rollup before saving/configuring |

## What The GUI Was Good At

- Tab-by-tab editing of the config model
- Keeping stage-1 and stage-2 fields separate
- Visual SSH user editing
- Storage type selection without hand-editing YAML

## Practical Recommendation

Use the CLI plus the docs in this manual today. If GUI work resumes, the mapping above is the anchor for understanding how the existing codebase models the form state.
