# Textual GUI Ecosystem Tools & Libraries Guide

This guide covers useful libraries, tools, and best practices within the Textual ecosystem that can help you implement your PeiDocker GUI project more effectively, following best practices and simplifying development.

## Why These Tools Matter for PeiDocker GUI

The PeiDocker GUI needs to handle complex Docker container configuration with multiple modes (Simple wizard-based, Advanced form-based), file system operations, validation, and real-time Docker integration. The Textual ecosystem provides exactly the tools needed to build this sophisticated interface while maintaining type safety and user experience.

## Core Textual Development Tools

### 1. textual-dev
**Purpose**: Development and debugging tools for Textual applications
**Installation**: `pip install textual-dev`

**Why Essential for PeiDocker GUI**:
The PeiDocker GUI is complex, with multiple screens, wizard flows, and advanced configuration options. You need robust debugging capabilities to handle the intricate state management between wizard steps, validate Docker configurations, and troubleshoot user interactions across different modes.

**Key Features**:
- **Dev Console**: `textual console` - Connect to your running Textual app for debugging
- **Live reloading**: Automatically reload your app when code changes
- **CSS inspector**: Inspect styles and layout in real-time
- **Event monitoring**: Watch events and messages in your app

**PeiDocker-Specific Usage Examples**:
```bash
# Debug the PeiDocker GUI with live console access
textual run --dev src/pei_docker/gui/app.py --project-dir ./test-project

# In another terminal, monitor wizard state changes
textual console
# Then in console:
>>> app.project_config.stage_1.ssh.enabled  # Check SSH configuration state
>>> app.current_wizard_step  # See which wizard step is active
```

**Real-World Benefits**:
- Debug wizard navigation issues when users skip steps
- Monitor Docker API calls during build monitoring
- Inspect CSS layout problems in complex forms
- Watch reactive variable changes during configuration updates

### 2. textual-serve
**Purpose**: Serve Textual apps on the web
**Installation**: Built into Textual

**Usage**:
```bash
# Serve your app on the web
textual serve your_app.py

# Serve with custom port
textual serve your_app.py --port 8080
```

## Third-Party Widget Libraries

### 1. textual-fspicker 🌟
**Purpose**: File and directory selection dialogs (already covered in detail)
**Installation**: `pip install textual-fspicker`

**Why Critical for PeiDocker GUI**:
PeiDocker heavily relies on file system operations - users need to select project directories, choose SSH key files, browse for custom scripts, select mount points, and pick configuration templates. Manual path typing is error-prone and user-unfriendly.

**Key Components**:
- `FileOpen` - Open file dialog
- `FileSave` - Save file dialog  
- `SelectDirectory` - Directory selection dialog
- Built-in filtering and validation

**PeiDocker-Specific Use Cases**:
```python
# Project directory selection on startup
class ProjectDirectoryScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        yield SelectDirectory(title="Choose Project Directory")
    
    def on_select_directory_selected(self, event) -> None:
        self.dismiss(str(event.path))

# SSH key file selection in advanced mode
class SSHKeySelector(Static):
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Input(placeholder="SSH key path", id="key_path")
            yield Button("Browse...", id="browse_key")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse_key":
            self.app.push_screen_wait(
                FileOpen(title="Select SSH Key", path=Path.home() / ".ssh")
            ).then(self.on_key_selected)
    
    def on_key_selected(self, key_path: str) -> None:
        self.query_one("#key_path", Input).value = key_path

# Custom script file selection for build hooks
class CustomScriptSelector(Static):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_script":
            self.app.push_screen_wait(
                FileOpen(
                    title="Select Build Script",
                    path=self.project_dir / "scripts",
                    file_types=[".sh", ".py", ".bash"]
                )
            ).then(self.add_script_to_config)
```

**Real-World Benefits**:
- Eliminates path typing errors in project setup
- Provides visual navigation for SSH key selection
- Enables browsing Docker volumes and mount points
- Supports script file selection for custom build hooks

### 2. textual-inputs
**Purpose**: Extended input widgets collection
**Installation**: `pip install textual-inputs`

**Why Valuable for PeiDocker GUI**:
PeiDocker requires specialized inputs - port ranges (2222:22), environment variables (KEY=value), package lists, and numeric constraints (UIDs 1-65535). Standard text inputs require extensive custom validation, while textual-inputs provides pre-built, validated widgets.

