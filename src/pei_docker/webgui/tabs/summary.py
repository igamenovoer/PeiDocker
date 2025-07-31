"""
Summary tab for PeiDocker Web GUI.

This tab provides a complete configuration review, validation status,
and actions for saving and exporting the project.
"""

from typing import TYPE_CHECKING, List, Tuple, Dict
from nicegui import ui
from .base import BaseTab
import yaml

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class SummaryTab(BaseTab):
    """Summary and validation tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.validation_status_container = None
        self.errors_container = None
        self.save_button = None
        self.configure_button = None
        self.download_button = None
        self.config_preview_container = None
    
    def render(self) -> ui.element:
        """Render the summary tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            self.create_section_header(
                '📋 Configuration Summary',
                'Review your complete PeiDocker configuration, validate all settings, and save your user_config.yml file'
            )
            
            # Validation Status
            with self.create_card('🔍 Validation Status'):
                # Status indicators grid
                with ui.row().classes('grid grid-cols-3 gap-4 w-full') as status_grid:
                    self.validation_status_container = status_grid
                
                # Errors container (initially hidden)
                with ui.column().classes('w-full mt-4') as errors_container:
                    self.errors_container = errors_container
            
            # Two-column layout for overview and actions
            with ui.row().classes('w-full gap-6'):
                # Left column - Configuration Overview
                with ui.column().classes('flex-1'):
                    self._create_project_overview()
                    self._create_ssh_overview()
                    self._create_network_overview()
                    self._create_environment_overview()
                    self._create_storage_overview()
                    self._create_scripts_overview()
                
                # Right column - Actions and Export
                with ui.column().classes('flex-1'):
                    self._create_actions_section()
                    self._create_config_preview()
            
            # Refresh the summary initially
            self.refresh_summary()
        
        return container
    
    def _create_project_overview(self):
        """Create project settings overview."""
        with self.create_card('🏗️ Project Settings'):
            with ui.row().classes('w-full text-sm'):
                # Labels column
                with ui.column().classes('font-semibold'):
                    ui.label('Name:')
                    ui.label('Base Image:')
                    ui.label('Directory:')
                
                # Values column
                with ui.column().classes('flex-1'):
                    ui.label(self.app.data.project.name or 'Not set').bind_text_from(
                        self.app.data.project, 'name', lambda x: x or 'Not set'
                    )
                    base_image = self.app.data.config.stage_1.get('image', {}).get('base', 'ubuntu:22.04')
                    ui.label(base_image)
                    ui.label(str(self.app.data.project.directory) if self.app.data.project.directory else 'Not set')
    
    def _create_ssh_overview(self):
        """Create SSH configuration overview."""
        with self.create_card('🔐 SSH Configuration'):
            with ui.column().classes('text-sm'):
                ssh_config = self.app.data.config.stage_1.get('ssh', {})
                enabled = ssh_config.get('enabled', False)
                
                if enabled:
                    port = ssh_config.get('port', 22)
                    host_port = ssh_config.get('host_port', 2222)
                    ui.label(f'✅ Enabled (port {host_port}:{port})').classes('mb-2')
                    
                    # Users info (simplified)
                    users = ssh_config.get('users', [])
                    if users:
                        for user in users[:2]:  # Show first 2 users
                            username = user.get('username', 'unknown')
                            uid = user.get('uid', 'auto')
                            ui.label(f'👤 User: {username} (UID: {uid})').classes('mb-1')
                        if len(users) > 2:
                            ui.label(f'... and {len(users) - 2} more users').classes('mb-1')
                    else:
                        ui.label('👤 No users configured').classes('mb-2')
                else:
                    ui.label('❌ Disabled').classes('mb-2')
    
    def _create_network_overview(self):
        """Create network configuration overview."""
        with self.create_card('🌐 Network Configuration'):
            with ui.column().classes('text-sm'):
                # Proxy
                proxy_config = self.app.data.config.stage_1.get('proxy', {})
                if proxy_config.get('enabled', False):
                    proxy_url = proxy_config.get('url', '')
                    ui.label(f'🌐 Proxy: {proxy_url}').classes('mb-2')
                else:
                    ui.label('🌐 Proxy: Not configured').classes('mb-2')
                
                # APT Mirror
                apt_config = self.app.data.config.stage_1.get('apt', {})
                mirror = apt_config.get('mirror', 'default')
                ui.label(f'📦 APT Mirror: {mirror.title()}').classes('mb-2')
                
                # Port mappings
                ports = self.app.data.config.stage_1.get('ports', [])
                if ports:
                    ui.label(f'🔌 Additional ports: {", ".join(ports[:3])}').classes('mb-2')
                    if len(ports) > 3:
                        ui.label(f'... and {len(ports) - 3} more').classes('text-xs text-gray-500')
                else:
                    ui.label('🔌 Additional ports: None')
    
    def _create_environment_overview(self):
        """Create environment configuration overview."""
        with self.create_card('⚙️ Environment Configuration'):
            with ui.column().classes('text-sm'):
                # Environment variables
                env_config = self.app.data.config.stage_1.get('environment', {})
                variables = env_config.get('variables', {})
                if variables:
                    var_count = len(variables)
                    ui.label(f'🌍 Environment variables: {var_count}').classes('mb-2')
                    # Show first few variables
                    for i, (name, value) in enumerate(list(variables.items())[:2]):
                        ui.label(f'  • {name}={value}').classes('text-xs mb-1')
                    if var_count > 2:
                        ui.label(f'  ... and {var_count - 2} more').classes('text-xs text-gray-500 mb-2')
                else:
                    ui.label('🌍 Environment variables: None').classes('mb-2')
                
                # Device configuration
                device_config = self.app.data.config.stage_1.get('device', {})
                device_type = device_config.get('type', 'cpu')
                if device_type == 'gpu':
                    gpu_config = device_config.get('gpu', {})
                    ui.label('🖥️ Device: GPU support enabled')
                    if gpu_config.get('memory'):
                        ui.label(f'  Memory limit: {gpu_config["memory"]}').classes('text-xs')
                else:
                    ui.label('🖥️ Device: CPU only')
    
    def _create_storage_overview(self):
        """Create storage configuration overview."""
        with self.create_card('💾 Storage Configuration'):
            with ui.column().classes('text-sm'):
                # Stage-2 dynamic storage
                storage_config = self.app.data.config.stage_2.get('storage', {})
                ui.label('🚀 Stage-2 Dynamic Storage:').classes('font-semibold mb-1')
                
                for storage_type in ['app', 'data', 'workspace']:
                    config = storage_config.get(storage_type, {})
                    storage_mode = config.get('type', 'image')
                    ui.label(f'  • {storage_type}: {storage_mode}').classes('text-xs mb-1')
                
                # Mounts
                stage1_mounts = self.app.data.config.stage_1.get('mounts', [])
                stage2_mounts = self.app.data.config.stage_2.get('mounts', [])
                
                if stage1_mounts or stage2_mounts:
                    ui.label('🔗 Volume Mounts:').classes('font-semibold mt-2 mb-1')
                    if stage1_mounts:
                        ui.label(f'  • Stage-1: {len(stage1_mounts)} mounts').classes('text-xs mb-1')
                    if stage2_mounts:
                        ui.label(f'  • Stage-2: {len(stage2_mounts)} mounts').classes('text-xs mb-1')
                else:
                    ui.label('🔗 Volume Mounts: None').classes('mt-2')
    
    def _create_scripts_overview(self):
        """Create scripts configuration overview."""
        with self.create_card('📜 Scripts Configuration'):
            with ui.column().classes('text-sm'):
                # Stage-1 scripts
                stage1_scripts = self.app.data.config.stage_1.get('scripts', {})
                stage2_scripts = self.app.data.config.stage_2.get('scripts', {})
                
                if stage1_scripts or stage2_scripts:
                    if stage1_scripts:
                        ui.label('🏗️ Stage-1 Scripts:').classes('font-semibold mb-1')
                        if 'entry_point' in stage1_scripts:
                            ui.label('  • Custom entry point configured').classes('text-xs mb-1')
                        
                        lifecycle_count = sum(1 for key in stage1_scripts.keys() if key.startswith('on_'))
                        if lifecycle_count > 0:
                            ui.label(f'  • {lifecycle_count} lifecycle scripts').classes('text-xs mb-1')
                    
                    if stage2_scripts:
                        ui.label('🚀 Stage-2 Scripts:').classes('font-semibold mt-2 mb-1')
                        if 'entry_point' in stage2_scripts:
                            ui.label('  • Custom entry point configured').classes('text-xs mb-1')
                        
                        lifecycle_count = sum(1 for key in stage2_scripts.keys() if key.startswith('on_'))
                        if lifecycle_count > 0:
                            ui.label(f'  • {lifecycle_count} lifecycle scripts').classes('text-xs mb-1')
                else:
                    ui.label('📜 No custom scripts configured')
    
    def _create_actions_section(self):
        """Create the actions section."""
        with self.create_card('💾 Save & Export'):
            # Save Configuration
            with ui.column().classes('mb-4'):
                self.save_button = ui.button('💾 Save Configuration', on_click=self._save_configuration) \
                    .classes('w-full bg-green-600 hover:bg-green-700 text-white')
                ui.label('Save user_config.yml to project directory').classes('text-center text-sm text-gray-600 mt-2')
            
            # Configure Project
            with ui.column().classes('mb-4'):
                self.configure_button = ui.button('⚙️ Configure Project', on_click=self._configure_project) \
                    .classes('w-full bg-yellow-600 hover:bg-yellow-700 text-white')
                ui.label('Run pei-docker-cli configure').classes('text-center text-sm text-gray-600 mt-2')
            
            # Download Project
            with ui.column():
                self.download_button = ui.button('📦 Download Project', on_click=self._download_project) \
                    .classes('w-full bg-blue-600 hover:bg-blue-700 text-white')
                ui.label('Export project as ZIP file').classes('text-center text-sm text-gray-600 mt-2')
    
    def _create_config_preview(self):
        """Create the configuration preview section."""
        with self.create_card('📄 Generated user_config.yml Preview'):
            with ui.column().classes('w-full') as preview_container:
                self.config_preview_container = preview_container
    
    def _save_configuration(self):
        """Save the configuration."""
        is_valid, errors = self.validate_all_tabs()
        
        if not is_valid:
            ui.notify('Please fix all validation errors before saving the configuration.', 
                     type='negative', timeout=5000)
            return
        
        try:
            # Generate the configuration
            config_data = self._generate_full_config()
            
            # In a real implementation, this would save to file
            ui.notify('Configuration saved successfully!', type='positive', timeout=3000)
            
        except Exception as e:
            ui.notify(f'Error saving configuration: {str(e)}', type='negative', timeout=5000)
    
    def _configure_project(self):
        """Configure the project using pei-docker-cli."""
        async def confirm_configure():
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                ui.label('Configure Project').classes('text-lg font-semibold mb-3')
                ui.label('Run pei-docker-cli configure to build project structure? This may take a few minutes.').classes('mb-4')
                
                with ui.row().classes('gap-2 justify-end'):
                    ui.button('Cancel', on_click=dialog.close).classes('bg-gray-600 hover:bg-gray-700 text-white')
                    ui.button('Configure', on_click=lambda: (dialog.close(), self._run_configure())).classes('bg-yellow-600 hover:bg-yellow-700 text-white')
            
            dialog.open()
        
        confirm_configure()
    
    def _run_configure(self):
        """Run the actual configure command."""
        ui.notify('Project configuration started. The process is running in the background.', 
                 type='info', timeout=5000)
        
        # In a real implementation, this would run the CLI command
        # subprocess.run(['pei-docker-cli', 'configure', '-p', str(self.app.data.project.directory)])
    
    def _download_project(self):
        """Download the project as ZIP."""
        is_valid, errors = self.validate_all_tabs()
        warnings = []
        
        if not is_valid:
            warnings.append('Configuration has validation errors.')
        
        # Check if project is configured (in real implementation)
        if not self._is_project_configured():
            warnings.append('Project has not been configured yet.')
        
        if warnings:
            async def confirm_download():
                with ui.dialog() as dialog, ui.card().classes('w-96'):
                    ui.label('Download Warning').classes('text-lg font-semibold mb-3')
                    ui.label('Warning:').classes('font-semibold text-yellow-700')
                    for warning in warnings:
                        ui.label(f'• {warning}').classes('text-yellow-700 text-sm mb-1')
                    ui.label('Do you want to continue with the download?').classes('mt-3 mb-4')
                    
                    with ui.row().classes('gap-2 justify-end'):
                        ui.button('Cancel', on_click=dialog.close).classes('bg-gray-600 hover:bg-gray-700 text-white')
                        ui.button('Download', on_click=lambda: (dialog.close(), self._start_download())).classes('bg-blue-600 hover:bg-blue-700 text-white')
                
                dialog.open()
            
            confirm_download()
        else:
            self._start_download()
    
    def _start_download(self):
        """Start the project download."""
        ui.notify('Project ZIP file is being prepared for download...', type='info', timeout=3000)
        
        # In a real implementation, this would create and serve the ZIP file
    
    def _is_project_configured(self) -> bool:
        """Check if the project has been configured."""
        # In a real implementation, this would check for build files
        return False
    
    def validate_all_tabs(self) -> Tuple[bool, List[str]]:
        """Validate all tabs and return overall status."""
        # Use the integrated real-time validator
        validation_errors = self.app.real_time_validator.validate_all_tabs()
        
        all_errors = []
        for tab_name, errors in validation_errors.items():
            # Prefix errors with tab name
            tab_errors = [f"{tab_name.title()}: {error}" for error in errors]
            all_errors.extend(tab_errors)
        
        return len(all_errors) == 0, all_errors
    
    def refresh_summary(self):
        """Refresh the summary display."""
        self._update_validation_status()
        self._update_config_preview()
    
    def _update_validation_status(self):
        """Update the validation status display."""
        if not self.validation_status_container:
            return
        
        self.validation_status_container.clear()
        
        # Get validation status for each tab
        tab_statuses = {}
        all_errors = []
        
        for tab_name, tab in self.app.tabs.items():
            is_valid, errors = tab.validate()
            tab_statuses[tab_name.value] = {
                'valid': is_valid,
                'error_count': len(errors),
                'errors': errors
            }
            if errors:
                # Prefix errors with tab name
                tab_errors = [f"{tab_name.value.title()}: {error}" for error in errors]
                all_errors.extend(tab_errors)
        
        # Create status indicators
        with self.validation_status_container:
            for tab_name, status in tab_statuses.items():
                with ui.row().classes('items-center gap-2'):
                    # Status dot
                    dot_color = 'bg-green-500' if status['valid'] else 'bg-red-500'
                    ui.element('div').classes(f'w-3 h-3 rounded-full {dot_color}')
                    
                    # Status text
                    if status['valid']:
                        ui.label(f'{tab_name.title()}: Valid').classes('text-sm')
                    else:
                        ui.label(f'{tab_name.title()}: {status["error_count"]} error{"s" if status["error_count"] != 1 else ""}').classes('text-sm')
        
        # Update errors container
        self.errors_container.clear()
        
        if all_errors:
            with self.errors_container:
                with ui.card().classes('w-full p-3 bg-red-50 border-red-200'):
                    with ui.row().classes('items-center gap-2 mb-2'):
                        ui.icon('error', color='red')
                        ui.label('Configuration Errors').classes('text-sm font-semibold text-red-700')
                    
                    with ui.column().classes('text-sm text-red-700'):
                        for error in all_errors[:5]:  # Show first 5 errors
                            ui.label(f'• {error}').classes('mb-1')
                        if len(all_errors) > 5:
                            ui.label(f'... and {len(all_errors) - 5} more errors').classes('text-xs')
        
        # Update save button state
        if self.save_button:
            if all_errors:
                self.save_button.props('disabled')
                self.save_button.classes(replace='w-full bg-gray-400 text-white cursor-not-allowed')
            else:
                self.save_button.props(remove='disabled')
                self.save_button.classes(replace='w-full bg-green-600 hover:bg-green-700 text-white')
    
    def _update_config_preview(self):
        """Update the configuration preview."""
        if not self.config_preview_container:
            return
        
        self.config_preview_container.clear()
        
        try:
            config_data = self._generate_full_config()
            config_yaml = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
            
            with self.config_preview_container:
                with ui.card().classes('w-full p-3 bg-gray-50'):
                    ui.code(config_yaml).classes('text-xs font-mono w-full')
        
        except Exception as e:
            with self.config_preview_container:
                ui.label(f'Error generating preview: {str(e)}').classes('text-red-600 text-sm')
    
    def _generate_full_config(self) -> dict:
        """Generate the complete configuration."""
        config = {
            'stage_1': dict(self.app.data.config.stage_1),
            'stage_2': dict(self.app.data.config.stage_2)
        }
        
        # Clean up empty sections
        for stage in ['stage_1', 'stage_2']:
            config[stage] = {k: v for k, v in config[stage].items() if v}
        
        return config
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate summary tab (always valid)."""
        return True, []
    
    def get_config_data(self) -> dict:
        """Get configuration data (returns full config)."""
        return self._generate_full_config()
    
    def set_config_data(self, data: dict):
        """Set configuration data (not applicable for summary)."""
        pass