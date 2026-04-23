# Node, UV, Bun, And Simple Installers Reference

## Source Files

- `docs/manual/scripts/simple-installers.md`
- `docs/examples/advanced/web-dev-nodejs.md`
- `docs/examples/advanced/china-corporate-proxy.md`
- `src/pei_docker/examples/advanced/web-dev-nodejs/user_config.yml`
- `src/pei_docker/examples/advanced/china-corporate-proxy/user_config.yml`

## Common Scripts

Preferred paths under `stage-1/system/`:

- Node.js / NVM: `nodejs/install-nvm.sh`, `nodejs/install-nodejs.sh`, `nodejs/install-nvm-nodejs.sh`
- Bun: `bun/install-bun.sh`
- UV: `uv/install-uv.sh`
- Clang: `clang/install-clang.sh`
- Firefox: `firefox/setup-firefox-repo.sh`
- NGC: `ngc/fix-shinit.sh`
- LiteLLM: `litellm/install-litellm.sh`
- Claude Code: `claude-code/install-claude-code.sh`
- Codex CLI: `codex-cli/install-codex-cli.sh`
- Magnum: `magnum/install-magnum-gl.sh`
- Vision Dev: `vision-dev/install-vision-dev.bash`
- Locale helper: `set-locale.sh`

## Node.js Pattern

```yaml
stage_2:
  custom:
    on_build:
      - "stage-1/system/nodejs/install-nvm-nodejs.sh --user webdev --nodejs-version 22"
```

Pair web development with host-backed workspace storage and app ports.

## UV Pattern

```yaml
stage_2:
  custom:
    on_build:
      - "stage-1/system/uv/install-uv.sh --user dev --pypi-repo tuna"
```

## Dependency Chains

- `claude-code` and `codex-cli` assume Bun is installed.
- `litellm` assumes UV is installed.
- `magnum` and `vision-dev` are heavier installs despite living in the simple installer catalog.