**Key Components & PeiDocker Use Cases**:
```python
from textual_inputs import NumberInput, DateInput, EmailInput

class PortMappingForm(Static):
    """Port mapping configuration with specialized inputs."""
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("SSH Port Mapping:")
            with Horizontal():
                yield NumberInput(
                    placeholder="Host port (1-65535)",
                    minimum=1,
                    maximum=65535,
                    id="host_port"
                )
                yield Static(":")
                yield NumberInput(
                    placeholder="Container port",
                    minimum=1,
                    maximum=65535, 
                    id="container_port"
                )

class UserAccountForm(Static):
    """SSH user account configuration."""
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(placeholder="Username", id="username")
            yield NumberInput(
                placeholder="User ID (1000-65535)",
                minimum=1000,
                maximum=65535,
                id="uid"
            )
            yield Input(placeholder="Password", password=True, id="password")
            yield EmailInput(placeholder="Email (optional)", id="email")

# Custom validation for Docker-specific formats
class DockerImageInput(Input):
    """Specialized input for Docker image names."""
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.failure("Docker image name is required")
        
        # Validate Docker image name format
        if not re.match(r'^[a-z0-9]+([\._-][a-z0-9]+)*(/[a-z0-9]+([\._-][a-z0-9]+)*)*(:[\w][\w.-]{0,127})?$', value):
            return self.failure("Invalid Docker image name format")
        
        return self.success()

class EnvironmentVariableInput(Input):
    """Specialized input for environment variables (KEY=value format)."""
    def validate(self, value: str) -> ValidationResult:
        if not value:
            return self.success()  # Optional
        
        if '=' not in value:
            return self.failure("Format: KEY=value")
        
        key, _ = value.split('=', 1)
        if not key.replace('_', '').isalnum():
            return self.failure("Environment variable key must be alphanumeric with underscores")
        
        return self.success()
```

**Real-World Benefits**:
- **Port Range Validation**: Prevents invalid port numbers (>65535)
- **User ID Constraints**: Enforces Linux UID ranges automatically
- **Docker Image Format**: Real-time validation of image name syntax
- **Environment Variables**: Ensures KEY=value format compliance

### 3. textual-forms 🌟
**Purpose**: Form creation and validation framework
**Installation**: `pip install textual-forms`

**Key Features**:
- Automatic form generation from data models
- Built-in validation
- Form state management
- Easy form submission handling

**Usage Example**:
```python
from textual_forms import FormScreen
from pydantic import BaseModel

class ProjectConfig(BaseModel):
    name: str
    base_image: str = "ubuntu:24.04"
    use_ssh: bool = True
    ssh_port: int = 2222

class ConfigForm(FormScreen[ProjectConfig]):
    def __init__(self):
        super().__init__(
            model=ProjectConfig,
            title="Project Configuration"
        )
    
    def on_form_submit(self, event) -> None:
        # Handle form submission
        config = event.data
        self.dismiss(config)
```

### 4. textual-plotext / textual-plot
**Purpose**: Data visualization and plotting in terminal
**Installation**: `pip install textual-plotext` or `pip install textual-plot`

**Usage**:
```python
from textual_plotext import PlotextPlot

class ChartWidget(Static):
    def compose(self) -> ComposeResult:
        yield PlotextPlot()
    
    def on_mount(self) -> None:
        plt = self.query_one(PlotextPlot).plt
        plt.scatter([1, 2, 3, 4], [1, 4, 2, 3])
        plt.title("Sample Data")
```

## Configuration & Data Management

### 1. Pydantic for Configuration Management 🌟
**Purpose**: Type-safe configuration and validation
**Installation**: `pip install pydantic`

**Why Essential for PeiDocker GUI**:
PeiDocker's `user_config.yml` is complex with nested structures (Stage-1/Stage-2 configs, SSH settings, proxy configs, port mappings, environment variables). Manual validation is error-prone and the GUI needs real-time validation with helpful error messages. Pydantic provides exactly this - type-safe models with automatic validation.

**Benefits for your project**:
- Type-safe configuration models that match your YAML structure
- Automatic validation with detailed error messages
- Environment variable loading for app settings
- JSON/YAML serialization for saving configurations
- Integration with Textual's reactive system

**Real-World PeiDocker Examples**:
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from pathlib import Path

