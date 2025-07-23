"""Docker utilities for the GUI."""

import subprocess
import shutil
from typing import Optional, List, Tuple


def check_docker_available() -> Tuple[bool, Optional[str]]:
    """Check if Docker is available and return version info."""
    try:
        result = subprocess.run(
            ["docker", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, None
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False, None


def check_docker_images_exist(image_names: List[str]) -> List[Tuple[str, bool]]:
    """Check if Docker images exist locally."""
    results = []
    for image in image_names:
        try:
            result = subprocess.run(
                ["docker", "images", "-q", image],
                capture_output=True,
                text=True,
                timeout=10
            )
            exists = bool(result.stdout.strip())
            results.append((image, exists))
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            results.append((image, False))
    
    return results


def get_docker_info() -> Optional[dict]:
    """Get Docker system information."""
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        return None
    except Exception:
        return None