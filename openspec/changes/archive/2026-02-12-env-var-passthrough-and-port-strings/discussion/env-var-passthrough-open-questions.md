## Env Var Handling: Open Questions / Decisions

This note captures open questions discovered while designing support for:

- **config-time env substitution** via `${VAR}` / `${VAR:-default}` (expanded during `pei-docker-cli configure`)
- **compose-time env passthrough** via `{{VAR}}` / `{{VAR:-default}}` (preserved through parsing and emitted as Docker Compose `${...}`)

### 1) What should happen if `${...}` survives config-time substitution?

Today, `process_config_env_substitution` expands `${VAR}` only if `VAR` is set; otherwise it leaves `${VAR}` in the config. That leftover `${...}` later trips OmegaConf interpolation during `OmegaConf.to_container(..., resolve=True)`.

Decision needed:
- Error early with a clear message (“use `{{VAR}}` for passthrough, or define VAR at configure time”), or
- Attempt to treat `${...}` as literal strings (requires escaping/rewrite), or
- Allow `${...}` only in certain places (complex).

Recommended default: **early, friendly error** when `${...}` remains in user config after substitution.

#### Decision
- Error if any `${...}` patterns remain after config-time substitution, with a clear message guiding users to use `{{...}}` for passthrough or set the variable at configure time. This avoids silent confusion and ensures users understand the two modes clearly.

### 2) Which outputs are in-scope for passthrough?

Compose-time passthrough only works in artifacts interpreted by Docker Compose.

Decision needed:
- Guarantee support only for `docker-compose.yml` initially, or extend to:
  - `compose-template.yml`
  - merged build outputs (`merged.env`, `build-merged.sh`, `merged.Dockerfile`)
  - `_etc_environment.sh` (baked into `/etc/environment` in-container)

Recommended default: guarantee only `docker-compose.yml` initially; treat other outputs as out of scope unless explicitly added.

#### Decision
- as recommended: guarantee passthrough support only for `docker-compose.yml` in the initial implementation. 
- prevent the usage of `--with-merged` with passthrough markers (error if detected) to avoid confusion about which outputs support passthrough, warn the user that support for merged outputs may be added in the future, and document the current scope clearly.
- explicitly disallow passthrough markers in baked envs (error if detected) to avoid silent confusion about unsupported contexts.

#### Revised Decision
- **Passthrough markers are allowed only in values that are interpreted by Docker Compose** (i.e., values that end up in the generated `docker-compose.yml`).
- **Passthrough markers are not allowed in values that PeiDocker writes directly into internal scripts/files** where Docker Compose has no opportunity to expand them, specifically:
  - any config values consumed by `installation/stage-{1,2}/internals/**` scripts without going through Docker Compose substitution, and
  - any config values baked into PeiDocker-generated scripts during `configure` in a way that Docker Compose cannot influence.
  In those contexts, users should use shell-native `$VAR` handling and defaults inside the script itself.
- `_etc_environment.sh` is always generated, but it is only *used* when baking is enabled. Therefore:
  - allow `{{...}}` in `stage_?.environment` generally (because it becomes compose env),
  - but **error if baking is requested** (`PEI_BAKE_ENV_STAGE_*` is true) and any passthrough markers would be written into `/etc/environment`.

### 3) Where should `{{...}} → ${...}` conversion occur?

Options:
- Post-process the emitted YAML text (`OmegaConf.to_yaml` output) and rewrite `{{...}}` sequences.
- Walk the final compose object (dict/tree) and rewrite values before YAML emission.

Trade-off:
- Text post-process is simplest but can affect any string in the YAML output (including unexpected places).
- Tree-walk is more structured but requires a traversal implementation.

#### Decision
- Using tree-walk approach to rewrite `{{...}}` to `${...}` in the final compose object before YAML emission. This method is more structured and reduces the risk of unintended replacements in unrelated parts of the YAML output.

**Note / doubt:** Be careful rewriting into an `OmegaConf.DictConfig`. `${...}` is also OmegaConf interpolation syntax, and if `${...}` ends up inside an OmegaConf object that later goes through any `resolve=True` / `to_container(resolve=True)` / interpolation resolution step, it can error (e.g., `InterpolationKeyError`). Prefer one of:

- Tree-walk rewrite on a *plain Python container* (convert compose to `dict`/`list` first), then YAML-emit from that container, or
- Post-process the final YAML text output (with strict validation) after `OmegaConf.to_yaml`, if we can ensure we only touch intended value strings.

#### Revised Decision
- OmegaConf resolution is a **one-way path**: perform all `OmegaConf` resolution steps first.
- Then tree-walk rewrite on a *plain Python container* (convert compose to `dict`/`list` first) and emit YAML from that container.
- Avoid placing `${...}` back into a `DictConfig` that might be resolved again.

### 4) How strict should `{{...}}` validation be?

We only intend to support:
- `{{VAR}}`
- `{{VAR:-default}}`

Open questions:
- Variable name charset: `[A-Za-z_][A-Za-z0-9_]*` only?
- Allow whitespace like `{{ VAR }}`?
- Allow `default` to contain braces, newlines, or other special chars?

Recommended default: strict parse + clear error on malformed markers (avoid silent corruption).

