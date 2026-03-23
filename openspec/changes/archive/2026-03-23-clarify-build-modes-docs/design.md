## Context

The docs were recently reorganized into Home, Manual, Examples, and Developer sections, with the first-time-user flow centered on Installation, Quickstart, and Project Structure. That flow currently teaches the default two-stage Compose path well, but it does not explain early enough that PeiDocker also supports stage-1-only usage and merged-build artifacts.

The mismatch is not conceptual only. The implementation already supports:

- omitting `stage_2` entirely
- building stage-1 and stage-2 separately with Compose
- generating merged artifacts with `pei-docker-cli configure --with-merged`

The current docs mention merged artifacts in isolated places, but they do not present the three modes as a coherent user choice. This is most likely to confuse first-time users, because the current quickstart and minimal example both imply that the two-stage path is the only normal workflow.

## Goals / Non-Goals

**Goals:**

- Make the three supported build modes visible in the first-time-user path before readers commit to the default quickstart.
- Establish consistent terminology that distinguishes:
  - stage-1-only configuration
  - default two-stage Compose workflow
  - merged-build workflow
- Provide at least one concrete, beginner-friendly runnable stage-1-only example and one concrete merged-build walkthrough.
- Keep the existing quickstart as the recommended default path while clearly marking it as one choice, not the only one.

**Non-Goals:**

- Change any runtime build behavior, CLI semantics, or configuration schema.
- Replace the default two-stage onboarding flow with a different default.
- Add a large CI cookbook for merged builds beyond a minimal beginner-facing walkthrough.
- Reorganize the entire examples section again.

## Decisions

### 1. Add a dedicated build-modes page under Getting Started

The primary documentation home for this topic will be a new page under `manual/getting-started/`, positioned before Quickstart in navigation.

Rationale:

- Choosing a build mode is a first-time-user onboarding decision.
- A Concepts-only placement is too late in the reading flow.
- A Quickstart-only placement would bury the taxonomy inside one workflow page.

Alternatives considered:

- Expand only `manual/concepts/two-stage-architecture.md`: rejected because the page title and location imply architecture background, not onboarding choice.
- Explain everything only in `manual/cli-reference.md`: rejected because CLI reference is not where first-time users look for workflow decisions.

### 2. Use a fixed three-mode taxonomy

The docs will consistently describe three modes:

- stage-1-only
- two-stage Compose
- merged build

The docs will explicitly avoid using “single-stage” as a synonym for merged build.

Rationale:

- “single-stage” is ambiguous today: it can mean “omit `stage_2`” or “use one `docker build` command”.
- First-time users need names that map cleanly to config shape and commands.

Alternatives considered:

- Keep using informal mixed terminology: rejected because it preserves the current confusion.

### 3. Keep Quickstart two-stage, but branch users early

The existing quickstart remains the default recommended path, but it will state clearly that it demonstrates the default two-stage Compose workflow and link to the build-modes page for stage-1-only and merged alternatives.

Rationale:

- The two-stage path is still the most representative default for the product.
- Replacing the quickstart would add churn without improving the common case.

Alternatives considered:

- Replace quickstart with a stage-1-only flow: rejected because it would underrepresent storage/runtime behavior that many users need.
- Put all three flows into one long quickstart: rejected because it would overwhelm first-time readers.

### 4. Represent stage-1-only as a runnable variant, not necessarily a whole new example ladder

Stage-1-only guidance will be concrete and runnable, but it does not need to force a full renumbering of the basic examples. The simplest acceptable representation is a runnable minimal config variant plus build/run commands, linked from the new build-modes page and from the existing minimal example.

Rationale:

- First-time users need a concrete path, not just abstract prose.
- A forced renumbering of the examples set is avoidable churn.

Alternatives considered:

- Add a new numbered example before `01 Minimal SSH`: rejected because it would create numbering churn across docs and links.
- Document stage-1-only only as prose: rejected because it would still feel theoretical.

### 5. Treat merged build as a workflow variant, not a separate config family

Merged build docs will use an existing compatible config shape and focus on the workflow difference: `configure --with-merged`, generated artifacts, `build-merged.sh`, and `run-merged.sh`.

Rationale:

- Merged build is primarily a different build/run path, not a separate config model.
- Requiring a dedicated example directory for merged build would duplicate configs without adding much value.

Alternatives considered:

- Create a separate merged-only example config: rejected because it would duplicate the underlying YAML and blur the distinction between config model and build workflow.

### 6. Update supporting pages to reinforce mode awareness

The new build-modes page will be the canonical overview, but supporting pages will also be updated:

- `docs/index.md`
- `manual/getting-started/installation.md`
- `manual/getting-started/quickstart.md`
- `manual/getting-started/project-structure.md`
- `manual/concepts/two-stage-architecture.md`
- `manual/cli-reference.md`
- the minimal example and examples indexes/readmes

Rationale:

- Users enter the docs from multiple angles.
- The current confusion comes from repeated small assumptions, not from one missing paragraph.

## Risks / Trade-offs

- [Risk] Users still confuse stage-1-only with merged build if terminology drifts across pages. → Mitigation: introduce a single canonical three-mode table and reuse the same labels everywhere.
- [Risk] The getting-started section becomes too broad. → Mitigation: keep the new page short and decision-oriented; push details to existing quickstart, concept, and CLI pages.
- [Risk] Example coverage becomes uneven if stage-1-only is only a variant and not a full example page. → Mitigation: require a runnable config snippet plus exact commands, and link it from the minimal example.
- [Risk] Merged-build guidance grows into a separate guide anyway. → Mitigation: keep the first change scoped to a minimal walkthrough; add a dedicated guide later only if the page becomes too dense.

## Migration Plan

1. Add the new getting-started build-modes page and wire it into navigation.
2. Update the home and installation/quickstart entry points to route first-time users there.
3. Update concept/reference/supporting pages to use the same terminology and cross-links.
4. Add runnable stage-1-only and merged-build guidance.
5. Validate the docs build and check that the first-time-user reading path is coherent end-to-end.

## Open Questions

- Should the generated `PEI-DOCKER-USAGE-GUIDE.md` also be aligned in the same change, or can it follow later as a consistency cleanup?
- Should the build-modes page live as `build-modes.md` or `choosing-a-build-mode.md`?
- If the merged-build walkthrough grows, should it later split into its own guide under `manual/guides/`?
