#!/usr/bin/env python3
"""
PeiDocker Web GUI Launcher.

This script launches the NiceGUI web interface for PeiDocker project configuration.
"""

import sys
import os
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from nicegui import ui, run
    from src.pei_docker.webgui.app import create_app
    print("✅ Successfully imported NiceGUI and PeiDocker web GUI modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed the dependencies:")
    print("  pixi install")
    print("  or pip install nicegui pyyaml")
    sys.exit(1)

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from src.pei_docker.webgui.models import AppData, AppState, TabName
        print("  ✅ Models imported successfully")
    except ImportError as e:
        print(f"  ❌ Models import failed: {e}")
        return False
    
    try:
        from src.pei_docker.webgui.utils import ProjectManager, FileOperations, ValidationManager
        print("  ✅ Utils imported successfully")
    except ImportError as e:
        print(f"  ❌ Utils import failed: {e}")
        return False
    
    try:
        from src.pei_docker.webgui.tabs import (
            ProjectTab, SSHTab, NetworkTab, EnvironmentTab,
            StorageTab, ScriptsTab, SummaryTab
        )
        print("  ✅ All tabs imported successfully")
    except ImportError as e:
        print(f"  ❌ Tabs import failed: {e}")
        return False
    
    return True


@ui.page('/')
def main_page():
    """Main PeiDocker GUI page."""
    try:
        # Create and setup the GUI directly
        gui_app = create_app()
        print("🚀 PeiDocker Web GUI launched successfully!")
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        ui.label(f'Error launching PeiDocker GUI: {str(e)}').classes('text-red-600 text-center mt-20')
        ui.label('Please check the console for more details.').classes('text-gray-600 text-center mt-4')

def main():
    """Main function to launch PeiDocker Web GUI."""
    print("🐳 Starting PeiDocker Web GUI...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Test imports first
    if not test_imports():
        print("❌ Import failed. Please check your installation.")
        return 1
    
    print("✅ All dependencies loaded successfully!")
    print("\n🌐 Starting web server...")
    print("📱 Open your browser and navigate to: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        # Configure NiceGUI
        ui.run(
            title='PeiDocker Web GUI',
            port=8080,
            host='0.0.0.0',
            show=True,  # Automatically open browser
            reload=False,  # Disable auto-reload for stability
            favicon='🐳'
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())