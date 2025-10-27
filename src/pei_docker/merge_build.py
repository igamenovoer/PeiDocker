"""
Merged build artifacts generator (merged.Dockerfile, merged.env, build-merged.sh).

This module provides a small, typed surface that `pei.py` can call to generate
standalone build artifacts for users who want to build without docker compose.

Usage (from CLI configure path):
    generate_merged_build(project_dir=..., out_compose=...)

It keeps `pei.py` and `config_processor.py` lean by encapsulating the logic
for assembling a multi-stage merged Dockerfile and the accompanying scripts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple
import os
import re
import stat

import omegaconf as oc
from omegaconf import DictConfig


def generate_merged_build(project_dir: str, out_compose: DictConfig) -> None:
    """Generate merged build artifacts into the given project directory.

    This writes three files side-by-side with the user's compose files:
    - merged.Dockerfile: standalone, self-contained multi-stage Dockerfile
    - merged.env: environment file with all build args as KEY='value'
    - build-merged.sh: one-shot build script that sources merged.env and runs docker build

    Parameters
    ----------
    project_dir : str
        Absolute or relative path to the project directory (contains stage-*.Dockerfile, installation/, etc.)
    out_compose : DictConfig
        The fully resolved docker compose DictConfig returned by the processor.
    """
    proj = Path(project_dir)
    proj.mkdir(parents=True, exist_ok=True)

    args1, args2, stage2_image = _collect_build_args(out_compose)

    merged_df_text = _compose_merged_dockerfile()
    _write_text(proj / "merged.Dockerfile", merged_df_text)

    _write_merged_env(proj / "merged.env", args1, args2)
    _write_build_script(proj / "build-merged.sh", stage2_image, args1, args2)


def _compose_merged_dockerfile() -> str:
    """Compose a standalone multi-stage Dockerfile by merging stage-1 and stage-2 templates.

    Reads the package-provided templates for stage-1 and stage-2 and stitches
    them into a single file. Stage-1 declares `ARG BASE_IMAGE_1` and builds as
    `stage1`. Stage-2 is rewritten to `FROM stage1 AS final`.

    Returns
    -------
    str
        The merged Dockerfile content.
    """
    pkg_root = Path(__file__).resolve().parent
    df1 = (pkg_root / "project_files" / "stage-1.Dockerfile").read_text()
    df2 = (pkg_root / "project_files" / "stage-2.Dockerfile").read_text()

    # Transform stage-1
    df1 = df1.replace("ARG BASE_IMAGE", "ARG BASE_IMAGE_1")
    df1 = re.sub(r"^FROM\s+\$\{BASE_IMAGE\}.*$", "FROM ${BASE_IMAGE_1} AS stage1", df1, flags=re.M)

    # Transform stage-2
    df2 = re.sub(r"^ARG\s+BASE_IMAGE\s*\n", "", df2, flags=re.M)  # remove BASE_IMAGE arg line
    df2 = re.sub(r"^FROM\s+\$\{BASE_IMAGE\}.*$", "FROM stage1 AS final", df2, flags=re.M)

    return df1.rstrip() + "\n\n" + df2.lstrip()


def _collect_build_args(out_compose: DictConfig) -> Tuple[Dict[str, Any], Dict[str, Any], str]:
    """Collect resolved build arguments and the final image tag from compose.

    Returns stage-1 args, stage-2 args, and the stage-2 image name.
    BASE_IMAGE is not removed/renamed here (renaming handled at emit time).
    """
    services = oc.OmegaConf.select(out_compose, "services") or {}
    s1 = services.get("stage-1", {})
    s2 = services.get("stage-2", {})
    build1 = (s1.get("build") or {})
    build2 = (s2.get("build") or {})
    args1: Dict[str, Any] = build1.get("args") or {}
    args2: Dict[str, Any] = build2.get("args") or {}
    stage2_image = s2.get("image") or "pei-image:stage-2"
    return args1, args2, stage2_image


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _write_merged_env(path: Path, args1: Dict[str, Any], args2: Dict[str, Any]) -> None:
    """Write merged.env with helpful comments describing each variable.

    The file is POSIX-compatible and can be sourced by `build-merged.sh`.
    Values are single-quoted with embedded quotes escaped.
    """

    def q(v: Any) -> str:
        s = str(v)
        return "'" + s.replace("'", "'\\''") + "'"

    # Known variable descriptions
    desc: Dict[str, str] = {
        # Stage-1
        "BASE_IMAGE_1": "Base image for stage-1 (system layer)",
        "PEI_STAGE_HOST_DIR_1": "Host path to installation/stage-1 (copied into image)",
        "PEI_STAGE_DIR_1": "In-container path for stage-1 files (default /pei-from-host/stage-1)",
        "WITH_ESSENTIAL_APPS": "Install essential utilities during build (stage-1)",
        "WITH_CUSTOM_APPS": "Enable custom apps during build (stage-1)",
        "WITH_SSH": "Install and configure OpenSSH server (stage-1)",
        "ROOT_PASSWORD": "Root password (optional; leave empty to disable)",
        "APT_SOURCE_FILE": "APT sources list template or special keyword (tuna/aliyun/163/ustc/cn)",
        "KEEP_APT_SOURCE_FILE": "Keep APT sources file after build (true/false)",
        "APT_USE_PROXY": "Use HTTP proxy for APT operations (true/false)",
        "APT_KEEP_PROXY": "Keep APT proxy settings after build (true/false)",
        "APT_NUM_RETRY": "APT retry count for package operations",
        "PEI_HTTP_PROXY_1": "HTTP proxy URL for stage-1 (e.g., http://host.docker.internal:7890)",
        "PEI_HTTPS_PROXY_1": "HTTPS proxy URL for stage-1",
        "ENABLE_GLOBAL_PROXY": "Export http(s)_proxy for all build steps (true/false)",
        "REMOVE_GLOBAL_PROXY_AFTER_BUILD": "Remove global proxy after build completes (true/false)",
        "SSH_USER_NAME": "SSH usernames (comma-separated)",
        "SSH_USER_PASSWORD": "SSH user passwords (comma-separated)",
        "SSH_USER_UID": "SSH user UIDs (comma-separated)",
        "SSH_CONTAINER_PORT": "SSH port inside container",
        "SSH_PUBKEY_FILE": "Public key file path(s) for SSH users (comma-separated)",
        "SSH_PRIVKEY_FILE": "Private key file path(s) for SSH users (comma-separated)",
        "PEI_BAKE_ENV_STAGE_1": "Bake stage-1 env vars into the image (true/false)",
        # Stage-2
        "PEI_STAGE_HOST_DIR_2": "Host path to installation/stage-2 (copied into image)",
        "PEI_STAGE_DIR_2": "In-container path for stage-2 files (default /pei-from-host/stage-2)",
        "PEI_PREFIX_DATA": "Prefix name for data path (used to construct /soft and /hard paths)",
        "PEI_PREFIX_APPS": "Prefix name for apps path",
        "PEI_PREFIX_WORKSPACE": "Prefix name for workspace path",
        "PEI_PREFIX_VOLUME": "Prefix name for volume path",
        "PEI_PREFIX_IMAGE": "Prefix name for in-image path",
        "PEI_PATH_HARD": "Hard storage base path (default /hard)",
        "PEI_PATH_SOFT": "Soft storage base path (default /soft)",
        "PEI_HTTP_PROXY_2": "HTTP proxy URL for stage-2",
        "PEI_HTTPS_PROXY_2": "HTTPS proxy URL for stage-2",
        # Shared flags also used in stage-2 context
        # ENABLE_GLOBAL_PROXY and REMOVE_GLOBAL_PROXY_AFTER_BUILD already listed above
        "WITH_ESSENTIAL_APPS_2": "Install essential utilities during build (stage-2)",
    }

    # Preferred ordering for readability
    order1 = [
        "BASE_IMAGE_1",
        "PEI_STAGE_HOST_DIR_1",
        "PEI_STAGE_DIR_1",
        "WITH_ESSENTIAL_APPS",
        "WITH_CUSTOM_APPS",
        "WITH_SSH",
        "ROOT_PASSWORD",
        "APT_SOURCE_FILE",
        "KEEP_APT_SOURCE_FILE",
        "APT_USE_PROXY",
        "APT_KEEP_PROXY",
        "APT_NUM_RETRY",
        "PEI_HTTP_PROXY_1",
        "PEI_HTTPS_PROXY_1",
        "ENABLE_GLOBAL_PROXY",
        "REMOVE_GLOBAL_PROXY_AFTER_BUILD",
        "SSH_USER_NAME",
        "SSH_USER_PASSWORD",
        "SSH_USER_UID",
        "SSH_CONTAINER_PORT",
        "SSH_PUBKEY_FILE",
        "SSH_PRIVKEY_FILE",
        "PEI_BAKE_ENV_STAGE_1",
    ]

    order2 = [
        "PEI_STAGE_HOST_DIR_2",
        "PEI_STAGE_DIR_2",
        "WITH_ESSENTIAL_APPS",
        "WITH_CUSTOM_APPS",
        "PEI_PREFIX_DATA",
        "PEI_PREFIX_APPS",
        "PEI_PREFIX_WORKSPACE",
        "PEI_PREFIX_VOLUME",
        "PEI_PREFIX_IMAGE",
        "PEI_PATH_HARD",
        "PEI_PATH_SOFT",
        "PEI_HTTP_PROXY_2",
        "PEI_HTTPS_PROXY_2",
        "ENABLE_GLOBAL_PROXY",
        "REMOVE_GLOBAL_PROXY_AFTER_BUILD",
    ]

    # Normalize keys and prepare
    args1_norm: Dict[str, Any] = {}
    for k, v in (args1 or {}).items():
        key = "BASE_IMAGE_1" if k == "BASE_IMAGE" else k
        args1_norm[key] = v

    args2_norm: Dict[str, Any] = {}
    for k, v in (args2 or {}).items():
        if k == "BASE_IMAGE":  # stage-2 BASE_IMAGE not used in merged
            continue
        args2_norm[k] = v

    def emit_group(title: str, items: Dict[str, Any], order: list[str]) -> list[str]:
        lines: list[str] = []
        lines.append(f"# {title}")
        # first ordered keys
        seen: set[str] = set()
        for k in order:
            if k in items:
                seen.add(k)
                comment = desc.get(k, "")
                if comment:
                    lines.append(f"# {comment}")
                lines.append(f"{k}={q(items[k])}")
                lines.append("")
        # then remaining keys in sorted order
        for k in sorted(items.keys() - seen):
            comment = desc.get(k, "")
            if comment:
                lines.append(f"# {comment}")
            lines.append(f"{k}={q(items[k])}")
            lines.append("")
        return lines

    header = [
        "# merged.env - build arguments for merged.Dockerfile",
        "# Generated by pei-docker-cli configure --with-merged",
        "# Edit values if needed. Format: KEY='value' (single quotes escaped).",
        "",
    ]

    lines: list[str] = []
    lines.extend(header)
    lines.extend(emit_group("Stage-1 build args", args1_norm, order1))
    lines.extend(emit_group("Stage-2 build args", args2_norm, order2))

    _write_text(path, "\n".join(lines).rstrip() + "\n")


def _write_build_script(path: Path, stage2_image: str, args1: Dict[str, Any], args2: Dict[str, Any]) -> None:
    def arg_names(args: Dict[str, Any]) -> str:
        names: list[str] = []
        for k in (args or {}).keys():
            key = "BASE_IMAGE_1" if k == "BASE_IMAGE" else k
            names.append(f"  --build-arg {key} \\")
        return "\n".join(names)

    content = f"""#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
STAGE2_IMAGE_NAME='{stage2_image}'
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o|--output-image)
      if [[ $# -lt 2 ]]; then
        echo "Error: --output-image requires a value <name:tag>" >&2
        exit 1
      fi
      STAGE2_IMAGE_NAME="$2"; shift 2 ;;
    --)
      shift; break ;;
    *)
      echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done
set -a
source "$PROJECT_DIR/merged.env"
set +a
docker build \
  -f "$PROJECT_DIR/merged.Dockerfile" \
  -t "$STAGE2_IMAGE_NAME" \
  --add-host=host.docker.internal:host-gateway \
{arg_names(args1)}
{arg_names(args2)}
  "$PROJECT_DIR"

echo "[merge] Done. Final image: $STAGE2_IMAGE_NAME"
"""

    _write_text(path, content)
    # chmod +x
    mode = os.stat(path).st_mode
    os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
