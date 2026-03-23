# Simple Installers

These scripts are closer to “install one thing” than to full environment orchestration, so they are grouped here instead of getting one page each.

## Tooling Summary

| Tool | Preferred path | Notes |
| --- | --- | --- |
| Node.js / NVM | `stage-1/system/nodejs/` | `install-nvm.sh`, `install-nodejs.sh`, and `install-nvm-nodejs.sh` cover the common flows |
| Bun | `stage-1/system/bun/install-bun.sh` | Supports `--user`, `--install-dir`, `--npm-repo`, `--installer-url` |
| UV | `stage-1/system/uv/install-uv.sh` | Supports `--user`, `--install-dir`, `--pypi-repo`, `--installer-url` |
| Clang | `stage-1/system/clang/install-clang.sh` | Pulls LLVM installer script |
| Firefox | `stage-1/system/firefox/setup-firefox-repo.sh` | Adds the Mozilla APT repository |
| NGC | `stage-1/system/ngc/fix-shinit.sh` | Small NVIDIA helper fixup |
| LiteLLM | `stage-1/system/litellm/install-litellm.sh` | Requires `uv` first |
| Claude Code | `stage-1/system/claude-code/install-claude-code.sh` | Requires `bun` first |
| Codex CLI | `stage-1/system/codex-cli/install-codex-cli.sh` | Requires `bun` first |
| Magnum | `stage-1/system/magnum/install-magnum-gl.sh` | Source-builds Corrade and Magnum |
| Vision Dev | `stage-1/system/vision-dev/install-vision-dev.bash` | Installs common CV libraries and Python packages |
| Set Locale | `stage-1/system/set-locale.sh` | Locale helper for scripts that need UTF-8 |

## Node.js Notes

`install-nvm-nodejs.sh` is the fastest one-step path when you want both NVM and a Node runtime:

```yaml
- "stage-1/system/nodejs/install-nvm-nodejs.sh --user webdev --nodejs-version 22"
```

## Dependency Chains

- `claude-code` and `codex-cli` assume Bun is installed.
- `litellm` assumes UV is installed.
- `magnum` and `vision-dev` are substantial installs even though their interfaces are simple.