class SSHUserConfig(BaseModel):
    """SSH user configuration matching PeiDocker's user_config.yml structure."""
    password: str = Field(..., min_length=1, description="SSH password")
    uid: int = Field(1100, ge=1, le=65535, description="User ID")
    public_key: Optional[str] = Field(None, description="SSH public key content")
    private_key_path: Optional[Path] = Field(None, description="Path to private key")
    shell: str = Field("/bin/bash", description="Default shell")
    sudo: bool = Field(True, description="Sudo privileges")

    @validator('password')
    def validate_password(cls, v):
        if ',' in v or ' ' in v:
            raise ValueError('Password cannot contain commas or spaces (Docker limitation)')
        return v
    
    @validator('private_key_path')
    def validate_key_path(cls, v):
        if v and not v.exists():
            raise ValueError(f'SSH key file not found: {v}')
        return v

class SSHConfig(BaseModel):
    """SSH configuration section."""
    enabled: bool = True
    container_port: int = Field(22, ge=1, le=65535)
    host_port: int = Field(2222, ge=1, le=65535)
    users: Dict[str, SSHUserConfig] = {}
    root_login: bool = False
    root_password: Optional[str] = None

    @validator('host_port')
    def validate_host_port(cls, v, values):
        # Check for common port conflicts
        if v in [80, 443, 8080, 3000]:
            raise ValueError(f'Port {v} is commonly used by other services')
        return v

class ProxyConfig(BaseModel):
    """Proxy configuration for build and runtime."""
    enabled: bool = False
    port: Optional[int] = Field(None, ge=1, le=65535)
    build_only: bool = True
    no_proxy: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1", ".local"])

class Stage1Config(BaseModel):
    """Stage-1 configuration section."""
    base_image: str = "ubuntu:24.04"
    ssh: SSHConfig = Field(default_factory=SSHConfig)
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    ports: List[str] = Field(default_factory=list)
    environment: Dict[str, str] = Field(default_factory=dict)
    apt_mirror: Optional[str] = None
    packages: List[str] = Field(default_factory=list)

    @validator('base_image')
    def validate_base_image(cls, v):
        # Basic Docker image name validation
        if not v or '/' not in v and ':' not in v:
            if not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Invalid Docker image name format')
        return v

