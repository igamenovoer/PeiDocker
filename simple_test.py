#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
from pei_docker.gui.models.config import ProjectConfig

config = ProjectConfig() 
screen = ModeSelectionScreen(config)
has_method = hasattr(screen, '_browse_directory_async')
print(f"SUCCESS: Mode selection screen created with async method: {has_method}")