# Stage 1 System Scripts

Scripts for configuring system-level packages and settings during Stage 1.

## Categories

The canonical implementations for PeiDocker-provided system installers live under
this directory.

Common categories (non-exhaustive):

*   `apt`: APT configuration (proxies, mirrors).
*   `proxy`: Network proxy settings.
*   `ssh`: SSH server configuration.
*   `uv`: UV package manager installation.
*   `conda`: Conda installers and activation helpers.
*   `pixi`: Pixi installer and environment helpers.
*   `nodejs`: Node.js / NVM installers.
*   `bun`: Bun runtime installer.
*   `codex-cli`: OpenAI Codex CLI installer.
*   `claude-code`: Anthropic Claude Code CLI installer.
*   `litellm`: LiteLLM proxy installer and helper assets.
*   `opencv`: OpenCV build/install scripts.
*   `opengl`: OpenGL (WSLg/Windows) setup scripts and assets.
*   `magnum`: Magnum graphics library build/install script.
*   `set-locale.sh`: Locale setup helper.