#### Decision
- As recommended: implement strict validation for `{{...}}` markers, allowing only the forms `{{VAR}}` and `{{VAR:-default}}` where `VAR` matches the regex `[A-Za-z_][A-Za-z0-9_]*`. 
- Allow whitespace inside the braces (e.g., `{{ VAR }}`) for user convenience, but trim it during processing.
- Treat the default portion opaquely (do not parse its internal syntax), but disallow the terminator `}}` inside defaults to keep parsing unambiguous.

**Note / doubt:** Docker Compose variable substitution does **not** recursively expand nested substitutions inside defaults in the way users may expect. Keep defaults simple and literal when possible.

#### Revised Decision
- As recommended, we just pass what user gives us to the docker compose output, and we will not attempt to validate passthrough default values beyond ensuring they fit within the `{{VAR:-default}}` structure.
- Additionally, due to the “no leftover `${...}`” rule (OmegaConf interpolation safety), defaults MUST NOT contain `${...}` sequences anywhere in the user config.

### 5) Quoting semantics in YAML emission

Docker Compose interpolation should work regardless of YAML quoting, but we should decide expectations:
- If YAML emitter outputs `'${VAR:-x}'` (single-quoted), is that acceptable in our supported Compose versions?
- Are there edge cases with backslashes / Windows paths / colon-heavy strings?

#### Decision
- Accept that YAML emission may quote `${...}` as `'${VAR:-x}'`, we will be using latest Docker Compose which supports this syntax without issues.
- Document that users should be aware of YAML quoting when writing passthrough markers, especially in contexts like volume host paths where backslashes and colons are common. 
- Emitter decides how to quote the output, but we will ensure that the transformation from `{{...}}` to `${...}` is consistent regardless of quoting.

**Note / doubt:** The sharp edge is Windows paths and double-quoted YAML strings (YAML escape sequences like `\U...`). If users write defaults like `{{HOST_HOME:-C:\Users\alice}}`, the generated YAML may become invalid if it ends up double-quoted. Recommend using `C:/Users/alice` or escaping backslashes (`C:\\Users\\alice`) in docs/examples, and add tests covering Windows-path defaults.

#### Revised Decision
- As recommended, we advise user to use forward slashes in paths for cross-platform compatibility and document best practices for writing defaults that may contain special characters.

### 6) Typed fields that currently require numeric parsing

Ports are already planned to become string-based to support passthrough markers.

Open questions:
- Do we want passthrough in other typed fields such as:
  - `ssh.host_port`
  - `uid` / `gid`
  - other int/bool config values
- If yes, do those need to become string-tolerant or get explicit “raw string” alternatives?

#### Decision
- For this change, only port mappings become string-based to support passthrough markers:
  - `stage_1.ports` / `stage_2.ports` are treated as ordered lists of Docker Compose-compatible port mapping **strings**
  - SSH host-port exposure is expressed as a port mapping **string** in the generated compose (either derived from existing SSH settings or provided by the user via the ports list)

**Note / doubt:** Changing truly numeric semantics fields like `uid`/`gid` to strings is higher-risk than ports, because they are used for build-time user creation and must eventually become integers. If passthrough is needed for those, define where and when they must be resolved to int (and what error to show if unresolved).

#### Revised Decision
- Out of scope for this change: making other numeric/bool fields (e.g., `uid`/`gid`) string-tolerant solely to enable passthrough. If users need passthrough there, handle it in a follow-up change with explicit “where does it get resolved?” semantics and validation rules.

### 7) Interaction with env baking into `/etc/environment`

Stage env vars are also written into `_etc_environment.sh` and optionally appended to `/etc/environment` in-container (when `PEI_BAKE_ENV_STAGE_*` is enabled).

Problem:
- Passthrough markers (and Compose `${...}`) do not expand in `/etc/environment` by themselves.

Decision needed:
- Disallow passthrough markers in baked envs (hard error), or
- Warn and keep them literal, or
- Add a runtime expansion step (bigger change).

Recommended default: **error** if passthrough markers are present while baking is enabled.

#### Decision
- As recommended: implement a hard error if passthrough markers will be present in baking.

### 8) Mixed-mode strings (both forms in one value)

Example:
- `image: "${PROJECT_NAME:-app}-{{TAG:-dev}}"`

Decision needed:
- Explicitly support mixed-mode strings, or constrain usage for clarity.

Recommended default: allow it (it is a natural, useful capability) but document clearly.

#### Decision
- Allow mixed-mode strings that contain both config-time `${...}` and compose-time `{{...}}` markers, as this can be a powerful pattern for users. 
- Document this capability clearly

---

### Suggested defaults to bake into the specs

1) After config-time substitution, remaining `${...}` in user config is a **hard error** with guidance to use `{{...}}` for passthrough.
2) Initial support scope: `{{...}}` passthrough is guaranteed only for `docker-compose.yml`.
3) `{{...}}` is strictly limited to `{{VAR}}` and `{{VAR:-default}}` with a clear validation error otherwise.
4) Passthrough markers are disallowed when baking env into `/etc/environment` (error).
5) Passthrough markers are allowed only in values that end up in `docker-compose.yml` (Docker Compose interpolation). They are disallowed in values consumed by `installation/stage-{1,2}/internals/**` without Docker Compose substitution, and in values baked into PeiDocker-generated scripts during `configure`.
