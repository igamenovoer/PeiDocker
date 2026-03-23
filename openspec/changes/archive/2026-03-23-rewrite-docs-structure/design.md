## Context

PeiDocker's current `docs/` is a flat directory with 10 markdown files mixing user guides, developer internals, and examples. The project has 19 curated system scripts, a two-stage architecture, 4 storage types, environment variable substitution with two modes, SSH multi-user support, GPU configuration, proxy handling, and a web GUI — most of which are undocumented or only documented in source-tree READMEs invisible to users.

The `context/` directory contains 280+ files of developer knowledge that is entirely separate from user-facing docs. The `openspec/specs/` directory has 14 formal specifications that document internal contracts but aren't accessible to contributors.

The existing example configs in `src/pei_docker/examples/` (20 YAML files) are functional but have no narrative explanation.

## Goals / Non-Goals

**Goals:**
- Restructure docs/ into three audience-oriented sections: manual/ (users), developer/ (contributors), examples/ (learners)
- Provide a progressive learning path: install → quickstart → concepts → basic examples → guides → advanced examples
- Document all 19 curated system scripts with parameters, usage patterns, and gotchas
- Create scenario-driven advanced examples ("I want to do X") that show multi-feature composition
- Include troubleshooting content covering known issues and common errors
- Maintain a navigable index page that routes users by audience and intent

**Non-Goals:**
- Changing the static site generator or hosting setup (keep current GitHub Pages / .nojekyll approach)
- Modifying README.md or other root-level files (can be a follow-up)
- Writing API docs or auto-generating documentation from code
- Creating video tutorials or interactive content
- Documenting the web GUI's internal implementation (that's developer/ territory, not webgui usage)
- Translating documentation to other languages

## Decisions

### 1. Three-section structure: manual/ + developer/ + examples/

**Choice**: Separate directories by audience rather than by topic.

**Rationale**: A user looking for "how to configure SSH" and a developer looking for "how SSH config processing works" need fundamentally different documents. Audience separation prevents the common problem of docs that are too technical for users and too shallow for developers.

**Alternatives considered**:
- Single flat directory with naming conventions (e.g., `user-ssh.md`, `dev-ssh.md`) — doesn't scale, hard to navigate
- Topic-based directories (e.g., `ssh/user.md`, `ssh/developer.md`) — fragments the reading path within each audience

### 2. Dual structure: runnable examples + narrative docs

**Choice**: Every example exists in two places:
- `examples/<slug>/user_config.yml` — the runnable, validated config (source of truth)
- `docs/examples/{basic,advanced}/<slug>.md` — narrative markdown with embedded YAML, workflow steps, and explanation

The doc page embeds the YAML from the runnable config (copy or reference), annotates it, and adds the full workflow (create → configure → build → run → verify).

**Rationale**: User chose Option A (embedded YAML in docs) but also requires that examples are actually correct and runnable. The dual structure achieves both: docs are self-contained for reading, while `examples/` provides copy-and-run configs that can be validated in CI. The runnable config is the single source of truth — if it doesn't pass `configure`, the example is broken.

**Alternatives considered**:
- Docs-only with no runnable counterpart — impossible to validate correctness programmatically
- Runnable-only with README per example (Option B) — worse reading experience on a docs site
- Symlinks from docs to examples — fragile, not portable across platforms

### 3. Repo-root `examples/` replaces `src/pei_docker/examples/`

**Choice**: Create a top-level `examples/` directory at repo root, organized by slug name. The existing `src/pei_docker/examples/legacy/` and `src/pei_docker/examples/envs/` content is migrated into this new structure.

**Directory layout**:
```
examples/
├── README.md                    ← index with links to docs
├── basic/
│   ├── minimal-ssh/
│   │   └── user_config.yml
│   ├── gpu-container/
│   │   └── user_config.yml
│   ├── host-mount/
│   │   └── user_config.yml
│   ├── docker-volume/
│   │   └── user_config.yml
│   ├── custom-script/
│   │   ├── user_config.yml
│   │   └── my-setup.sh         ← supporting files if needed
│   ├── port-mapping/
│   │   └── user_config.yml
│   ├── proxy-setup/
│   │   └── user_config.yml
│   ├── env-variables/
│   │   └── user_config.yml
│   ├── env-passthrough/
│   │   └── user_config.yml
│   ├── pixi-environment/
│   │   └── user_config.yml
│   ├── conda-environment/
│   │   └── user_config.yml
│   ├── multi-user-ssh/
│   │   └── user_config.yml
│   └── apt-mirrors/
│       └── user_config.yml
└── advanced/
    ├── ml-dev-gpu/
    │   └── user_config.yml
    ├── web-dev-nodejs/
    │   └── user_config.yml
    ├── team-dev-environment/
    │   └── user_config.yml
    ├── china-corporate-proxy/
    │   └── user_config.yml
    ├── ros2-robotics/
    │   └── user_config.yml
    └── vision-opengl/
        └── user_config.yml
```

**Rationale**: Top-level `examples/` is the conventional location for example configs (visible in repo root, easy to discover). Slug-based subdirectories allow each example to carry supporting files (custom scripts, .env files) alongside the config. The existing `src/pei_docker/examples/legacy/` naming suggests those examples were already considered outdated.

