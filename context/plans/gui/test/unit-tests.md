# PeiDocker GUI Unit Testing Plan

## Overview

Unit tests focus on testing individual components and functions in isolation. Each test should be fast, deterministic, and independent of external systems.

## Test Structure Template

```python
# Standard unit test structure
import pytest
from unittest.mock import AsyncMock, Mock, patch
from textual.testing import App

@pytest.mark.unit
async def test_component_basic_functionality():
    """Test basic component functionality."""
    # Arrange
    # Act  
    # Assert
    pass
```

## Main Application (`app.py`)

### Test: `test_app.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.app import PeiDockerApp, main
from pei_docker.gui.models.config import ProjectConfig

class TestPeiDockerApp:
    """Test suite for the main PeiDocker application."""
    
    @pytest.mark.unit
    async def test_app_initialization_default(self):
        """Test app initializes with default settings."""
        app = PeiDockerApp()
        assert app.project_config is not None
        assert app.project_config.project_name == ""
        assert app.project_config.project_dir == ""
    
    @pytest.mark.unit
    async def test_app_initialization_with_project_dir(self):
        """Test app initializes with provided project directory."""
        test_dir = "/test/project/path"
        app = PeiDockerApp(project_dir=test_dir)
        assert app.project_config.project_dir == test_dir
        assert app.project_config.project_name == "path"
    
    @pytest.mark.unit
    async def test_app_screen_installation(self):
        """Test all screens are properly installed."""
        app = PeiDockerApp()
        async with app.run_test() as pilot:
            # Check startup screen is installed
            assert "startup" in app.screen_stack[0].id or "startup" in str(type(app.screen_stack[0]))
    
    @pytest.mark.unit
    async def test_main_function_no_args(self):
        """Test main function with no arguments."""
        with patch('sys.argv', ['pei-docker-gui']):
            with patch.object(PeiDockerApp, 'run') as mock_run:
                main()
                mock_run.assert_called_once()
    
    @pytest.mark.unit
    async def test_main_function_with_project_dir(self):
        """Test main function with project directory argument."""
        test_dir = "/test/project"
        with patch('sys.argv', ['pei-docker-gui', '--project-dir', test_dir]):
            with patch.object(PeiDockerApp, 'run') as mock_run:
                with patch.object(PeiDockerApp, '__init__', return_value=None) as mock_init:
                    main()
                    mock_init.assert_called_once()
```

## Startup Screen (`screens/startup.py`)

### Test: `test_startup_screen.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.screens.startup import StartupScreen
from pei_docker.gui.models.config import ProjectConfig

class TestStartupScreen:
    """Test suite for the startup screen."""
    
    @pytest.mark.unit
    async def test_startup_screen_initialization(self):
        """Test startup screen initializes correctly."""
        config = ProjectConfig()
        screen = StartupScreen(config)
        assert screen.project_config == config
        assert hasattr(screen, 'auto_continue_timer')
    
    @pytest.mark.unit
    async def test_startup_screen_compose(self):
        """Test startup screen composition."""
        config = ProjectConfig()
        screen = StartupScreen(config)
        widgets = list(screen.compose())
        
        # Should have ASCII logo, system status, and buttons
        assert len(widgets) > 0
        # Check for specific widget types if needed
    
    @pytest.mark.unit
    @patch('pei_docker.gui.screens.startup.check_docker_available')
    async def test_startup_screen_docker_available(self, mock_docker_check):
        """Test startup screen when Docker is available."""
        mock_docker_check.return_value = (True, "24.0.6")
        config = ProjectConfig()
        screen = StartupScreen(config)
        
        # Test on_mount behavior
        await screen.on_mount()
        
        # Should start auto-continue timer
        assert screen.auto_continue_timer is not None
    
    @pytest.mark.unit
    @patch('pei_docker.gui.screens.startup.check_docker_available')
    async def test_startup_screen_docker_unavailable(self, mock_docker_check):
        """Test startup screen when Docker is unavailable."""
        mock_docker_check.return_value = (False, None)
        config = ProjectConfig()
        screen = StartupScreen(config)
        
        await screen.on_mount()
        
        # Should show warning and not auto-continue
        assert screen.docker_available == False
    
    @pytest.mark.unit
    async def test_startup_screen_continue_action(self):
        """Test continue action navigation."""
        config = ProjectConfig()
        screen = StartupScreen(config)
        
        # Mock the app's screen switching
        mock_app = Mock()
        screen.app = mock_app
        
        screen.action_continue()
        
        # Should attempt to navigate to mode selection
        mock_app.install_screen.assert_called()
        mock_app.push_screen.assert_called()
    
    @pytest.mark.unit
    async def test_startup_screen_quit_action(self):
        """Test quit action."""
        config = ProjectConfig()
        screen = StartupScreen(config)
        
        mock_app = Mock()
        screen.app = mock_app
        
        screen.action_quit()
        
        mock_app.action_quit_app.assert_called_once()
