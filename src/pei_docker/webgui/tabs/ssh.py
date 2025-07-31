"""
SSH tab for PeiDocker Web GUI.

This tab handles SSH server configuration, user management,
and SSH key setup for container access.
"""

from typing import TYPE_CHECKING
from nicegui import ui
from .base import BaseTab

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class SSHTab(BaseTab):
    """SSH configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI'):
        super().__init__(app)
        self.ssh_enabled_switch = None
        self.ssh_port_input = None
        self.host_port_input = None
        self.users_container = None
    
    def render(self) -> ui.element:
        """Render the SSH tab content."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            # Tab header
            self.create_section_header(
                '🔐 SSH Configuration',
                'Configure SSH server access and user authentication'
            )
            
            # SSH Service Configuration
            with self.create_card('🔐 SSH Service'):
                # Enable SSH toggle
                with ui.row().classes('items-center gap-4 mb-4'):
                    self.ssh_enabled_switch = ui.switch('✅ Enable SSH Server', value=False)
                    self.ssh_enabled_switch.on('change', self._on_ssh_toggle)
                
                # Port configuration
                with ui.row().classes('gap-4 mb-4') as port_config:
                    with ui.column():
                        ui.label('📦 Container Port').classes('font-medium text-gray-700 mb-1')
                        self.ssh_port_input = ui.number('SSH Port', value=22, min=1, max=65535) \
                            .classes('w-32')
                    
                    with ui.column():
                        ui.label('Host Port').classes('font-medium text-gray-700 mb-1')
                        self.host_port_input = ui.number('Host Port', value=2222, min=1, max=65535) \
                            .classes('w-32')
                
                port_config.bind_visibility_from(self.ssh_enabled_switch, 'value')
            
            # SSH Users Configuration
            with self.create_card('SSH Users') as users_card:
                ui.label('Configure user accounts for SSH access').classes('text-gray-600 mb-4')
                
                # Users container
                with ui.column().classes('w-full') as users_container:
                    self.users_container = users_container
                
                # Add user button
                ui.button('[Add User] Add User', on_click=self._add_user) \
                    .classes('bg-blue-600 hover:bg-blue-700 text-white')
                
                users_card.bind_visibility_from(self.ssh_enabled_switch, 'value')
            
            # SSH disabled warning
            with ui.card().classes('w-full p-4 mb-4 bg-yellow-50 border-yellow-200') as warning:
                with ui.row().classes('items-center gap-2'):
                    ui.icon('warning', color='orange')
                    ui.label('SSH server is disabled. Enable SSH to configure user access.') \
                        .classes('text-yellow-800')
                
                warning.bind_visibility_from(self.ssh_enabled_switch, 'value', lambda enabled: not enabled)
        
        return container
    
    def _on_ssh_toggle(self, e):
        """Handle SSH enable/disable toggle."""
        enabled = e.value
        
        # Update configuration
        if 'ssh' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['ssh'] = {}
        
        self.app.data.config.stage_1['ssh']['enable'] = enabled
        self.mark_modified()
    
    def _add_user(self):
        """Add a new SSH user configuration."""
        user_count = len(self.users_container.default_slot.children) + 1
        
        with self.users_container:
            with ui.card().classes('w-full p-4 mb-4') as user_card:
                # User header
                with ui.row().classes('items-center justify-between mb-4'):
                    ui.label(f'[Add User] SSH User {user_count}').classes('text-lg font-semibold')
                    ui.button('[Remove] Remove', on_click=lambda: user_card.delete()) \
                        .classes('bg-red-600 hover:bg-red-700 text-white text-sm')
                
                # User configuration
                with ui.row().classes('gap-4 mb-4'):
                    ui.input('Username', placeholder='user1').classes('flex-1')
                    ui.input('Password', placeholder='secure-password', password=True).classes('flex-1')
                
                # SSH Key configuration
                with ui.column().classes('mb-4'):
                    ui.label('SSH Key Configuration').classes('font-medium text-gray-700 mb-2')
                    
                    # Public key
                    with ui.expansion('Public Key (optional)', icon='key').classes('mb-2'):
                        ui.radio(['None', 'File path', 'Inline text'], value='None') \
                            .classes('mb-2').props('inline')
                        ui.input('Key file path or content').classes('w-full')
                    
                    # Private key  
                    with ui.expansion('Private Key (optional)', icon='key'):
                        ui.radio(['None', 'File path', 'Inline text'], value='None') \
                            .classes('mb-2').props('inline')
                        ui.textarea('Key file path or content').classes('w-full')
        
        self.mark_modified()
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate SSH configuration."""
        errors = []
        
        if self.ssh_enabled_switch and self.ssh_enabled_switch.value:
            # Validate port numbers
            if self.ssh_port_input and (self.ssh_port_input.value < 1 or self.ssh_port_input.value > 65535):
                errors.append("SSH container port must be between 1 and 65535")
            
            if self.host_port_input and (self.host_port_input.value < 1 or self.host_port_input.value > 65535):
                errors.append("SSH host port must be between 1 and 65535")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> dict:
        """Get SSH configuration data."""
        return {
            'stage_1': {
                'ssh': self.app.data.config.stage_1.get('ssh', {})
            }
        }
    
    def set_config_data(self, data: dict):
        """Set SSH configuration data."""
        ssh_config = data.get('stage_1', {}).get('ssh', {})
        
        if self.ssh_enabled_switch:
            self.ssh_enabled_switch.set_value(ssh_config.get('enable', False))
        
        if self.ssh_port_input:
            self.ssh_port_input.set_value(ssh_config.get('port', 22))
        
        if self.host_port_input:
            self.host_port_input.set_value(ssh_config.get('host_port', 2222))