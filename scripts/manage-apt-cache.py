#!/usr/bin/env python3
"""
APT Cache Management Script for PeiDocker Testing

This script manages apt package caching to accelerate testing by:
1. Copying cached packages from workspace cache to project tmp directories
2. Setting up builds to use cached packages
3. Collecting packages back to workspace cache after builds
"""

import os
import shutil
import argparse
import sys
from pathlib import Path

def get_workspace_root():
    """Get the PeiDocker workspace root directory"""
    return Path(__file__).parent.parent

def get_cache_dir():
    """Get the workspace apt cache directory"""
    return get_workspace_root() / "tmp" / "apt-cache"

def copy_cache_to_project(project_path):
    """
    Copy cached packages from workspace cache to project tmp directories
    
    Args:
        project_path: Path to the project directory (e.g., test-minimal-build)
    """
    project_path = Path(project_path)
    cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        print(f"Cache directory {cache_dir} does not exist, creating it...")
        cache_dir.mkdir(parents=True, exist_ok=True)
        return
    
    # Copy to both stage-1 and stage-2 tmp directories
    for stage in ["stage-1", "stage-2"]:
        stage_tmp = project_path / "installation" / stage / "tmp"
        stage_tmp.mkdir(parents=True, exist_ok=True)
        
        if cache_dir.exists() and any(cache_dir.iterdir()):
            print(f"Copying cached packages to {stage_tmp}")
            for item in cache_dir.iterdir():
                if item.is_file() and item.name.endswith('.deb'):
                    dest = stage_tmp / item.name
                    shutil.copy2(item, dest)
                    print(f"  Copied {item.name}")
        else:
            print(f"No cached packages found in {cache_dir}")

def collect_cache_from_project(project_path):
    """
    Collect packages from project tmp directories back to workspace cache
    
    Args:
        project_path: Path to the project directory (e.g., test-minimal-build)
    """
    project_path = Path(project_path)
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    collected = 0
    for stage in ["stage-1", "stage-2"]:
        stage_tmp = project_path / "installation" / stage / "tmp"
        if stage_tmp.exists():
            for item in stage_tmp.iterdir():
                if item.is_file() and item.name.endswith('.deb'):
                    dest = cache_dir / item.name
                    if not dest.exists():
                        shutil.copy2(item, dest)
                        collected += 1
                        print(f"Collected {item.name} to cache")
    
    print(f"Collected {collected} new packages to cache")

def setup_project_for_caching(project_path):
    """
    Set up project to use apt caching during build
    
    Args:
        project_path: Path to the project directory (e.g., test-minimal-build)
    """
    project_path = Path(project_path)
    
    # Create cache setup script for each stage
    for stage in ["stage-1", "stage-2"]:
        stage_tmp = project_path / "installation" / stage / "tmp"
        stage_tmp.mkdir(parents=True, exist_ok=True)
        
        # Create a script to set up apt cache from tmp directory
        cache_setup_script = stage_tmp / "setup-apt-cache.sh"
        cache_setup_content = f"""#!/bin/bash
# Set up APT cache from tmp directory

echo "Setting up APT cache from tmp directory..."

# Create cache directory
mkdir -p /apt-cache
mkdir -p /var/cache/apt/archives

# Copy .deb files from tmp to cache directory
if [ -d "$PEI_STAGE_DIR_{stage[-1]}/tmp" ]; then
    find "$PEI_STAGE_DIR_{stage[-1]}/tmp" -name "*.deb" -exec cp {{}} /apt-cache/ \\;
    find "$PEI_STAGE_DIR_{stage[-1]}/tmp" -name "*.deb" -exec cp {{}} /var/cache/apt/archives/ \\;
    echo "Copied cached packages to /apt-cache and /var/cache/apt/archives"
fi

# Configure APT to keep downloaded packages
echo 'APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/01keep-packages
echo 'Dir::Cache::Archives "/var/cache/apt/archives";' >> /etc/apt/apt.conf.d/01keep-packages

# Set up APT to use the cache
export PEI_APT_CACHE_DIR="/apt-cache"
if [ -f "$PEI_STAGE_DIR_{stage[-1]}/system/apt/enable-external-cache.sh" ]; then
    $PEI_STAGE_DIR_{stage[-1]}/system/apt/enable-external-cache.sh /apt-cache
fi

# Create a script to collect packages after installation
cat > /collect-packages.sh << 'EOF'
#!/bin/bash
echo "Collecting downloaded packages..."
mkdir -p "$PEI_STAGE_DIR_{stage[-1]}/tmp"
find /var/cache/apt/archives -name "*.deb" -exec cp {{}} "$PEI_STAGE_DIR_{stage[-1]}/tmp/" \\;
echo "Packages collected to $PEI_STAGE_DIR_{stage[-1]}/tmp"
EOF
chmod +x /collect-packages.sh
"""
        
        with open(cache_setup_script, 'w') as f:
            f.write(cache_setup_content)
        
        print(f"Created cache setup script for {stage}")

def clear_project_cache(project_path):
    """
    Clear cached packages from project tmp directories
    
    Args:
        project_path: Path to the project directory (e.g., test-minimal-build)
    """
    project_path = Path(project_path)
    
    cleared = 0
    for stage in ["stage-1", "stage-2"]:
        stage_tmp = project_path / "installation" / stage / "tmp"
        if stage_tmp.exists():
            for item in stage_tmp.iterdir():
                if item.is_file() and item.name.endswith('.deb'):
                    item.unlink()
                    cleared += 1
            
            # Remove cache setup script
            cache_setup_script = stage_tmp / "setup-apt-cache.sh"
            if cache_setup_script.exists():
                cache_setup_script.unlink()
    
    print(f"Cleared {cleared} cached packages from project")

def main():
    parser = argparse.ArgumentParser(description="Manage APT cache for PeiDocker testing")
    parser.add_argument("command", choices=["copy-to", "collect-from", "setup", "clear"], 
                       help="Command to execute")
    parser.add_argument("project_path", help="Path to the project directory")
    
    args = parser.parse_args()
    
    if args.command == "copy-to":
        copy_cache_to_project(args.project_path)
    elif args.command == "collect-from":
        collect_cache_from_project(args.project_path)
    elif args.command == "setup":
        setup_project_for_caching(args.project_path)
    elif args.command == "clear":
        clear_project_cache(args.project_path)

if __name__ == "__main__":
    main()