```

## Mode Selection Screen (`screens/mode_selection.py`)

### Test: `test_mode_selection.py`

```python
import pytest
from unittest.mock import patch, Mock
from pathlib import Path
from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
from pei_docker.gui.models.config import ProjectConfig

class TestModeSelectionScreen:
    """Test suite for the mode selection screen."""
    
    @pytest.mark.unit
    async def test_mode_selection_initialization(self):
        """Test mode selection screen initializes correctly."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        assert screen.project_config == config
        assert screen.selected_mode == "simple"
        assert screen.project_dir_valid == False
    
    @pytest.mark.unit
    async def test_mode_selection_with_existing_project_dir(self):
        """Test mode selection with pre-set project directory."""
        config = ProjectConfig()
        config.project_dir = "/test/project"
        screen = ModeSelectionScreen(config)
        
        assert screen.project_dir_valid == True
    
    @pytest.mark.unit
    async def test_project_dir_validation_valid_path(self):
        """Test project directory validation with valid path."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=True):
                    result = screen._validate_project_dir("/valid/path")
                    assert result == True
    
    @pytest.mark.unit
    async def test_project_dir_validation_invalid_path(self):
        """Test project directory validation with invalid path."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        # Test empty path
        result = screen._validate_project_dir("")
        assert result == False
        
        # Test invalid characters (this might be platform-specific)
        result = screen._validate_project_dir("\\invalid:path*")
        assert result == False
    
    @pytest.mark.unit
    async def test_project_dir_validation_parent_writable(self):
        """Test project directory validation checks parent directory."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        # Mock path that doesn't exist but parent is writable
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.parent') as mock_parent:
                mock_parent.exists.return_value = True
                with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=True):
                    result = screen._validate_project_dir("/new/project/path")
                    assert result == True
    
    @pytest.mark.unit
    async def test_input_changed_project_dir(self):
        """Test input change handling for project directory."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        # Mock the input widget and button
        mock_input = Mock()
        mock_input.id = "project_dir"
        mock_input.value = "/test/project"
        
        mock_button = Mock()
        screen.query_one = Mock(return_value=mock_button)
        
        # Mock validation to return True
        screen._validate_project_dir = Mock(return_value=True)
        
        # Create mock event
        mock_event = Mock()
        mock_event.input = mock_input
        mock_event.value = "/test/project"
        
        screen.on_input_changed(mock_event)
        
        # Should update project config and enable button
        assert screen.project_dir_valid == True
        assert screen.project_config.project_dir == str(Path("/test/project").resolve())
        assert mock_button.disabled == False
    
    @pytest.mark.unit
    async def test_mode_selection_simple(self):
        """Test simple mode selection."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        screen.on_simple_mode_pressed()
        
        assert screen.selected_mode == "simple"
    
    @pytest.mark.unit
    async def test_mode_selection_advanced(self):
        """Test advanced mode selection."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        screen.on_advanced_mode_pressed()
        
        assert screen.selected_mode == "advanced"
    
    @pytest.mark.unit
    @patch('pei_docker.gui.screens.mode_selection.ensure_dir_exists')
    async def test_continue_action_success(self, mock_ensure_dir):
        """Test successful continue action."""
        config = ProjectConfig()
        config.project_dir = "/test/project"
        screen = ModeSelectionScreen(config)
        screen.project_dir_valid = True
        
        mock_ensure_dir.return_value = True
        screen._create_project = Mock(return_value=True)
        
        mock_app = Mock()
        screen.app = mock_app
        
        screen.action_continue()
        
        # Should create project and navigate to wizard
        mock_ensure_dir.assert_called_once()
        screen._create_project.assert_called_once()
        mock_app.install_screen.assert_called()
        mock_app.push_screen.assert_called()
    
    @pytest.mark.unit
    async def test_continue_action_invalid_project_dir(self):
        """Test continue action with invalid project directory."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        screen.project_dir_valid = False
        
        mock_app = Mock()
        screen.app = mock_app
        
        screen.action_continue()
        
        # Should show notification and not navigate
        mock_app.notify.assert_called_with(
            "Please enter a valid project directory first", 
            severity="warning"
        )
    
    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('shutil.copytree')
    @patch('shutil.copy2')
    async def test_create_project_success(self, mock_copy2, mock_copytree, mock_exists):
        """Test successful project creation."""
        config = ProjectConfig()
        config.project_dir = "/test/project"
        screen = ModeSelectionScreen(config)
        
        mock_exists.return_value = True
        
        result = screen._create_project()
        
        assert result == True
        # Should copy project files
        assert mock_copytree.called or mock_copy2.called
    
    @pytest.mark.unit
    async def test_create_project_failure(self):
        """Test project creation failure."""
        config = ProjectConfig()
        config.project_dir = "/invalid/project"
        screen = ModeSelectionScreen(config)
        
        # Mock exception during project creation
        with patch('os.path.exists', side_effect=Exception("Permission denied")):
            result = screen._create_project()
            
            assert result == False
