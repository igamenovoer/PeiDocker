# PeiDocker GUI Integration Testing Plan

## Overview

Integration tests focus on testing the interactions between components and complete user workflows. These tests ensure that the GUI functions correctly as a complete system and that user workflows operate seamlessly.

## Test Categories

### 1. Screen Navigation Tests
### 2. Complete User Workflow Tests  
### 3. Configuration Persistence Tests
### 4. Docker Integration Tests
### 5. File System Integration Tests
### 6. Cross-Component Communication Tests

## Integration Test Structure Template

```python
import pytest
from unittest.mock import patch, Mock
from textual.testing import App
from pathlib import Path
import tempfile
import shutil

@pytest.mark.integration
async def test_integration_scenario():
    """Test complete integration scenario."""
    # Arrange - Set up test environment
    # Act - Execute complete workflow
    # Assert - Verify end-to-end results
    pass
```

## Screen Navigation Integration Tests

### Test: `test_navigation_flow.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.app import PeiDockerApp
from pei_docker.gui.models.config import ProjectConfig

class TestNavigationFlow:
    """Test suite for screen navigation integration."""
    
    @pytest.mark.integration
    async def test_complete_navigation_flow(self):
        """Test complete navigation from startup to summary."""
        app = PeiDockerApp()
        
        async with app.run_test() as pilot:
            # Should start on startup screen
            assert len(app.screen_stack) == 1
            
            # Continue from startup screen
            await pilot.press("enter")
            await pilot.pause()
            
            # Should navigate to mode selection
            assert len(app.screen_stack) == 2
            
            # Select simple mode and continue
            await pilot.click("#simple_mode")
            await pilot.click("#continue")
            await pilot.pause()
            
            # Should navigate to wizard
            assert len(app.screen_stack) == 3
    
    @pytest.mark.integration
    async def test_navigation_with_project_dir_provided(self):
        """Test navigation when project directory is provided."""
        test_dir = "/test/project"
        app = PeiDockerApp(project_dir=test_dir)
        
        async with app.run_test() as pilot:
            # Should start with project dir already set
            assert app.project_config.project_dir == test_dir
            
            # Continue from startup
            await pilot.press("enter")
            await pilot.pause()
            
            # Should skip directory selection and go to mode selection
            # Mode selection should show existing project directory
            mode_screen = app.screen_stack[-1]
            assert hasattr(mode_screen, 'project_config')
            assert mode_screen.project_config.project_dir == test_dir
    
    @pytest.mark.integration
    async def test_back_navigation_flow(self):
        """Test backward navigation through screens."""
        app = PeiDockerApp()
        
        async with app.run_test() as pilot:
            # Navigate forward to wizard
            await pilot.press("enter")  # Continue from startup
            await pilot.pause()
            
            await pilot.click("#simple_mode")
            await pilot.click("#continue")
            await pilot.pause()
            
            # Now navigate back
            await pilot.press("b")  # Back key
            await pilot.pause()
            
            # Should be back at mode selection
            assert len(app.screen_stack) == 2
            
            await pilot.press("b")  # Back again
            await pilot.pause()
            
            # Should be back at startup
            assert len(app.screen_stack) == 1
    
    @pytest.mark.integration
    @patch('pei_docker.gui.utils.docker_utils.check_docker_available')
    async def test_navigation_with_docker_unavailable(self, mock_docker_check):
        """Test navigation flow when Docker is unavailable."""
        mock_docker_check.return_value = (False, None)
        
        app = PeiDockerApp()
        
        async with app.run_test() as pilot:
            # Should show Docker warning but still allow navigation
            await pilot.press("enter")
            await pilot.pause()
            
            # Should still be able to continue to mode selection
            assert len(app.screen_stack) == 2
    
    @pytest.mark.integration
    async def test_quit_from_any_screen(self):
        """Test quitting from various screens."""
        app = PeiDockerApp()
        
        async with app.run_test() as pilot:
            # Test quit from startup
            await pilot.press("q")
            # App should quit (test framework will handle this)
