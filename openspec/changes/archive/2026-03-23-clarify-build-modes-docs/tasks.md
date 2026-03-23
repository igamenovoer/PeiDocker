## 1. Navigation And Entry Points

- [x] 1.1 Add a new getting-started build-modes page to `mkdocs.yml` before Quickstart.
- [x] 1.2 Update `docs/index.md` to surface build-mode choice for first-time users.
- [x] 1.3 Update `docs/manual/getting-started/installation.md` so the next-step flow points users to build-modes guidance before or alongside Quickstart.

## 2. Core Build-Mode Onboarding

- [x] 2.1 Create `docs/manual/getting-started/build-modes.md` (or the chosen equivalent filename) with the three-mode taxonomy: stage-1-only, two-stage Compose, and merged build.
- [x] 2.2 Add a decision-oriented comparison to the build-modes page that distinguishes config shape, configure output, and build/run commands for each mode.
- [x] 2.3 Update `docs/manual/getting-started/quickstart.md` to state that it demonstrates the default two-stage Compose workflow and link to stage-1-only and merged-build alternatives.
- [x] 2.4 Update `docs/manual/concepts/two-stage-architecture.md` to explain how the two-stage model relates to stage-1-only usage and merged builds.
- [x] 2.5 Update `docs/manual/getting-started/project-structure.md` to explain which generated artifacts are specific to the default two-stage path versus merged artifacts or stage-1-only usage.
- [x] 2.6 Update `docs/manual/cli-reference.md` to frame `--with-merged` within the broader build-modes model, not as an isolated option.

## 3. Runnable Examples And Workflow Guidance

- [x] 3.1 Add runnable stage-1-only guidance using a minimal config or config variant that omits `stage_2` and shows configure/build/run/connect commands.
- [x] 3.2 Add concrete merged-build guidance showing `pei-docker-cli configure --with-merged`, the generated artifacts, and `build-merged.sh` / `run-merged.sh`.
- [x] 3.3 Update `docs/examples/basic/01-minimal-ssh.md` so it no longer implies the default two-stage layout is the only beginner path.
- [x] 3.4 Update `docs/examples/index.md` and `examples/README.md` to surface the availability of stage-1-only and merged-build guidance.
- [x] 3.5 Add or update cross-links so users entering through examples can discover the build-modes overview page.

## 4. Consistency And Validation

- [x] 4.1 Review the updated docs for consistent terminology: “stage-1-only”, “two-stage Compose”, and “merged build”.
- [x] 4.2 Verify that merged-build guidance mentions the passthrough-marker incompatibility.
- [x] 4.3 Run the docs build and confirm the first-time-user path is coherent from Home → Installation/Build Modes → Quickstart/Examples.