```

## Simple Mode Wizard (`screens/simple/wizard.py`)

### Test: `test_wizard.py`

```python
import pytest
from unittest.mock import Mock, patch
from pei_docker.gui.screens.simple.wizard import SimpleWizardScreen, WizardStep
from pei_docker.gui.models.config import ProjectConfig

class TestWizardStep:
    """Test suite for WizardStep class."""
    
    @pytest.mark.unit
    def test_wizard_step_initialization(self):
        """Test WizardStep initialization."""
        step = WizardStep("test", "Test Step", Mock)
        
        assert step.name == "test"
        assert step.title == "Test Step"
        assert step.screen_class == Mock

class TestSimpleWizardScreen:
    """Test suite for the simple mode wizard."""
    
    @pytest.mark.unit
    async def test_wizard_initialization(self):
        """Test wizard initializes correctly."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        assert wizard.project_config == config
        assert wizard.current_step == 0
        assert len(wizard.steps) == 3  # project_info, ssh_config, summary
        assert len(wizard.step_screens) == len(wizard.steps)
    
    @pytest.mark.unit
    async def test_wizard_steps_creation(self):
        """Test wizard steps are created correctly."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        steps = wizard._create_steps()
        
        assert len(steps) == 3
        assert steps[0].name == "project_info"
        assert steps[1].name == "ssh_config"
        assert steps[2].name == "summary"
    
    @pytest.mark.unit
    async def test_wizard_compose(self):
        """Test wizard screen composition."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        widgets = list(wizard.compose())
        
        # Should have header, content, and navigation
        assert len(widgets) > 0
    
    @pytest.mark.unit
    async def test_wizard_action_back(self):
        """Test back action."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        wizard.current_step = 1
        
        wizard.action_back()
        
        assert wizard.current_step == 0
    
    @pytest.mark.unit
    async def test_wizard_action_back_first_step(self):
        """Test back action on first step (should not change)."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        wizard.current_step = 0
        
        wizard.action_back()
        
        assert wizard.current_step == 0
    
    @pytest.mark.unit
    async def test_wizard_action_next_valid_step(self):
        """Test next action with valid step."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        wizard.current_step = 0
        
        # Mock validation to return True
        wizard._validate_current_step = Mock(return_value=True)
        
        wizard.action_next()
        
        assert wizard.current_step == 1
    
    @pytest.mark.unit
    async def test_wizard_action_next_invalid_step(self):
        """Test next action with invalid step."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        wizard.current_step = 0
        
        # Mock validation to return False
        wizard._validate_current_step = Mock(return_value=False)
        
        mock_app = Mock()
        wizard.app = mock_app
        
        wizard.action_next()
        
        # Should stay on same step and show notification
        assert wizard.current_step == 0
        mock_app.notify.assert_called_with(
            "Please correct the errors before proceeding", 
            severity="warning"
        )
    
    @pytest.mark.unit
    async def test_wizard_action_next_last_step(self):
        """Test next action on last step (should finish)."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        wizard.current_step = 2  # Last step
        
        wizard._validate_current_step = Mock(return_value=True)
        wizard.action_finish = Mock()
        
        wizard.action_next()
        
        wizard.action_finish.assert_called_once()
    
    @pytest.mark.unit
    async def test_wizard_action_finish_valid(self):
        """Test finish action with valid configuration."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        wizard._validate_current_step = Mock(return_value=True)
        
        mock_app = Mock()
        wizard.app = mock_app
        
        wizard.action_finish()
        
        mock_app.notify.assert_called_with(
            "Configuration completed!", 
            severity="information"
        )
    
    @pytest.mark.unit
    async def test_wizard_action_finish_invalid(self):
        """Test finish action with invalid configuration."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        wizard._validate_current_step = Mock(return_value=False)
        
        mock_app = Mock()
        wizard.app = mock_app
        
        wizard.action_finish()
        
        mock_app.notify.assert_called_with(
            "Please correct the errors before finishing", 
            severity="warning"
        )
    
    @pytest.mark.unit
    async def test_wizard_update_step(self):
        """Test step update functionality."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        # Mock the UI components
        wizard.query_one = Mock()
        
        wizard._update_step()
        
        # Should update progress and navigation buttons
        wizard.query_one.assert_called()
    
    @pytest.mark.unit
    async def test_wizard_validate_current_step(self):
        """Test current step validation."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        # Mock step screen with is_valid method
        mock_step_screen = Mock()
        mock_step_screen.is_valid.return_value = True
        wizard.step_screens[0] = mock_step_screen
        
        result = wizard._validate_current_step()
        
        assert result == True
        mock_step_screen.is_valid.assert_called_once()
    
    @pytest.mark.unit
    async def test_wizard_validate_current_step_no_screen(self):
        """Test validation when step screen is None."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        wizard.step_screens[0] = None
        
        result = wizard._validate_current_step()
        
        assert result == True  # Should return True if no screen to validate
    
    @pytest.mark.unit
    async def test_wizard_validate_current_step_no_method(self):
        """Test validation when step screen has no is_valid method."""
        config = ProjectConfig()
        wizard = SimpleWizardScreen(config)
        
        # Mock step screen without is_valid method
        mock_step_screen = Mock()
        del mock_step_screen.is_valid  # Remove the method
        wizard.step_screens[0] = mock_step_screen
        
        result = wizard._validate_current_step()
        
        assert result == True  # Should return True if no validation method
```

## Configuration Models (`models/config.py`)

### Test: `test_config_models.py`

```python
import pytest
from pei_docker.gui.models.config import (
    ProjectConfig, Stage1Config, Stage2Config, SSHConfig, SSHUser
)

class TestSSHUser:
    """Test suite for SSHUser data class."""
    
    @pytest.mark.unit
    def test_ssh_user_initialization(self):
        """Test SSHUser initialization with defaults."""
        user = SSHUser()
        
        assert user.password == ""
        assert user.uid == 1100
        assert user.pubkey_text is None
        assert user.privkey_file is None
    
    @pytest.mark.unit
    def test_ssh_user_custom_values(self):
        """Test SSHUser with custom values."""
        user = SSHUser(
            password="test123",
            uid=1200,
            pubkey_text="ssh-rsa AAAAB3...",
            privkey_file="/path/to/key"
        )
        
        assert user.password == "test123"
        assert user.uid == 1200
        assert user.pubkey_text == "ssh-rsa AAAAB3..."
        assert user.privkey_file == "/path/to/key"

class TestSSHConfig:
    """Test suite for SSHConfig data class."""
    
    @pytest.mark.unit
    def test_ssh_config_initialization(self):
        """Test SSHConfig initialization with defaults."""
        ssh_config = SSHConfig()
        
        assert ssh_config.enable == True
        assert ssh_config.port == 22
        assert ssh_config.host_port == 2222
        assert len(ssh_config.users) == 0
    
    @pytest.mark.unit
    def test_ssh_config_add_user(self):
        """Test adding users to SSH configuration."""
        ssh_config = SSHConfig()
        user = SSHUser(password="test123")
        ssh_config.users["testuser"] = user
        
        assert "testuser" in ssh_config.users
        assert ssh_config.users["testuser"].password == "test123"

class TestStage1Config:
    """Test suite for Stage1Config data class."""
    
    @pytest.mark.unit
    def test_stage1_config_initialization(self):
        """Test Stage1Config initialization with defaults."""
        stage1 = Stage1Config()
        
        assert stage1.base_image == "ubuntu:24.04"
        assert stage1.output_image == ""
        assert isinstance(stage1.ssh, SSHConfig)
        assert stage1.proxy_enable == False
        assert stage1.apt_mirror == "default"
        assert stage1.device_type == "cpu"
        assert len(stage1.ports) == 0
        assert len(stage1.environment) == 0
    
    @pytest.mark.unit
    def test_stage1_config_custom_values(self):
        """Test Stage1Config with custom values."""
        ssh_config = SSHConfig(enable=False)
        stage1 = Stage1Config(
            base_image="python:3.11",
            output_image="my-project:stage-1",
            ssh=ssh_config,
            proxy_enable=True,
            apt_mirror="tuna",
            device_type="gpu"
        )
        
        assert stage1.base_image == "python:3.11"
        assert stage1.output_image == "my-project:stage-1"
        assert stage1.ssh.enable == False
        assert stage1.proxy_enable == True
        assert stage1.apt_mirror == "tuna"
        assert stage1.device_type == "gpu"

class TestStage2Config:
    """Test suite for Stage2Config data class."""
    
    @pytest.mark.unit
    def test_stage2_config_initialization(self):
        """Test Stage2Config initialization with defaults."""
        stage2 = Stage2Config()
        
        assert stage2.output_image == ""
        assert stage2.pixi_enable == False
        assert stage2.conda_enable == False

class TestProjectConfig:
    """Test suite for ProjectConfig data class."""
    
    @pytest.mark.unit
    def test_project_config_initialization(self):
        """Test ProjectConfig initialization with defaults."""
        config = ProjectConfig()
        
        assert config.project_name == ""
        assert config.project_dir == ""
        assert isinstance(config.stage_1, Stage1Config)
        assert isinstance(config.stage_2, Stage2Config)
    
    @pytest.mark.unit
    def test_project_config_custom_values(self):
        """Test ProjectConfig with custom values."""
        config = ProjectConfig(
            project_name="test-project",
            project_dir="/test/path"
        )
        
        assert config.project_name == "test-project"
        assert config.project_dir == "/test/path"
    
    @pytest.mark.unit
    def test_project_config_to_user_config_dict(self):
        """Test conversion to user_config dictionary format."""
        config = ProjectConfig(
            project_name="test-project",
            project_dir="/test/path"
        )
        
        # Add some SSH configuration
        config.stage_1.ssh.enable = True
        config.stage_1.ssh.users["testuser"] = SSHUser(password="test123")
        
        # Add some ports and environment variables
        config.stage_1.ports = ["8080:80"]
        config.stage_1.environment = ["NODE_ENV=production"]
        
        user_config = config.to_user_config_dict()
        
        # Check overall structure
        assert "stage_1" in user_config
        assert "stage_2" in user_config
        
        # Check stage_1 configuration
        stage1 = user_config["stage_1"]
        assert stage1["image"]["base"] == config.stage_1.base_image
        assert stage1["ssh"]["enable"] == True
        assert "testuser" in stage1["ssh"]["users"]
        assert stage1["ssh"]["users"]["testuser"]["password"] == "test123"
        assert stage1["ports"] == ["8080:80"]
        assert stage1["environment"] == ["NODE_ENV=production"]
    
    @pytest.mark.unit
    def test_project_config_to_user_config_dict_disabled_ssh(self):
        """Test conversion with SSH disabled."""
        config = ProjectConfig()
        config.stage_1.ssh.enable = False
        
        user_config = config.to_user_config_dict()
        
        stage1 = user_config["stage_1"]
        assert stage1["ssh"]["enable"] == False
        assert len(stage1["ssh"]["users"]) == 0
    
    @pytest.mark.unit  
    def test_project_config_to_user_config_dict_gpu_device(self):
        """Test conversion with GPU device configuration."""
        config = ProjectConfig()
        config.stage_1.device_type = "gpu"
        
        user_config = config.to_user_config_dict()
        
        stage1 = user_config["stage_1"]
        assert stage1["device"]["type"] == "gpu"
    
    @pytest.mark.unit
    def test_project_config_to_user_config_dict_proxy_enabled(self):
        """Test conversion with proxy enabled."""
        config = ProjectConfig()
        config.stage_1.proxy_enable = True
        config.stage_1.proxy_port = 8080
        config.stage_1.proxy_build_only = True
        
        user_config = config.to_user_config_dict()
        
        stage1 = user_config["stage_1"]
        assert stage1["proxy"]["enable"] == True
        assert stage1["proxy"]["port"] == 8080
        assert stage1["proxy"]["build_only"] == True
    
    @pytest.mark.unit
    def test_project_config_to_user_config_dict_custom_apt_mirror(self):
        """Test conversion with custom APT mirror."""
        config = ProjectConfig()
        config.stage_1.apt_mirror = "tuna"
        
        user_config = config.to_user_config_dict()
        
        stage1 = user_config["stage_1"]
        assert stage1["apt"]["repo_source"] == "tuna"
```

## Utility Tests

### Test: `test_docker_utils.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.utils.docker_utils import check_docker_available

class TestDockerUtils:
    """Test suite for Docker utility functions."""
    
    @pytest.mark.unit
    @patch('subprocess.run')
    def test_check_docker_available_success(self, mock_run):
        """Test Docker availability check when Docker is available."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Docker version 24.0.6, build ed223bc"
        mock_run.return_value = mock_result
        
        available, version = check_docker_available()
        
        assert available == True
        assert "24.0.6" in version
        mock_run.assert_called_with(
            ["docker", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
    
    @pytest.mark.unit
    @patch('subprocess.run')
    def test_check_docker_available_not_found(self, mock_run):
        """Test Docker availability check when Docker is not found."""
        mock_run.side_effect = FileNotFoundError()
        
        available, version = check_docker_available()
        
        assert available == False
        assert version is None
    
    @pytest.mark.unit
    @patch('subprocess.run')
    def test_check_docker_available_permission_error(self, mock_run):
        """Test Docker availability check with permission error."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        available, version = check_docker_available()
        
        assert available == False
        assert version is None
    
    @pytest.mark.unit
    @patch('subprocess.run')
    def test_check_docker_available_timeout(self, mock_run):
        """Test Docker availability check with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["docker", "--version"], 10)
        
        available, version = check_docker_available()
        
        assert available == False
        assert version is None
```

### Test: `test_file_utils.py`

```python
import pytest
from unittest.mock import patch, Mock
from pathlib import Path
from pei_docker.gui.utils.file_utils import (
    ensure_dir_exists, check_path_writable, validate_port_mapping, 
    validate_environment_var, validate_ssh_key
)

class TestFileUtils:
    """Test suite for file utility functions."""
    
    @pytest.mark.unit
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_ensure_dir_exists_creates_directory(self, mock_exists, mock_mkdir):
        """Test directory creation when it doesn't exist."""
        mock_exists.return_value = False
        
        result = ensure_dir_exists("/test/path")
        
        assert result == True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
    @pytest.mark.unit
    @patch('pathlib.Path.exists')
    def test_ensure_dir_exists_already_exists(self, mock_exists):
        """Test when directory already exists."""
        mock_exists.return_value = True
        
        result = ensure_dir_exists("/test/path")
        
        assert result == True
    
    @pytest.mark.unit
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_ensure_dir_exists_permission_error(self, mock_exists, mock_mkdir):
        """Test directory creation with permission error."""
        mock_exists.return_value = False
        mock_mkdir.side_effect = PermissionError()
        
        result = ensure_dir_exists("/test/path")
        
        assert result == False
    
    @pytest.mark.unit
    def test_validate_port_mapping_single_port(self):
        """Test validation of single port mapping."""
        assert validate_port_mapping("8080:80") == True
        assert validate_port_mapping("3000:3000") == True
        assert validate_port_mapping("1234:5678") == True
    
    @pytest.mark.unit
    def test_validate_port_mapping_port_range(self):
        """Test validation of port range mapping."""
        assert validate_port_mapping("100-200:300-400") == True
        assert validate_port_mapping("1000-1010:2000-2010") == True
    
    @pytest.mark.unit
    def test_validate_port_mapping_invalid_format(self):
        """Test validation of invalid port mapping formats."""
        assert validate_port_mapping("invalid") == False
        assert validate_port_mapping("8080") == False
        assert validate_port_mapping("8080:") == False
        assert validate_port_mapping(":80") == False
        assert validate_port_mapping("abc:def") == False
    
    @pytest.mark.unit
    def test_validate_port_mapping_invalid_range(self):
        """Test validation of invalid port ranges."""
        assert validate_port_mapping("0:80") == False  # Port 0 invalid
        assert validate_port_mapping("8080:65536") == False  # Port too high
        assert validate_port_mapping("200-100:300-400") == False  # Invalid range
    
    @pytest.mark.unit
    def test_validate_environment_var_valid(self):
        """Test validation of valid environment variables."""
        assert validate_environment_var("KEY=value") == True
        assert validate_environment_var("NODE_ENV=production") == True
        assert validate_environment_var("DEBUG=true") == True
        assert validate_environment_var("PATH=/usr/bin:/bin") == True
    
    @pytest.mark.unit
    def test_validate_environment_var_invalid(self):
        """Test validation of invalid environment variables."""
        assert validate_environment_var("invalid") == False
        assert validate_environment_var("KEY=") == True  # Empty value is valid
        assert validate_environment_var("=value") == False  # Empty key invalid
        assert validate_environment_var("") == False  # Empty string invalid
    
    @pytest.mark.unit
    def test_validate_ssh_key_valid_rsa(self):
        """Test validation of valid RSA SSH key."""
        rsa_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... user@host"
        assert validate_ssh_key(rsa_key) == True
    
    @pytest.mark.unit
    def test_validate_ssh_key_valid_ed25519(self):
        """Test validation of valid Ed25519 SSH key."""
        ed25519_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@host"
        assert validate_ssh_key(ed25519_key) == True
    
    @pytest.mark.unit
    def test_validate_ssh_key_invalid(self):
        """Test validation of invalid SSH keys."""
        assert validate_ssh_key("invalid-key") == False
        assert validate_ssh_key("ssh-rsa") == False  # Missing key data
        assert validate_ssh_key("") == False  # Empty string
        assert validate_ssh_key("rsa-ssh AAAAB3...") == False  # Wrong prefix
    
    @pytest.mark.unit
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_check_path_writable_file(self, mock_is_file, mock_exists):
        """Test path writability check for existing file."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        with patch('builtins.open', Mock()):
            result = check_path_writable("/test/file.txt")
            assert result == True
    
    @pytest.mark.unit
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_check_path_writable_directory(self, mock_is_dir, mock_exists):
        """Test path writability check for existing directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        
        with patch('tempfile.NamedTemporaryFile'):
            result = check_path_writable("/test/dir")
            assert result == True
    
    @pytest.mark.unit
    def test_check_path_writable_permission_error(self):
        """Test path writability check with permission error."""
        with patch('builtins.open', side_effect=PermissionError()):
            result = check_path_writable("/test/file.txt")
            assert result == False
```

This comprehensive unit testing plan covers all the major components of the implemented GUI system. Each test suite focuses on a specific component and tests both happy paths and error conditions, ensuring robust coverage of the functionality.