**Migration mapping from existing examples**:
| Existing file | New location |
|---|---|
| `legacy/minimal-ubuntu-ssh.yml` | `basic/minimal-ssh/user_config.yml` |
| `legacy/gpu-with-host-mount.yml` | adapted into `basic/gpu-container/` + `basic/host-mount/` |
| `legacy/pixi-basic-cpu.yml` | `basic/pixi-environment/user_config.yml` |
| `legacy/pixi-ml-gpu.yml` | `advanced/ml-dev-gpu/user_config.yml` |
| `envs/01-no-passthrough.yml` | `basic/env-variables/user_config.yml` |
| `envs/02-with-passthrough.yml` | `basic/env-passthrough/user_config.yml` |
| `envs/03-advanced-env-handling.yml` | adapted into advanced example |
| Other legacy configs | absorbed into relevant basic/advanced examples |

### 4. Example validation deferred

**Choice**: Runnable verification of example configs (passing `pei-docker-cli configure`, building images) is explicitly out of scope for this change. The focus is on writing correct documentation. Validation will be a follow-up change.

**Rationale**: Keeps this change focused on documentation structure and content. Configs should be written with best effort correctness based on existing legacy examples and the config schema, but systematic validation adds scope without improving the docs reading experience.

### 5. Standard base images for examples

**Choice**: All examples use these base images (confirmed available on the host):
- **Non-GPU**: `ubuntu:24.04` (78MB, already pulled)
- **GPU**: `nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04` (available via mirror)

**Rationale**: Using consistent base images across all examples avoids confusion and ensures reproducibility. `ubuntu:24.04` is the latest LTS and is lightweight. `nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04` matches what the existing `pixi-ml-gpu.yml` legacy example uses and is confirmed present on the host system. Examples that don't demonstrate GPU should always use `ubuntu:24.04`.

### 6. Embedded YAML in docs (Option A) — with source-of-truth reference

**Choice**: Doc example pages embed the YAML inline for reading, but note the source file path (e.g., "Source: `examples/basic/minimal-ssh/user_config.yml`") so readers can copy the runnable version.

**Rationale**: User chose Option A for the docs reading experience. The embedded YAML keeps docs self-contained — readers don't need to leave the page. The source path reference connects them to the validated runnable config when they want to actually use it.

**Alternatives considered**:
- Option B: Separate `user_config.yml` + `README.md` per example in docs — worse reading experience on docs site (now moot since runnable configs live in `examples/` separately)

### 7. Basic examples: numbered single-feature progression

**Choice**: Basic examples are numbered (01–13+), each demonstrating exactly one feature with the minimal config needed.

**Rationale**: Numbered ordering creates a natural curriculum. Single-feature focus means each example is a building block that readers combine in advanced examples. Minimal configs reduce cognitive load — the reader sees only what matters for that feature.

### 8. Advanced examples: scenario-driven "I want to..."

**Choice**: Advanced examples are framed as user goals/scenarios, each composing multiple features.

**Rationale**: Real users don't think in features — they think in goals. "I want a GPU ML dev environment" naturally leads to combining GPU + pixi + storage + SSH. This framing also serves as an integration test for the documentation: if a scenario can't be clearly explained by combining concepts from manual/, the concepts docs need improvement.

### 9. Script catalog: individual pages for complex scripts, grouped page for simple ones

**Choice**: Complex scripts (pixi, conda, ssh, ros2, proxy, opengl, opencv) get individual pages. Simple single-installer scripts (nodejs, bun, uv, clang, firefox, ngc, litellm, claude-code, codex-cli, magnum, vision-dev) are grouped into a `simple-installers.md` page.

**Rationale**: Complex scripts have parameters, configuration patterns, and gotchas that warrant dedicated pages. Simple scripts that are essentially "install X" with minimal params don't need a full page each — a catalog table with brief notes is more efficient for readers.

### 10. Developer docs sourced from openspec/ and context/

**Choice**: Developer docs are written fresh in `docs/developer/` but draw content from existing `openspec/specs/` and `context/design/` files. The openspec specs and context directory remain as-is (they serve different purposes).

**Rationale**: openspec specs are formal contracts (SHALL/MUST language, scenarios). Developer docs need narrative explanation of architecture and rationale. The developer docs reference and summarize specs rather than duplicating them.

### 11. Clean wipe of existing docs/

**Choice**: All existing content in `docs/` is deleted before writing new docs. This is a clean rewrite, not a migration — no content from existing files needs to be preserved or absorbed.

**Rationale**: The existing docs are not good for user reading (the motivation for this change). Attempting to migrate content would constrain the new structure and carry forward the problems we're trying to fix. The diagram assets in `docs/internals-diagrams/` may be re-used in `docs/developer/diagrams/` if still accurate, but are not required.

## Risks / Trade-offs

**[Large scope]** → Mitigate by implementing in phases: structure first, then manual/, then examples/, then developer/. Each phase produces usable documentation independently.

**[Stale system script docs]** → Script pages may fall out of sync as scripts evolve. Mitigate by keeping script docs minimal (params + usage pattern + link to source) rather than duplicating implementation details.

**[Broken external links]** → Any bookmarks or external references to current docs/ paths will break. Acceptable since existing content is being discarded entirely — a clean break is intentional.

**[Maintenance burden]** → More files means more to maintain. Mitigate by keeping docs DRY — concepts are explained once in manual/concepts/ and referenced from examples and guides rather than repeated.

**[Docs/config drift]** → Embedded YAML in doc pages may drift from the runnable `examples/` configs over time. Mitigate by establishing `examples/` as the single source of truth and adding a note in each doc page pointing to the runnable config path. A CI check comparing doc YAML blocks to actual config files could be added later.

**[Legacy example migration]** → Some legacy configs (e.g., `gpu-with-opengl-win32.yml`, `with-everything.yml`) may not map cleanly to the new structure. Mitigate by absorbing useful content rather than forcing 1:1 migration — not every legacy config needs a direct successor.
