"""
SSH tab for PeiDocker Web GUI.

This tab handles SSH server configuration, user management,
and SSH key setup for container access.
"""

from typing import TYPE_CHECKING, Optional, Dict, List, Any
from nicegui import ui
from .base import BaseTab

if TYPE_CHECKING:
    from ..app import PeiDockerWebGUI

class SSHTab(BaseTab):
    """SSH configuration tab."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        super().__init__(app)
        self.ssh_enabled_switch: Optional[ui.switch] = None
        self.ssh_port_input: Optional[ui.number] = None
        self.host_port_input: Optional[ui.number] = None
        self.users_container: Optional[ui.column] = None
        self.users_data: List[Dict[str, Any]] = []  # Track user configurations
    
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
                ui.button('➕ Add SSH User', on_click=self._add_user) \
                    .classes('bg-blue-600 hover:bg-blue-700 text-white')
                
                users_card.bind_visibility_from(self.ssh_enabled_switch, 'value')
            
            # SSH disabled warning
            with ui.card().classes('w-full p-4 mb-4 bg-yellow-50 border-yellow-200') as warning:
                with ui.row().classes('items-center gap-2'):
                    ui.icon('warning', color='orange')
                    ui.label('SSH server is disabled. Enable SSH to configure user access.') \
                        .classes('text-yellow-800')
                
                warning.bind_visibility_from(self.ssh_enabled_switch, 'value', lambda enabled: not enabled)
        
        # Clear existing data since container was cleared
        self.users_data = []
        self.user_count = 0
        
        # Check if we should add default user
        ssh_config = self.app.data.config.stage_1.get('ssh', {})
        if ssh_config.get('enabled', False) and not ssh_config.get('users', []):
            # Only add default user if SSH is enabled and no users exist
            self._add_default_user()
        
        return container
    
    def _add_default_user(self) -> None:
        """Add the default 'me' user like in the demo."""
        with self.users_container:
            with ui.card().classes('w-full p-4 mb-4') as user_card:
                user_id = 'default-user-me'
                
                # User header
                with ui.row().classes('items-center justify-between mb-4'):
                    ui.label('👤 SSH User: me').classes('text-lg font-semibold')
                    ui.button('🗑️ Remove', on_click=lambda: self._remove_user(user_card, user_id)) \
                        .classes('bg-red-600 hover:bg-red-700 text-white text-sm px-3 py-1')
                
                # User configuration
                with ui.row().classes('gap-4 mb-4'):
                    username_input = ui.input('Username', placeholder='username', value='me').classes('flex-1')
                    password_input = ui.input('Password', placeholder='Enter secure password', password=True, value='').classes('flex-1')
                
                # Optional UID Configuration
                with ui.column().classes('mb-4'):
                    uid_enabled = ui.checkbox('Set custom User ID (UID)', value=False)
                    uid_container = ui.column().classes('ml-6')
                    with uid_container:
                        ui.label('Advanced: Leave unchecked to use automatic UID assignment').classes('text-sm text-gray-600 mb-2')
                        uid_input = ui.input('UID', placeholder='1000', value='1000').props('type=number min=0').classes('max-w-xs')
                        ui.label('Custom UID for file permissions mapping').classes('text-sm text-gray-600')
                    
                    # Bind UID input visibility to checkbox
                    uid_input.bind_visibility_from(uid_enabled, 'value')
                
                # SSH Key configuration (simplified for default user)
                with ui.column().classes('mb-4'):
                    # Public key configuration
                    with ui.column().classes('mb-4'):
                        ui.label('Public Key (copy into container)').classes('font-medium text-gray-700 mb-2')
                        
                        pubkey_source = ui.radio(['None', 'File path', 'Direct text'], value='None').props('inline')
                        
                        # File path input
                        pubkey_file_container = ui.column().classes('mt-2')
                        with pubkey_file_container:
                            with ui.row().classes('gap-2'):
                                pubkey_file_input = ui.input(placeholder='~  or  /path/to/public.key  or  stage-1/keys/id_rsa.pub').classes('flex-1')
                                ui.button('📁', on_click=lambda: ui.notify('File browser not implemented')).classes('bg-gray-500 hover:bg-gray-600 text-white')
                            ui.label('Use ~ for auto-discovery or specify file path relative to project directory').classes('text-sm text-gray-600')
                        
                        # Text input
                        pubkey_text_container = ui.column().classes('mt-2')
                        with pubkey_text_container:
                            pubkey_text_input = ui.textarea(placeholder='ssh-ed25519 AAAAC3... user@host').props('rows=3').classes('w-full')
                            ui.label('Paste your public key content directly').classes('text-sm text-gray-600')
                        
                        # Bind visibility based on selection
                        pubkey_file_container.bind_visibility_from(pubkey_source, 'value', lambda v: v == 'File path')
                        pubkey_text_container.bind_visibility_from(pubkey_source, 'value', lambda v: v == 'Direct text')
                    
                    # Private key configuration
                    with ui.column():
                        ui.label('Private Key (copy into container)').classes('font-medium text-gray-700 mb-2')
                        
                        privkey_source = ui.radio(['None', 'File path', 'Direct text'], value='None').props('inline')
                        
                        # File path input
                        privkey_file_container = ui.column().classes('mt-2')
                        with privkey_file_container:
                            with ui.row().classes('gap-2'):
                                privkey_file_input = ui.input(placeholder='~  or  /path/to/private.key  or  stage-1/keys/id_rsa').classes('flex-1')
                                ui.button('📁', on_click=lambda: ui.notify('File browser not implemented')).classes('bg-gray-500 hover:bg-gray-600 text-white')
                            ui.label('Use ~ for auto-discovery or specify file path').classes('text-sm text-gray-600')
                        
                        # Text input
                        privkey_text_container = ui.column().classes('mt-2')
                        with privkey_text_container:
                            privkey_text_input = ui.textarea(placeholder='-----BEGIN OPENSSH PRIVATE KEY-----\n...').props('rows=8').classes('w-full')
                            ui.label('Paste your private key content directly').classes('text-sm text-gray-600')
                        
                        # Bind visibility based on selection
                        privkey_file_container.bind_visibility_from(privkey_source, 'value', lambda v: v == 'File path')
                        privkey_text_container.bind_visibility_from(privkey_source, 'value', lambda v: v == 'Direct text')
                
                # Store user data for later access
                user_data = {
                    'id': user_id,
                    'card': user_card,
                    'username': username_input,
                    'password': password_input,
                    'uid_enabled': uid_enabled,
                    'uid': uid_input,
                    'pubkey_source': pubkey_source,
                    'pubkey_file': pubkey_file_input,
                    'pubkey_text': pubkey_text_input,
                    'privkey_source': privkey_source,
                    'privkey_file': privkey_file_input,
                    'privkey_text': privkey_text_input
                }
                
                # Add change handlers
                for component in [username_input, password_input, uid_enabled, uid_input, 
                                pubkey_source, pubkey_file_input, pubkey_text_input,
                                privkey_source, privkey_file_input, privkey_text_input]:
                    component.on('change', lambda e: self.mark_modified())
                
                # Add to users data list
                self.users_data.append(user_data)
    
    def _on_ssh_toggle(self, e: Any) -> None:
        """Handle SSH enable/disable toggle."""
        enabled = e.value
        
        # Update configuration
        if 'ssh' not in self.app.data.config.stage_1:
            self.app.data.config.stage_1['ssh'] = {}
        
        self.app.data.config.stage_1['ssh']['enable'] = enabled
        self.mark_modified()
    
    def _add_user(self) -> None:
        """Add a new SSH user configuration."""
        user_count = len(self.users_container.default_slot.children) + 1
        user_id = f'user-{user_count}'
        
        with self.users_container:
            with ui.card().classes('w-full p-4 mb-4') as user_card:
                # User header
                with ui.row().classes('items-center justify-between mb-4'):
                    ui.label(f'👤 SSH User: user{user_count}').classes('text-lg font-semibold')
                    ui.button('🗑️ Remove', on_click=lambda: self._remove_user(user_card, user_id)) \
                        .classes('bg-red-600 hover:bg-red-700 text-white text-sm px-3 py-1')
                
                # User configuration
                with ui.row().classes('gap-4 mb-4'):
                    username_input = ui.input('Username', placeholder='username', value=f'user{user_count}').classes('flex-1')
                    password_input = ui.input('Password', placeholder='Enter secure password', password=True).classes('flex-1')
                
                # Optional UID Configuration
                with ui.column().classes('mb-4'):
                    uid_enabled = ui.checkbox(f'Set custom User ID (UID)', value=False)
                    uid_container = ui.column().classes('ml-6')
                    with uid_container:
                        ui.label('Advanced: Leave unchecked to use automatic UID assignment').classes('text-sm text-gray-600 mb-2')
                        uid_input = ui.input('UID', placeholder='1000', value='').props('type=number min=0').classes('max-w-xs')
                        ui.label('Custom UID for file permissions mapping').classes('text-sm text-gray-600')
                    
                    # Bind UID input visibility to checkbox
                    uid_input.bind_visibility_from(uid_enabled, 'value')
                
                # SSH Key configuration
                with ui.column().classes('mb-4'):
                    # Public key configuration
                    with ui.column().classes('mb-4'):
                        ui.label('Public Key (copy into container)').classes('font-medium text-gray-700 mb-2')
                        
                        pubkey_source = ui.radio(['None', 'File path', 'Direct text'], value='None').props('inline')
                        
                        # File path input
                        pubkey_file_container = ui.column().classes('mt-2')
                        with pubkey_file_container:
                            with ui.row().classes('gap-2'):
                                pubkey_file_input = ui.input(placeholder='~  or  /path/to/public.key  or  stage-1/keys/id_rsa.pub').classes('flex-1')
                                ui.button('📁', on_click=lambda: ui.notify('File browser not implemented')).classes('bg-gray-500 hover:bg-gray-600 text-white')
                            ui.label('Use ~ for auto-discovery or specify file path relative to project directory').classes('text-sm text-gray-600')
                        
                        # Text input
                        pubkey_text_container = ui.column().classes('mt-2')
                        with pubkey_text_container:
                            pubkey_text_input = ui.textarea(placeholder='ssh-ed25519 AAAAC3... user@host').props('rows=3').classes('w-full')
                            ui.label('Paste your public key content directly').classes('text-sm text-gray-600')
                        
                        # Bind visibility based on selection
                        pubkey_file_container.bind_visibility_from(pubkey_source, 'value', lambda v: v == 'File path')
                        pubkey_text_container.bind_visibility_from(pubkey_source, 'value', lambda v: v == 'Direct text')
                    
                    # Private key configuration
                    with ui.column():
                        ui.label('Private Key (copy into container)').classes('font-medium text-gray-700 mb-2')
                        
                        privkey_source = ui.radio(['None', 'File path', 'Direct text'], value='None').props('inline')
                        
                        # File path input
                        privkey_file_container = ui.column().classes('mt-2')
                        with privkey_file_container:
                            with ui.row().classes('gap-2'):
                                privkey_file_input = ui.input(placeholder='~  or  /path/to/private.key  or  stage-1/keys/id_rsa').classes('flex-1')
                                ui.button('📁', on_click=lambda: ui.notify('File browser not implemented')).classes('bg-gray-500 hover:bg-gray-600 text-white')
                            ui.label('Use ~ for auto-discovery or specify file path').classes('text-sm text-gray-600')
                        
                        # Text input
                        privkey_text_container = ui.column().classes('mt-2')
                        with privkey_text_container:
                            privkey_text_input = ui.textarea(placeholder='-----BEGIN OPENSSH PRIVATE KEY-----\n...').props('rows=8').classes('w-full')
                            ui.label('Paste your private key content directly').classes('text-sm text-gray-600')
                        
                        # Bind visibility based on selection
                        privkey_file_container.bind_visibility_from(privkey_source, 'value', lambda v: v == 'File path')
                        privkey_text_container.bind_visibility_from(privkey_source, 'value', lambda v: v == 'Direct text')
                
                # Store user data for later access
                user_data = {
                    'id': user_id,
                    'card': user_card,
                    'username': username_input,
                    'password': password_input,
                    'uid_enabled': uid_enabled,
                    'uid': uid_input,
                    'pubkey_source': pubkey_source,
                    'pubkey_file': pubkey_file_input,
                    'pubkey_text': pubkey_text_input,
                    'privkey_source': privkey_source,
                    'privkey_file': privkey_file_input,
                    'privkey_text': privkey_text_input
                }
                
                # Add change handlers
                for component in [username_input, password_input, uid_enabled, uid_input, 
                                pubkey_source, pubkey_file_input, pubkey_text_input,
                                privkey_source, privkey_file_input, privkey_text_input]:
                    component.on('change', lambda e: self.mark_modified())
                
                # Add to users data list
                self.users_data.append(user_data)
        
        self.mark_modified()
    
    def _remove_user(self, user_card: ui.card, user_id: str) -> None:
        """Remove a user configuration."""
        user_card.delete()
        # Remove from tracking list
        self.users_data = [u for u in self.users_data if u['id'] != user_id]
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
            self.ssh_enabled_switch.set_value(ssh_config.get('enabled', False))
        
        if self.ssh_port_input:
            self.ssh_port_input.set_value(ssh_config.get('port', 22))
        
        if self.host_port_input:
            self.host_port_input.set_value(ssh_config.get('host_port', 2222))
        
        # Note: User loading from config would need to be implemented
        # For now, users need to be re-entered when switching tabs