class ProjectConfig(BaseModel):
    """Complete PeiDocker project configuration."""
    project_name: str = Field(..., min_length=1)
    project_dir: str = Field(..., min_length=1) 
    stage_1: Stage1Config = Field(default_factory=Stage1Config)
    
    @validator('project_name')
    def validate_project_name(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Project name must be alphanumeric with hyphens/underscores only')
        return v
    
    def to_yaml(self) -> dict:
        """Convert to PeiDocker user_config.yml format."""
        return {
            'stage_1': self.stage_1.dict(),
            # Add stage_2 when implemented
        }

# Usage in your Textual GUI screens
class SSHConfigurationScreen(Screen):
    def __init__(self, config: ProjectConfig):
        super().__init__()
        self.config = config
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "validate_ssh":
            try:
                # Validate SSH configuration in real-time
                ssh_data = self.collect_ssh_form_data()
                validated_ssh = SSHConfig(**ssh_data)
                self.config.stage_1.ssh = validated_ssh
                self.notify("✅ SSH configuration is valid!", severity="information")
            except ValidationError as e:
                error_details = "\n".join([f"• {err['msg']}" for err in e.errors()])
                self.notify(f"❌ SSH Configuration Error:\n{error_details}", severity="error")

class ProjectSummaryScreen(Screen):
    def save_configuration(self) -> None:
        """Save validated configuration to user_config.yml."""
        try:
            # Pydantic automatically validates the entire configuration
            validated_config = ProjectConfig(**self.collect_all_form_data())
            
            # Save to YAML file
            config_path = Path(validated_config.project_dir) / "user_config.yml"
            with open(config_path, 'w') as f:
                yaml.dump(validated_config.to_yaml(), f, default_flow_style=False)
            
            self.notify(f"✅ Configuration saved to {config_path}")
            
        except ValidationError as e:
            # Show detailed validation errors
            error_summary = self.format_validation_errors(e)
            self.app.push_screen(ErrorDialog("Configuration Validation Failed", error_summary))
```

**Integration with Textual Reactive System**:
```python
from textual.reactive import reactive

class ConfigurationState:
    """Reactive configuration state management."""
    project_config: reactive[ProjectConfig] = reactive(ProjectConfig())
    
    def watch_project_config(self, old_config: ProjectConfig, new_config: ProjectConfig) -> None:
        """React to configuration changes."""
        # Auto-save on changes
        if new_config.project_name and new_config.project_dir:
            self.auto_save_config(new_config)

class PeiDockerApp(App):
    def __init__(self):
        super().__init__()
        self.config_state = ConfigurationState()
```

**Real-World Benefits for PeiDocker GUI**:
- **Prevents Invalid Configurations**: Catches SSH port conflicts, invalid Docker image names, missing key files
- **Rich Error Messages**: Instead of "invalid input", users see "Port 22 conflicts with container SSH port"
- **Type Safety**: Eliminates runtime errors from configuration mismatches
- **Auto-completion Support**: IDEs can provide intelligent suggestions for configuration fields
- **Seamless YAML Integration**: Direct conversion to/from PeiDocker's user_config.yml format
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from pathlib import Path

class SSHConfig(BaseModel):
    enabled: bool = True
    container_port: int = Field(22, ge=1, le=65535)
    host_port: int = Field(2222, ge=1, le=65535)
    username: str = "me"
    password: str = Field("123456", min_length=1)
    public_key: Optional[str] = None
    private_key_path: Optional[Path] = None
    root_login: bool = False
    root_password: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if ',' in v or ' ' in v:
            raise ValueError('Password cannot contain commas or spaces')
        return v

class ProxyConfig(BaseModel):
    enabled: bool = False
    port: Optional[int] = Field(None, ge=1, le=65535)
    build_only: bool = True

class ProjectConfig(BaseModel):
    name: str = Field(..., min_length=1)
    base_image: str = "ubuntu:24.04"
    ssh: SSHConfig = SSHConfig()
    proxy: ProxyConfig = ProxyConfig()
    use_gpu: bool = False
    
    # Additional validations
    @validator('name')
    def validate_project_name(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Project name must be alphanumeric with hyphens/underscores')
        return v

# Usage in your GUI
class ConfigurationScreen(ModalScreen[ProjectConfig]):
    def __init__(self):
        super().__init__()
        self.config = ProjectConfig()
    
    def validate_and_save(self) -> None:
        try:
            # Pydantic automatically validates
            validated_config = ProjectConfig(**self.get_form_data())
            self.dismiss(validated_config)
        except ValidationError as e:
            self.notify(f"Validation error: {e}")
```

### 2. Pydantic Settings for Environment Variables
```python
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    docker_available: bool = True
    default_project_dir: Path = Path.cwd()
    config_template_path: Path = Path("templates/config-template-full.yml")
    
    class Config:
        env_prefix = "PEIDOCKER_"
        env_file = ".env"

# Usage
settings = AppSettings()
```

## State Management & Architecture

### 1. Reactive Variables for State Management
**Why Critical for PeiDocker GUI**:
PeiDocker's GUI has complex state relationships - changing the base image affects available packages, enabling SSH updates port requirements, proxy settings influence build scripts. Without proper state management, the GUI becomes buggy with inconsistent data across screens.

**PeiDocker-Specific State Management Examples**:
```python
from textual.reactive import reactive

class PeiDockerConfigurationState:
    """Centralized state management for PeiDocker GUI."""
    
    # Project-level state
    project_name: reactive[str] = reactive("")
    project_dir: reactive[str] = reactive("")
    base_image: reactive[str] = reactive("ubuntu:24.04")
    
    # SSH state with cascading effects
    ssh_enabled: reactive[bool] = reactive(True)
    ssh_host_port: reactive[int] = reactive(2222)
    ssh_users: reactive[dict] = reactive({})
    
    # Build-related state
    docker_available: reactive[bool] = reactive(False)
    build_in_progress: reactive[bool] = reactive(False)
    current_wizard_step: reactive[int] = reactive(0)
    
    # Advanced mode state
    advanced_mode_tab: reactive[str] = reactive("stage1")
    validation_errors: reactive[list] = reactive([])

    def watch_ssh_enabled(self, old_enabled: bool, new_enabled: bool) -> None:
        """React to SSH enablement changes."""
        if not new_enabled:
            # Clear SSH-related configurations when disabled
            self.ssh_users = {}
            self.ssh_host_port = 0
            self.notify("SSH disabled - related settings cleared")
    
    def watch_base_image(self, old_image: str, new_image: str) -> None:
        """React to base image changes."""
        if "gpu" in new_image.lower() or "cuda" in new_image.lower():
            self.notify("GPU image detected - GPU configuration available")
        
        if "ubuntu" in new_image:
            self.default_packages = ["curl", "wget", "git", "vim"]
        elif "alpine" in new_image:
            self.default_packages = ["curl", "wget", "git", "vim"]
    
    def watch_build_in_progress(self, old_status: bool, new_status: bool) -> None:
        """React to build status changes."""
        if new_status:
            # Disable form modifications during build
            self.lock_configuration = True
        else:
            self.lock_configuration = False

class PeiDockerApp(App):
    def __init__(self):
        super().__init__()
        self.config_state = PeiDockerConfigurationState()
        
        # Bind state changes to UI updates
        self.config_state.watch_ssh_enabled = self.on_ssh_state_changed
        self.config_state.watch_docker_available = self.on_docker_state_changed

    def on_ssh_state_changed(self, old_enabled: bool, new_enabled: bool) -> None:
        """Update UI when SSH state changes."""
        ssh_screen = self.screen_stack[-1]
        if hasattr(ssh_screen, 'update_ssh_options'):
            ssh_screen.update_ssh_options(new_enabled)

# Usage in wizard screens
class SSHConfigurationStep(Screen):
    def __init__(self, config_state: PeiDockerConfigurationState):
        super().__init__()
        self.config_state = config_state
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "enable_ssh":
            # This triggers the reactive watch method automatically
            self.config_state.ssh_enabled = event.value
    
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "ssh_port":
            try:
                port = int(event.value)
                if 1 <= port <= 65535:
                    self.config_state.ssh_host_port = port
                else:
                    self.notify("Port must be between 1-65535", severity="error")
            except ValueError:
                self.notify("Invalid port number", severity="error")
```

**Real-World Benefits for PeiDocker**:
- **Consistent State**: SSH settings stay synchronized across wizard steps
- **Automatic Validation**: Changing base image triggers package compatibility checks
- **UI Synchronization**: Enable/disable controls based on current configuration
- **Build State Management**: Lock UI during Docker builds to prevent conflicts

### 2. Message-Based Communication
```python
from textual.message import Message

class ConfigUpdated(Message):
    """Message sent when configuration is updated"""
    def __init__(self, config: ProjectConfig) -> None:
        self.config = config
        super().__init__()

class ConfigurationForm(Static):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            config = self.build_config()
            self.post_message(ConfigUpdated(config))

class MainApp(App):
    def on_config_updated(self, message: ConfigUpdated) -> None:
        """Handle configuration updates"""
        self.save_config(message.config)
        self.notify("Configuration saved!")
```

## Advanced Widget Patterns

### 1. Custom Validation Widgets
```python
from textual.validation import ValidationResult, Validator

class PortValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            port = int(value)
            if 1 <= port <= 65535:
                return self.success()
            else:
                return self.failure("Port must be between 1 and 65535")
        except ValueError:
            return self.failure("Must be a valid number")

class ValidatedInput(Input):
    def __init__(self, placeholder: str, validator: Validator, **kwargs):
        super().__init__(placeholder=placeholder, validators=[validator], **kwargs)
```

### 2. Wizard/Step-by-Step Components
**Why Essential for PeiDocker Simple Mode**:
PeiDocker's Simple Mode is designed as a 15-step wizard (Project Info → SSH Config → Proxy → APT → Ports → Environment → Device → Mounts → Scripts → Summary). Users need clear progress indication, validation at each step, and the ability to navigate back to make changes.

**PeiDocker Wizard Implementation**:
```python
from dataclasses import dataclass
from typing import Type, Optional

@dataclass
class WizardStep:
    """Represents a step in the PeiDocker configuration wizard."""
    name: str
    title: str
    screen_class: Type[Screen]
    is_optional: bool = False
    requires_docker: bool = False
    
class PeiDockerWizard(Static):
    """15-step configuration wizard for PeiDocker Simple Mode."""
    
    def __init__(self, config_state: PeiDockerConfigurationState):
        super().__init__()
        self.config_state = config_state
        self.steps = [
            WizardStep("project_info", "Project Information", ProjectInfoStep),
            WizardStep("ssh_config", "SSH Configuration", SSHConfigStep),
            WizardStep("ssh_users", "SSH User Details", SSHUsersStep),
            WizardStep("ssh_root", "SSH Root Access", SSHRootStep, is_optional=True),
            WizardStep("proxy_config", "Proxy Configuration", ProxyConfigStep, is_optional=True),
            WizardStep("apt_config", "APT Configuration", APTConfigStep, is_optional=True),
            WizardStep("port_mapping", "Port Mapping", PortMappingStep, is_optional=True),
            WizardStep("environment", "Environment Variables", EnvironmentStep, is_optional=True),
            WizardStep("device_config", "Device Configuration", DeviceConfigStep),
            WizardStep("stage1_mounts", "Stage-1 Mounts", Stage1MountsStep, is_optional=True),
            WizardStep("entry_point", "Custom Entry Point", EntryPointStep, is_optional=True),
            WizardStep("custom_scripts", "Custom Scripts", CustomScriptsStep, is_optional=True),
            WizardStep("summary", "Configuration Summary", ConfigSummaryStep),
        ]
        self.current_step = 0
    
    def compose(self) -> ComposeResult:
        with Vertical():
            # Progress indicator
            yield Static(f"Step {self.current_step + 1} of {len(self.steps)}: {self.current_step_title}")
            yield ProgressBar(total=len(self.steps), progress=self.current_step + 1)
            
            # Current step content
            yield Container(self.current_step_screen, id="step_content")
            
            # Navigation buttons
            with Horizontal(id="navigation"):
                yield Button("Back", id="back", disabled=self.current_step == 0)
                yield Button("Skip", id="skip", disabled=not self.current_step_optional)
                yield Button("Next", id="next", variant="primary")
    
    @property
    def current_step_screen(self) -> Screen:
        """Get the current step's screen instance."""
        step = self.steps[self.current_step]
        return step.screen_class(self.config_state)
    
    @property
    def current_step_title(self) -> str:
        """Get the current step's title."""
        return self.steps[self.current_step].title
    
    @property 
    def current_step_optional(self) -> bool:
        """Check if current step is optional."""
        return self.steps[self.current_step].is_optional
    
    def validate_current_step(self) -> tuple[bool, Optional[str]]:
        """Validate the current step's data."""
        current_screen = self.current_step_screen
        if hasattr(current_screen, 'validate_step'):
            return current_screen.validate_step()
        return True, None
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next":
            is_valid, error_msg = self.validate_current_step()
            if is_valid:
                self.next_step()
            else:
                self.notify(f"Validation Error: {error_msg}", severity="error")
        
        elif event.button.id == "back":
            self.previous_step()
        
        elif event.button.id == "skip":
            if self.current_step_optional:
                self.next_step()
    
    def next_step(self) -> None:
        """Move to the next wizard step."""
        if self.current_step < len(self.steps) - 1:
            # Save current step data
            self.save_current_step_data()
            
            self.current_step += 1
            self.refresh_step_content()
            
            # Check if final step
            if self.current_step == len(self.steps) - 1:
                self.query_one("#next", Button).label = "Finish"
        else:
            # Final step - save configuration
            self.complete_wizard()
    
    def previous_step(self) -> None:
        """Move to the previous wizard step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.refresh_step_content()
            self.query_one("#next", Button).label = "Next"
    
    def refresh_step_content(self) -> None:
        """Refresh the step content area."""
        content_container = self.query_one("#step_content", Container)
        content_container.remove_children()
        content_container.mount(self.current_step_screen)
        
        # Update navigation buttons
        self.query_one("#back", Button).disabled = (self.current_step == 0)
        self.query_one("#skip", Button).disabled = not self.current_step_optional
        
        # Update progress
        progress_bar = self.query_one(ProgressBar)
        progress_bar.progress = self.current_step + 1
        
        # Update title
        title_label = self.query_one(Static)
        title_label.update(f"Step {self.current_step + 1} of {len(self.steps)}: {self.current_step_title}")

# Individual step implementations
class ProjectInfoStep(Screen):
    """Step 1: Project name and base Docker image."""
    
    def __init__(self, config_state: PeiDockerConfigurationState):
        super().__init__()
        self.config_state = config_state
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Configure your PeiDocker project:")
            yield Input(placeholder="Project name", id="project_name", value=self.config_state.project_name)
            yield Input(placeholder="Base Docker image", id="base_image", value=self.config_state.base_image)
            
            yield Static("Popular base images:")
            with Vertical():
                yield Static("• ubuntu:24.04 - Latest Ubuntu LTS")
                yield Static("• nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04 - GPU support")
                yield Static("• python:3.11-slim - Python runtime")
    
    def validate_step(self) -> tuple[bool, Optional[str]]:
        """Validate project information."""
        project_name = self.query_one("#project_name", Input).value.strip()
        base_image = self.query_one("#base_image", Input).value.strip()
        
        if not project_name:
            return False, "Project name is required"
        
        if not project_name.replace('-', '').replace('_', '').isalnum():
            return False, "Project name must be alphanumeric with hyphens/underscores only"
        
        if not base_image:
            return False, "Base Docker image is required"
        
        # Save to state
        self.config_state.project_name = project_name
        self.config_state.base_image = base_image
        
        return True, None

class SSHConfigStep(Screen):
    """Step 2: SSH configuration."""
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Configure SSH access to your container:")
            yield Checkbox("Enable SSH access", id="enable_ssh", value=self.config_state.ssh_enabled)
            
            with Container(id="ssh_options"):
                if self.config_state.ssh_enabled:
                    yield NumberInput(placeholder="Host port (default: 2222)", id="ssh_port", value=str(self.config_state.ssh_host_port))
                    yield Static("SSH will be available at localhost:{port}")
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "enable_ssh":
            self.config_state.ssh_enabled = event.value
            self.update_ssh_options()
    
    def update_ssh_options(self) -> None:
        """Show/hide SSH options based on enabled state."""
        options_container = self.query_one("#ssh_options", Container)
        options_container.remove_children()
        
        if self.config_state.ssh_enabled:
            options_container.mount(NumberInput(placeholder="Host port (default: 2222)", id="ssh_port"))
            options_container.mount(Static("SSH will be available at localhost:{port}"))
```

**Real-World Benefits for PeiDocker**:
- **Clear Progress**: Users see exactly where they are in the 15-step process
- **Flexible Navigation**: Can go back to modify earlier settings
- **Optional Steps**: Skip advanced configurations in Simple Mode
- **Step Validation**: Prevents moving forward with invalid data
- **State Persistence**: Configuration preserved across navigation

## Development Best Practices

### 1. Project Structure
```
src/pei_docker/gui/
├── __init__.py
├── app.py              # Main application class
├── config/
│   ├── __init__.py
│   ├── models.py       # Pydantic models
│   └── settings.py     # App settings
├── widgets/
│   ├── __init__.py
│   ├── forms.py        # Custom form widgets
│   ├── inputs.py       # Custom input widgets
│   └── dialogs.py      # Modal dialogs
├── screens/
│   ├── __init__.py
│   ├── main.py         # Main screen
│   ├── wizard.py       # Configuration wizard
│   └── advanced.py     # Advanced mode screen
├── utils/
│   ├── __init__.py
│   ├── validation.py   # Custom validators
│   └── docker_utils.py # Docker-related utilities
└── assets/
    ├── app.css         # Main stylesheet
    └── themes/         # Custom themes
```

### 2. Configuration Loading Pattern
```python
class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.config_path = project_dir / "user_config.yml"
    
    def load_config(self) -> Optional[ProjectConfig]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                import yaml
                with open(self.config_path) as f:
                    data = yaml.safe_load(f)
                return ProjectConfig(**data)
            except Exception as e:
                # Handle loading errors
                return None
        return None
    
    def save_config(self, config: ProjectConfig) -> bool:
        """Save configuration to file"""
        try:
            import yaml
            with open(self.config_path, 'w') as f:
                yaml.dump(config.dict(), f, default_flow_style=False)
            return True
        except Exception as e:
            return False
```

### 3. Error Handling Pattern
```python
class ErrorDialog(ModalScreen[None]):
    def __init__(self, title: str, message: str):
        super().__init__()
        self.title = title
        self.message = message
    
    def compose(self) -> ComposeResult:
        with Grid(id="error-dialog"):
            yield Static(self.title, classes="dialog-title")
            yield Static(self.message, classes="dialog-message")
            yield Button("OK", variant="primary", id="ok")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

# Usage in main app
class MainApp(App):
    async def show_error(self, title: str, message: str) -> None:
        """Show error dialog"""
        await self.push_screen_wait(ErrorDialog(title, message))
    
    def handle_docker_error(self, error: Exception) -> None:
        """Handle Docker-related errors"""
        self.call_later(self.show_error, "Docker Error", str(error))
```

## Testing Tools

### 1. Textual Testing
```python
from textual.app import App
from textual.testing import AppTestCase

class TestPeiDockerGUI(AppTestCase):
    def test_app_startup(self):
        """Test app starts correctly"""
        app = PeiDockerApp()
        with app.test() as pilot:
            # Test initial state
            assert app.title == "PeiDocker GUI"
    
    def test_project_creation(self):
        """Test project creation workflow"""
        app = PeiDockerApp()
        with app.test() as pilot:
            # Simulate user interactions
            pilot.click("#create-project")
            pilot.type("my-test-project")
            pilot.press("enter")
            
            # Assert expected state
            assert app.config_state.project_name == "my-test-project"
```

## Recommended Library Combinations

### For Your PeiDocker GUI Project:

**Why These Specific Tools Matter**:
Your PeiDocker GUI handles complex Docker container configuration with multiple interdependent settings. You need robust file system operations (project directories, SSH keys, scripts), sophisticated validation (port conflicts, Docker image formats, SSH configurations), and multi-mode interfaces (Simple wizard vs Advanced tabbed). These tools provide exactly what you need.

1. **Core Foundation**:
   - `textual` - Main framework with reactive state management for configuration changes
   - `textual-dev` - Essential for debugging complex wizard flows and Docker integration
   - `textual-fspicker` - Critical for project directory selection, SSH key browsing, script file selection

2. **Configuration & Validation**:
   - `pydantic` - Type-safe models matching your user_config.yml structure with Docker-specific validation
   - `pydantic-settings` - Environment variable handling for Docker daemon settings
   - `PyYAML` - Direct integration with PeiDocker's configuration file format

3. **Enhanced Widgets** (Highly Recommended):
   - `textual-inputs` - NumberInput for ports (1-65535), specialized validation for Docker formats
   - `typing-extensions` - Enhanced type hints for complex configuration structures

4. **Development & Testing**:
   - `pytest` - Testing framework for GUI interactions and Docker integration
   - Standard Textual testing tools for wizard navigation and validation

**Real-World PeiDocker Benefits**:
- **Eliminate Configuration Errors**: Pydantic prevents invalid Docker configs, port conflicts, malformed SSH settings
- **Streamline File Operations**: textual-fspicker eliminates manual path typing for directories and key files  
- **Accelerate Development**: textual-dev enables real-time debugging of wizard state and Docker API calls
- **Professional User Experience**: Specialized inputs and validation provide polished, error-free configuration flow

### Installation Command:
```bash
# Using pixi (already added to your project):
pixi add --pypi textual textual-dev textual-fspicker pydantic pydantic-settings PyYAML pytest textual-inputs typing-extensions

# Or using pip:
pip install textual[dev] textual-fspicker pydantic pydantic-settings PyYAML pytest textual-inputs typing-extensions
```

## Summary

The Textual ecosystem provides exactly the tools needed to build PeiDocker's sophisticated Docker configuration GUI:

- **textual-fspicker** - Essential for project directory selection, SSH key browsing, and script file management
- **Pydantic** - Critical for type-safe Docker configuration validation matching user_config.yml structure  
- **textual-dev** - Invaluable for debugging complex wizard flows and Docker API integration
- **Built-in validation** framework - Perfect for real-time Docker image name and port validation
- **Modal screens** - Ideal for file selection dialogs and error handling
- **Reactive variables** - Essential for managing interdependent configuration state across wizard steps
- **Message system** - Enables clean communication between wizard steps and configuration screens

**PeiDocker-Specific Advantages**:
- **Prevents Docker Configuration Errors**: Type-safe models catch port conflicts, invalid image names, SSH misconfigurations
- **Streamlines Complex Workflows**: 15-step wizard with validation, navigation, and state persistence
- **Professional File Management**: Visual browsing for project directories, SSH keys, custom scripts
- **Real-time Validation**: Immediate feedback on Docker image availability, port conflicts, configuration compatibility
- **Maintainable Architecture**: Clean separation between GUI logic and Docker configuration models

These tools transform what could be a fragile, error-prone configuration interface into a robust, user-friendly GUI that guides users through creating valid PeiDocker projects while preventing common Docker configuration mistakes.