```

## Complete User Workflow Tests

### Test: `test_simple_mode_flow.py`

```python
import pytest
from unittest.mock import patch, Mock
import tempfile
import shutil
from pathlib import Path
from pei_docker.gui.app import PeiDockerApp
from pei_docker.gui.models.config import ProjectConfig

class TestSimpleModeFlow:
    """Test suite for complete simple mode workflow."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.integration
    async def test_complete_simple_mode_workflow(self, temp_project_dir):
        """Test complete simple mode workflow from start to finish."""
        app = PeiDockerApp()
        
        async with app.run_test() as pilot:
            # Step 1: Navigate through startup and mode selection
            await pilot.press("enter")  # Continue from startup
            await pilot.pause()
            
            # Enter project directory
            await pilot.click("#project_dir")
            await pilot.press(*temp_project_dir)
            await pilot.pause()
            
            # Select simple mode and continue
            await pilot.click("#simple_mode")
            await pilot.click("#continue")
            await pilot.pause()
            
            # Step 2: Configure project information
            await pilot.click("#project_name")
            await pilot.press("ctrl+a")  # Select all
            await pilot.press(*"test-project")
            await pilot.pause()
            
            await pilot.click("#base_image")
            await pilot.press("ctrl+a")
            await pilot.press(*"ubuntu:24.04")
            await pilot.pause()
            
            # Continue to next step
            await pilot.click("#next")
            await pilot.pause()
            
            # Step 3: Configure SSH
            # Enable SSH (should be default)
            await pilot.click("#ssh_user")
            await pilot.press("ctrl+a")
            await pilot.press(*"testuser")
            await pilot.pause()
            
            await pilot.click("#ssh_password")
            await pilot.press("ctrl+a")
            await pilot.press(*"testpass")
            await pilot.pause()
            
            # Continue to summary
            await pilot.click("#next")
            await pilot.pause()
            
            # Step 4: Review and save configuration
            await pilot.click("#save")
            await pilot.pause()
            
            # Verify configuration was saved
            config_file = Path(temp_project_dir) / "user_config.yml"
            assert config_file.exists()
            
            # Verify configuration content
            config_content = config_file.read_text()
            assert "test-project" in config_content
            assert "ubuntu:24.04" in config_content
            assert "testuser" in config_content
    
    @pytest.mark.integration
    async def test_simple_mode_with_advanced_ssh_config(self, temp_project_dir):
        """Test simple mode with advanced SSH configuration."""
        app = PeiDockerApp(project_dir=temp_project_dir)
        
        async with app.run_test() as pilot:
            # Navigate to wizard
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#simple_mode")
            await pilot.click("#continue")
            await pilot.pause()
            
            # Configure project info
            await pilot.click("#project_name")
            await pilot.press(*"ssh-test-project")
            await pilot.click("#next")
            await pilot.pause()
            
            # Configure SSH with public key
            await pilot.click("#ssh_user")
            await pilot.press(*"sshuser")
            await pilot.pause()
            
            # Enable public key authentication
            await pilot.click("#enable_pubkey")
            await pilot.pause()
            
            await pilot.click("#pubkey_text")
            test_pubkey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ test@example.com"
            await pilot.press(*test_pubkey)
            await pilot.pause()
            
            # Enable root access
            await pilot.click("#enable_root")
            await pilot.pause()
            
            await pilot.click("#root_password")
            await pilot.press(*"rootpass")
            await pilot.pause()
            
            # Continue to summary and save
            await pilot.click("#next")
            await pilot.pause()
            await pilot.click("#save")
            await pilot.pause()
            
            # Verify advanced SSH configuration
            config_file = Path(temp_project_dir) / "user_config.yml"
            config_content = config_file.read_text()
            assert "sshuser" in config_content
            assert "ssh-rsa AAAAB3" in config_content
            assert "root" in config_content
    
    @pytest.mark.integration
    async def test_simple_mode_with_validation_errors(self, temp_project_dir):
        """Test simple mode workflow with validation errors."""
        app = PeiDockerApp(project_dir=temp_project_dir)
        
        async with app.run_test() as pilot:
            # Navigate to wizard
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#simple_mode")
            await pilot.click("#continue")
            await pilot.pause()
            
            # Try to continue without entering project name
            await pilot.click("#next")
            await pilot.pause()
            
            # Should show validation error and stay on same screen
            # (Implementation specific - check for error message)
            
            # Now enter valid project name
            await pilot.click("#project_name")
            await pilot.press(*"valid-project")
            await pilot.pause()
            
            # Should now be able to continue
            await pilot.click("#next")
            await pilot.pause()
            
            # Should be on SSH configuration screen
    
    @pytest.mark.integration
    async def test_simple_mode_back_and_forth_navigation(self, temp_project_dir):
        """Test navigating back and forth in simple mode wizard."""
        app = PeiDockerApp(project_dir=temp_project_dir)
        
        async with app.run_test() as pilot:
            # Navigate to wizard
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#simple_mode")
            await pilot.click("#continue")
            await pilot.pause()
            
            # Configure project info
            await pilot.click("#project_name")
            await pilot.press(*"nav-test-project")
            await pilot.click("#next")
            await pilot.pause()
            
            # Now on SSH screen - go back
            await pilot.click("#back")
            await pilot.pause()
            
            # Should be back on project info screen
            # Verify data was preserved
            project_name_input = app.query_one("#project_name")
            assert "nav-test-project" in str(project_name_input.value)
            
            # Go forward again
            await pilot.click("#next")
            await pilot.pause()
            
            # Configure SSH and continue
            await pilot.click("#ssh_user")
            await pilot.press(*"navuser")
            await pilot.click("#next")
            await pilot.pause()
            
            # Now on summary screen - go back twice
            await pilot.click("#back")
            await pilot.pause()
            await pilot.click("#back")
            await pilot.pause()
            
            # Should be back on project info screen
            # Data should still be preserved
            project_name_input = app.query_one("#project_name")
            assert "nav-test-project" in str(project_name_input.value)
    
    @pytest.mark.integration
    async def test_simple_mode_cancel_workflow(self, temp_project_dir):
        """Test canceling workflow at various stages."""
        app = PeiDockerApp(project_dir=temp_project_dir)
        
        async with app.run_test() as pilot:
            # Navigate to wizard
            await pilot.press("enter")
            await pilot.pause()
            await pilot.click("#simple_mode")
            await pilot.click("#continue")
            await pilot.pause()
            
            # Configure some data
            await pilot.click("#project_name")
            await pilot.press(*"cancel-test")
            await pilot.pause()
            
            # Cancel from wizard
            await pilot.click("#cancel")
            await pilot.pause()
            
            # Should quit application or return to main menu
            # Verify no configuration file was created
            config_file = Path(temp_project_dir) / "user_config.yml"
            assert not config_file.exists()
```

## Configuration Persistence Tests

### Test: `test_configuration_save.py`

```python
import pytest
from unittest.mock import patch, Mock
import tempfile
import shutil
import yaml
from pathlib import Path
from pei_docker.gui.models.config import ProjectConfig, SSHUser
from pei_docker.gui.screens.simple.summary import SummaryScreen

class TestConfigurationPersistence:
    """Test suite for configuration saving and loading."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config(self):
        """Create sample configuration for testing."""
        config = ProjectConfig(
            project_name="test-project",
            project_dir="/test/path"
        )
        
        # Configure SSH
        config.stage_1.ssh.enable = True
        config.stage_1.ssh.port = 22
        config.stage_1.ssh.host_port = 2222
        config.stage_1.ssh.users["testuser"] = SSHUser(
            password="testpass",
            uid=1100
        )
        
        # Configure other settings
        config.stage_1.base_image = "ubuntu:24.04"
        config.stage_1.output_image = "test-project:stage-1"
        config.stage_1.ports = ["8080:80", "3000:3000"]
        config.stage_1.environment = ["NODE_ENV=production", "DEBUG=false"]
        config.stage_1.device_type = "gpu"
        
        return config
    
    @pytest.mark.integration
    async def test_configuration_save_to_yaml(self, temp_project_dir, sample_config):
        """Test saving configuration to YAML file."""
        sample_config.project_dir = temp_project_dir
        summary_screen = SummaryScreen(sample_config)
        
        # Mock the app for notifications
        mock_app = Mock()
        summary_screen.app = mock_app
        
        # Save configuration
        result = summary_screen._save_configuration()
        
        assert result == True
        
        # Verify file was created
        config_file = Path(temp_project_dir) / "user_config.yml"
        assert config_file.exists()
        
        # Verify file content
        with open(config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        # Check structure
        assert "stage_1" in saved_config
        assert "stage_2" in saved_config
        
        # Check specific values
        stage1 = saved_config["stage_1"]
        assert stage1["image"]["base"] == "ubuntu:24.04"
        assert stage1["image"]["output"] == "test-project:stage-1"
        assert stage1["ssh"]["enable"] == True
        assert stage1["ssh"]["port"] == 22
        assert stage1["ssh"]["host_port"] == 2222
        assert "testuser" in stage1["ssh"]["users"]
        assert stage1["ssh"]["users"]["testuser"]["password"] == "testpass"
        assert stage1["ssh"]["users"]["testuser"]["uid"] == 1100
        assert stage1["ports"] == ["8080:80", "3000:3000"]
        assert stage1["environment"] == ["NODE_ENV=production", "DEBUG=false"]
        assert stage1["device"]["type"] == "gpu"
    
    @pytest.mark.integration
    async def test_configuration_save_minimal(self, temp_project_dir):
        """Test saving minimal configuration."""
        config = ProjectConfig(
            project_name="minimal-project",
            project_dir=temp_project_dir
        )
        
        summary_screen = SummaryScreen(config)
        mock_app = Mock()
        summary_screen.app = mock_app
        
        result = summary_screen._save_configuration()
        
        assert result == True
        
        # Verify file content
        config_file = Path(temp_project_dir) / "user_config.yml"
        with open(config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        # Should have basic structure even with minimal config
        assert "stage_1" in saved_config
        assert "stage_2" in saved_config
        
        stage1 = saved_config["stage_1"]
        assert stage1["image"]["base"] == "ubuntu:24.04"  # Default value
        assert stage1["ssh"]["enable"] == True  # Default value
    
    @pytest.mark.integration
    async def test_configuration_save_ssh_disabled(self, temp_project_dir):
        """Test saving configuration with SSH disabled."""
        config = ProjectConfig(
            project_name="no-ssh-project",
            project_dir=temp_project_dir
        )
        config.stage_1.ssh.enable = False
        
        summary_screen = SummaryScreen(config)
        mock_app = Mock()
        summary_screen.app = mock_app
        
        result = summary_screen._save_configuration()
        
        assert result == True
        
        # Verify SSH is disabled in saved config
        config_file = Path(temp_project_dir) / "user_config.yml"
        with open(config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["stage_1"]["ssh"]["enable"] == False
        assert len(saved_config["stage_1"]["ssh"]["users"]) == 0
    
    @pytest.mark.integration
    async def test_configuration_save_failure(self, sample_config):
        """Test configuration save failure handling."""
        # Set invalid project directory
        sample_config.project_dir = "/invalid/path/that/does/not/exist"
        
        summary_screen = SummaryScreen(sample_config)
        mock_app = Mock()
        summary_screen.app = mock_app
        
        result = summary_screen._save_configuration()
        
        assert result == False
        mock_app.notify.assert_called_with(
            "Failed to save configuration", 
            severity="error"
        )
    
    @pytest.mark.integration
    async def test_configuration_yaml_format_validation(self, temp_project_dir, sample_config):
        """Test that saved YAML is valid and properly formatted."""
        sample_config.project_dir = temp_project_dir
        summary_screen = SummaryScreen(sample_config)
        mock_app = Mock()
        summary_screen.app = mock_app
        
        # Save configuration
        summary_screen._save_configuration()
        
        # Load and verify YAML is valid
        config_file = Path(temp_project_dir) / "user_config.yml"
        
        try:
            with open(config_file, 'r') as f:
                saved_config = yaml.safe_load(f)
            
            # Should be able to load without errors
            assert isinstance(saved_config, dict)
            
            # Check required top-level keys
            assert "stage_1" in saved_config
            assert "stage_2" in saved_config
            
        except yaml.YAMLError as e:
            pytest.fail(f"Generated YAML is invalid: {e}")
    
    @pytest.mark.integration
    async def test_configuration_roundtrip(self, temp_project_dir, sample_config):
        """Test configuration save and load roundtrip."""
        sample_config.project_dir = temp_project_dir
        
        # Save configuration
        summary_screen = SummaryScreen(sample_config)
        mock_app = Mock()
        summary_screen.app = mock_app
        
        summary_screen._save_configuration()
        
        # Load configuration back
        config_file = Path(temp_project_dir) / "user_config.yml"
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        # Verify key values survived the roundtrip
        stage1 = loaded_config["stage_1"]
        assert stage1["image"]["base"] == sample_config.stage_1.base_image
        assert stage1["ssh"]["enable"] == sample_config.stage_1.ssh.enable
        assert stage1["ports"] == sample_config.stage_1.ports
        assert stage1["environment"] == sample_config.stage_1.environment
        
        # Verify SSH user configuration
        ssh_users = stage1["ssh"]["users"]
        assert "testuser" in ssh_users
        assert ssh_users["testuser"]["password"] == "testpass"
        assert ssh_users["testuser"]["uid"] == 1100
```

## Docker Integration Tests

### Test: `test_docker_integration.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.screens.startup import StartupScreen
from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen  
from pei_docker.gui.models.config import ProjectConfig

class TestDockerIntegration:
    """Test suite for Docker system integration."""
    
    @pytest.mark.integration
    @pytest.mark.docker_required
    @patch('subprocess.run')
    async def test_docker_availability_detection(self, mock_run):
        """Test Docker availability detection integration."""
        # Mock successful Docker command
        mock_result = Mock()
        mock_result.returncode = 0  
        mock_result.stdout = "Docker version 24.0.6, build ed223bc"
        mock_run.return_value = mock_result
        
        config = ProjectConfig()
        startup_screen = StartupScreen(config)
        
        # Mock app for screen transitions
        mock_app = Mock()
        startup_screen.app = mock_app
        
        await startup_screen.on_mount()
        
        # Should detect Docker as available
        assert startup_screen.docker_available == True
        assert "24.0.6" in startup_screen.docker_version
        
        # Should start auto-continue timer
        assert startup_screen.auto_continue_timer is not None
    
    @pytest.mark.integration
    @patch('subprocess.run')
    async def test_docker_unavailable_workflow(self, mock_run):
        """Test complete workflow when Docker is unavailable."""
        # Mock Docker not found
        mock_run.side_effect = FileNotFoundError()
        
        config = ProjectConfig()
        startup_screen = StartupScreen(config)
        
        mock_app = Mock()
        startup_screen.app = mock_app
        
        await startup_screen.on_mount()
        
        # Should detect Docker as unavailable
        assert startup_screen.docker_available == False
        assert startup_screen.docker_version is None
        
        # Should not start auto-continue timer
        assert startup_screen.auto_continue_timer is None
        
        # User should still be able to continue manually
        startup_screen.action_continue()
        
        # Should still navigate to next screen
        mock_app.install_screen.assert_called()
        mock_app.push_screen.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.docker_required
    @patch('subprocess.run')
    async def test_docker_image_validation(self, mock_run):
        """Test Docker image validation integration."""
        # Mock Docker commands for image checking
        def mock_docker_command(cmd, **kwargs):
            if "inspect" in cmd:
                # Mock image exists
                result = Mock()
                result.returncode = 0
                result.stdout = '{"Id": "sha256:123456"}'
                return result
            else:
                # Default mock for other commands
                result = Mock()
                result.returncode = 0
                result.stdout = "Docker version 24.0.6"
                return result
        
        mock_run.side_effect = mock_docker_command
        
        config = ProjectConfig()
        project_info_screen = ProjectInfoScreen(config)
        
        # Test image validation
        is_valid = project_info_screen._validate_docker_image("ubuntu:24.04")
        
        assert is_valid == True
        
        # Verify Docker inspect command was called
        mock_run.assert_called_with(
            ["docker", "image", "inspect", "ubuntu:24.04"],
            capture_output=True,
            text=True,
            timeout=30
        )
    
    @pytest.mark.integration
    @patch('subprocess.run')
    async def test_docker_image_not_found(self, mock_run):
        """Test Docker image validation when image doesn't exist."""
        # Mock Docker image not found
        def mock_docker_command(cmd, **kwargs):
            if "inspect" in cmd:
                result = Mock()
                result.returncode = 1  # Image not found
                result.stderr = "Error: No such image"
                return result
            else:
                result = Mock()
                result.returncode = 0
                result.stdout = "Docker version 24.0.6"
                return result
        
        mock_run.side_effect = mock_docker_command
        
        config = ProjectConfig()
        project_info_screen = ProjectInfoScreen(config)
        
        # Test image validation
        is_valid = project_info_screen._validate_docker_image("nonexistent:tag")
        
        assert is_valid == False
    
    @pytest.mark.integration
    @pytest.mark.docker_required
    async def test_docker_integration_end_to_end(self):
        """Test end-to-end Docker integration workflow."""
        from pei_docker.gui.app import PeiDockerApp
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            app = PeiDockerApp(project_dir=temp_dir)
            
            async with app.run_test() as pilot:
                # Navigate through workflow
                await pilot.press("enter")  # Continue from startup
                await pilot.pause()
                
                # Should have detected Docker (if available)
                startup_screen = app.screen_stack[0]
                if startup_screen.docker_available:
                    # Complete workflow with Docker validation
                    await pilot.click("#simple_mode")
                    await pilot.click("#continue")
                    await pilot.pause()
                    
                    # Configure project with valid Docker image
                    await pilot.click("#project_name")
                    await pilot.press(*"docker-test")
                    
                    await pilot.click("#base_image")
                    await pilot.press("ctrl+a")
                    await pilot.press(*"ubuntu:24.04")
                    await pilot.pause()
                    
                    # Image validation should occur
                    # Continue with workflow...
                    
        finally:
            shutil.rmtree(temp_dir)
```

## File System Integration Tests

### Test: `test_filesystem_integration.py`

```python
import pytest
from unittest.mock import patch, Mock
import tempfile
import shutil
import os
from pathlib import Path
from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
from pei_docker.gui.models.config import ProjectConfig

class TestFileSystemIntegration:
    """Test suite for file system integration."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        base_temp = tempfile.mkdtemp()
        
        # Create various test directories
        existing_dir = Path(base_temp) / "existing"
        existing_dir.mkdir()
        
        writable_parent = Path(base_temp) / "writable"
        writable_parent.mkdir()
        
        new_project_path = writable_parent / "new_project"
        
        yield {
            "base": base_temp,
            "existing": str(existing_dir),
            "new_project": str(new_project_path),
            "writable_parent": str(writable_parent)
        }
        
        shutil.rmtree(base_temp)
    
    @pytest.mark.integration
    async def test_project_directory_creation_workflow(self, temp_dirs):
        """Test complete project directory creation workflow."""
        config = ProjectConfig()
        mode_screen = ModeSelectionScreen(config)
        
        # Mock UI components
        mock_button = Mock()
        mode_screen.query_one = Mock(return_value=mock_button)
        
        # Simulate user entering new project directory
        mock_event = Mock()
        mock_event.input = Mock()
        mock_event.input.id = "project_dir"
        mock_event.input.value = temp_dirs["new_project"]
        mock_event.value = temp_dirs["new_project"]
        
        # Process input change
        mode_screen.on_input_changed(mock_event)
        
        # Should validate as True (parent exists and is writable)
        assert mode_screen.project_dir_valid == True
        assert mode_screen.project_config.project_dir == temp_dirs["new_project"]
        
        # Simulate continue action
        mode_screen._create_project = Mock(return_value=True)
        
        mock_app = Mock()
        mode_screen.app = mock_app
        
        mode_screen.action_continue()
        
        # Should attempt to create project
        mode_screen._create_project.assert_called_once()
    
    @pytest.mark.integration
    async def test_project_files_copying_integration(self, temp_dirs):
        """Test project template files copying integration."""
        config = ProjectConfig()
        config.project_dir = temp_dirs["new_project"]
        mode_screen = ModeSelectionScreen(config)
        
        # Mock the project template files
        with patch('os.path.exists') as mock_exists:
            with patch('os.listdir') as mock_listdir:
                with patch('shutil.copytree') as mock_copytree:
                    with patch('shutil.copy2') as mock_copy2:
                        
                        # Mock template directory exists
                        mock_exists.return_value = True
                        mock_listdir.return_value = [
                            'installation',
                            'stage-1',
                            'stage-2',
                            'docker-compose-template.yml'
                        ]
                        
                        # Ensure target directory exists
                        Path(temp_dirs["new_project"]).mkdir(exist_ok=True)
                        
                        result = mode_screen._create_project()
                        
                        assert result == True
                        
                        # Verify copying operations were called
                        assert mock_copytree.called or mock_copy2.called
    
    @pytest.mark.integration
    async def test_permission_error_handling(self, temp_dirs):
        """Test handling of file system permission errors."""
        config = ProjectConfig()
        
        # Try to use a path where we don't have write permissions
        readonly_path = "/root/readonly_project"  # Typically not writable
        config.project_dir = readonly_path
        
        mode_screen = ModeSelectionScreen(config)
        
        result = mode_screen._create_project()
        
        # Should gracefully handle permission errors
        assert result == False
    
    @pytest.mark.integration
    async def test_cross_platform_path_handling(self, temp_dirs):
        """Test cross-platform path handling."""
        config = ProjectConfig()
        mode_screen = ModeSelectionScreen(config)
        
        # Test various path formats
        test_paths = [
            temp_dirs["new_project"],  # Standard path
            temp_dirs["new_project"].replace(os.sep, "/"),  # Forward slashes
            temp_dirs["new_project"].replace(os.sep, "\\"),  # Backward slashes
        ]
        
        for test_path in test_paths:
            result = mode_screen._validate_project_dir(test_path)
            # Should handle all path formats correctly
            assert isinstance(result, bool)
    
    @pytest.mark.integration
    async def test_configuration_file_writing_integration(self, temp_dirs):
        """Test configuration file writing integration."""
        from pei_docker.gui.screens.simple.summary import SummaryScreen
        
        config = ProjectConfig(
            project_name="file-test",
            project_dir=temp_dirs["existing"]
        )
        
        # Add some configuration
        config.stage_1.base_image = "python:3.11"
        config.stage_1.ssh.enable = True
        
        summary_screen = SummaryScreen(config)
        mock_app = Mock()
        summary_screen.app = mock_app
        
        result = summary_screen._save_configuration()
        
        assert result == True
        
        # Verify file was created
        config_file = Path(temp_dirs["existing"]) / "user_config.yml"
        assert config_file.exists()
        
        # Verify file permissions (should be readable/writable by user)
        assert config_file.is_file()
        assert os.access(config_file, os.R_OK)
        assert os.access(config_file, os.W_OK)
        
        # Verify file content is valid YAML
        import yaml
        with open(config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert isinstance(saved_config, dict)
        assert "stage_1" in saved_config
    
    @pytest.mark.integration
    async def test_disk_space_consideration(self, temp_dirs):
        """Test handling when disk space might be limited."""
        import yaml
        from pei_docker.gui.screens.simple.summary import SummaryScreen
        
        config = ProjectConfig(
            project_name="large-config-test",
            project_dir=temp_dirs["existing"]
        )
        
        # Create a configuration with many entries
        config.stage_1.ports = [f"{i}:{i+1000}" for i in range(100)]
        config.stage_1.environment = [f"VAR_{i}=value_{i}" for i in range(100)]
        
        summary_screen = SummaryScreen(config)
        mock_app = Mock()
        summary_screen.app = mock_app
        
        result = summary_screen._save_configuration()
        
        # Should handle large configurations
        assert result == True
        
        # Verify file was created and is readable
        config_file = Path(temp_dirs["existing"]) / "user_config.yml"
        assert config_file.exists()
        
        # Verify content is complete
        with open(config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert len(saved_config["stage_1"]["ports"]) == 100
        assert len(saved_config["stage_1"]["environment"]) == 100
```

This comprehensive integration testing plan covers the major interaction patterns and workflows in the PeiDocker GUI. The tests ensure that components work together correctly and that complete user workflows function as expected.