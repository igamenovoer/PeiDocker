#!/usr/bin/env python3
"""Test script for the PeiDocker GUI."""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all GUI modules can be imported."""
    print("Testing GUI imports...")
    
    try:
        from pei_docker.gui.app import PeiDockerApp, main
        print("[OK] Main app import successful")
        
        from pei_docker.gui.models.config import ProjectConfig
        print("[OK] Config models import successful")
        
        from pei_docker.gui.screens.startup import StartupScreen
        print("[OK] Startup screen import successful")
        
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        print("[OK] Mode selection screen import successful")
        
        from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen
        print("[OK] Simple wizard import successful")
        
        from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen
        print("[OK] Project info screen import successful")
        
        from pei_docker.gui.screens.simple.ssh_config import SSHConfigScreen
        print("[OK] SSH config screen import successful")
        
        from pei_docker.gui.screens.simple.summary import SummaryScreen
        print("[OK] Summary screen import successful")
        
        from pei_docker.gui.utils.docker_utils import check_docker_available
        print("[OK] Docker utils import successful")
        
        from pei_docker.gui.utils.file_utils import ensure_dir_exists
        print("[OK] File utils import successful")
        
        print("\n[SUCCESS] All imports successful!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without running the GUI."""
    print("\nTesting basic functionality...")
    
    try:
        from pei_docker.gui.models.config import ProjectConfig
        
        # Test creating a project config
        config = ProjectConfig()
        config.project_name = "test-project"
        config.project_dir = "./test-project"
        
        # Test generating user config dict
        config_dict = config.to_user_config_dict()
        print("[OK] Config generation successful")
        
        # Test Docker utilities
        from pei_docker.gui.utils.docker_utils import check_docker_available
        docker_available, docker_version = check_docker_available()
        print(f"[OK] Docker check: {'Available' if docker_available else 'Not available'}")
        if docker_version:
            print(f"  Version: {docker_version}")
        
        # Test file utilities
        from pei_docker.gui.utils.file_utils import validate_port_mapping, validate_environment_var
        
        assert validate_port_mapping("8080:80") == True
        assert validate_port_mapping("100-200:300-400") == True
        assert validate_port_mapping("invalid") == False
        print("[OK] Port mapping validation working")
        
        assert validate_environment_var("KEY=value") == True
        assert validate_environment_var("invalid") == False
        print("[OK] Environment variable validation working")
        
        print("\n[SUCCESS] Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Functionality test error: {e}")
        return False


if __name__ == "__main__":
    print("PeiDocker GUI Test Suite")
    print("=" * 40)
    
    # Run tests
    import_success = test_imports()
    if import_success:
        functionality_success = test_basic_functionality()
        
        if functionality_success:
            print("\n[SUCCESS] All tests passed! The GUI should be ready to use.")
            print("\nTo run the GUI:")
            print("  pixi run pei-docker-gui")
            print("  pixi run pei-docker-gui --project-dir ./my-project")
        else:
            print("\n[ERROR] Some functionality tests failed.")
            sys.exit(1)
    else:
        print("\n[ERROR] Import tests failed. Cannot proceed with functionality tests.")
        sys.exit(1)