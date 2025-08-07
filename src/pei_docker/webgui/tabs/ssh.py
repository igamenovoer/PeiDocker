"""
SSH tab for PeiDocker Web GUI - Refactored with data binding.

This tab handles SSH server configuration, user management,
and SSH key setup for container access using NiceGUI's data binding.
"""

from typing import TYPE_CHECKING, Optional, Dict, List, Any
from nicegui import ui
from pei_docker.webgui.tabs.base import BaseTab
import re

if TYPE_CHECKING:
    from pei_docker.webgui.app import PeiDockerWebGUI

class SSHTab(BaseTab):
    """SSH configuration tab with data binding."""
    
    def __init__(self, app: 'PeiDockerWebGUI') -> None:
        super().__init__(app)
        self.users_container: Optional[ui.column] = None
        self.user_rows: List[Dict[str, Any]] = []
    
    def render(self) -> ui.element:
        """Render the SSH tab content with data binding."""
        with ui.column().classes('w-full max-w-4xl') as container:
            self.container = container
            
            # Tab header
            self.create_section_header(
                '🔐 SSH Configuration',
                'Configure SSH server access and user authentication'
            )
            
            # Get SSH UI state (only in stage 1)
            ssh_ui = self.app.ui_state.stage_1.ssh
            
            # SSH Service Configuration
            with self.create_card('🔐 SSH Service'):
                # Enable SSH toggle
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.switch('✅ Enable SSH Server').bind_value(ssh_ui, 'enabled') \
                        .props('data-testid="ssh-enabled-switch"')
                
                # Port configuration
                with ui.row().classes('gap-4 mb-4') as port_config:
                    port_config.bind_visibility_from(ssh_ui, 'enabled')
                    
                    with ui.column():
                        ui.label('📦 Container Port').classes('font-medium text-gray-700 mb-1')
                        ui.input(
                            placeholder='22',
                            value='22'
                        ).classes('w-full').bind_value(ssh_ui, 'port') \
                            .props('data-testid="ssh-container-port"')
                    
                    with ui.column():
                        ui.label('Host Port').classes('font-medium text-gray-700 mb-1')
                        ui.input(
                            placeholder='2222',
                            value='2222'
                        ).classes('w-full').bind_value(ssh_ui, 'host_port') \
                            .props('data-testid="ssh-host-port"')
            
            # SSH Users Configuration
            with self.create_card('SSH Users') as users_card:
                users_card.bind_visibility_from(ssh_ui, 'enabled')
                
                ui.label('Configure user accounts for SSH access').classes('text-gray-600 mb-4')
                
                # Users container
                with ui.column().classes('w-full') as users_container:
                    self.users_container = users_container
                    self._render_users()
                
                # Add user button
                ui.button('➕ Add SSH User', on_click=self._add_user) \
                    .classes('bg-blue-600 hover:bg-blue-700 text-white') \
                    .props('data-testid="add-ssh-user-btn"')
            
            # SSH disabled warning
            with ui.card().classes('w-full p-4 mb-4 bg-yellow-50 border-yellow-200') as warning:
                warning.bind_visibility_from(ssh_ui, 'enabled', lambda enabled: not enabled)
                
                with ui.row().classes('items-center gap-2'):
                    ui.icon('warning', color='orange')
                    ui.label('SSH server is disabled. Enable SSH to configure user access.') \
                        .classes('text-yellow-800')
        
        return container
    
    def _render_users(self) -> None:
        """Render SSH users from the UI state."""
        if not self.users_container:
            return
        
        # Clear existing UI elements
        self.users_container.clear()
        self.user_rows.clear()
        
        # Get SSH users from UI state
        ssh_ui = self.app.ui_state.stage_1.ssh
        
        # Render each user
        for i, user in enumerate(ssh_ui.users):
            self._create_user_row(i, user)
        
        # Add default user if no users exist
        if not ssh_ui.users:
            ssh_ui.users.append({
                'name': 'me',
                'password': '',
                'uid': None,
                'ssh_keys': []
            })
            self._create_user_row(0, ssh_ui.users[0])
    
    def _create_user_row(self, index: int, user_data: Dict[str, Any]) -> None:
        """Create a single user row with data binding."""
        if not self.users_container:
            return
        
        with self.users_container:
            with ui.card().classes('w-full p-4 mb-4') as user_card:
                # User header
                with ui.row().classes('items-center justify-between mb-4'):
                    ui.label(f'👤 SSH User: {user_data.get("name", f"user{index + 1}")}').classes('text-lg font-semibold')
                    ui.button('🗑️ Remove', on_click=lambda idx=index: self._remove_user(idx)) \
                        .classes('bg-red-600 hover:bg-red-700 text-white text-sm px-3 py-1')
                
                # User configuration
                with ui.row().classes('gap-4 mb-4'):
                    # Username
                    username_input = ui.input(
                        'Username',
                        placeholder='username'
                    ).classes('flex-1').props(f'data-testid="ssh-username-{index}"')
                    username_input.set_value(user_data.get('name', ''))
                    
                    # Password
                    password_input = ui.input(
                        'Password',
                        placeholder='Enter password (letters, numbers, -, _)'
                    ).classes('flex-1').props(f'data-testid="ssh-password-{index}"')
                    password_input.set_value(user_data.get('password', ''))
                
                # Optional UID Configuration
                with ui.column().classes('mb-4'):
                    # Check if UID is set
                    has_uid = user_data.get('uid') is not None
                    uid_enabled = ui.checkbox('Set custom User ID (UID)', value=has_uid)
                    
                    uid_container = ui.column().classes('ml-6')
                    uid_container.bind_visibility_from(uid_enabled, 'value')
                    
                    with uid_container:
                        ui.label('Advanced: Leave unchecked to use automatic UID assignment').classes('text-sm text-gray-600 mb-2')
                        uid_input = ui.input(
                            'UID',
                            placeholder='2000'
                        ).props('type=number min=0').classes('w-full')
                        uid_input.set_value(str(user_data.get('uid', '')) if user_data.get('uid') else '')
                        ui.label('Custom UID for file permissions mapping').classes('text-sm text-gray-600')
                
                # SSH Key configuration
                with ui.column().classes('mb-4 w-full'):
                    ui.label('SSH Keys').classes('font-medium text-gray-700 mb-2')
                    
                    # Check if user has SSH keys
                    ssh_keys = user_data.get('ssh_keys', [])
                    has_keys = len(ssh_keys) > 0
                    
                    # Public key
                    pubkey_data = next((k for k in ssh_keys if k.get('type') == 'public'), None)
                    pubkey_source_value = 'None'
                    pubkey_file_value = ''
                    pubkey_text_value = ''
                    
                    if pubkey_data:
                        if pubkey_data.get('file'):
                            pubkey_source_value = 'File path'
                            pubkey_file_value = pubkey_data['file']
                        elif pubkey_data.get('content'):
                            pubkey_source_value = 'Direct text'
                            pubkey_text_value = pubkey_data['content']
                    
                    # Public key configuration
                    with ui.column().classes('mb-4 w-full'):
                        ui.label('Public Key (copy into container)').classes('font-medium text-gray-700 mb-2')
                        
                        pubkey_source = ui.radio(['None', 'File path', 'Direct text'], value=pubkey_source_value).props('inline')
                        
                        # File path input
                        pubkey_file_container = ui.column().classes('mt-2')
                        pubkey_file_container.bind_visibility_from(pubkey_source, 'value', lambda v: v == 'File path')
                        with pubkey_file_container:
                            with ui.row().classes('gap-2'):
                                pubkey_file_input = ui.input(
                                    placeholder='~  or  /path/to/public.key',
                                    value=pubkey_file_value
                                ).classes('flex-1')
                                ui.button('📁', on_click=lambda: ui.notify('File browser not implemented')).classes('bg-gray-500 hover:bg-gray-600 text-white')
                            ui.label('Use ~ for auto-discovery or specify file path').classes('text-sm text-gray-600')
                        
                        # Text input
                        pubkey_text_container = ui.column().classes('mt-2')
                        pubkey_text_container.bind_visibility_from(pubkey_source, 'value', lambda v: v == 'Direct text')
                        with pubkey_text_container:
                            pubkey_text_input = ui.textarea(
                                placeholder='ssh-ed25519 AAAAC3... user@host',
                                value=pubkey_text_value
                            ).props('rows=3').classes('w-full')
                            ui.label('Paste your public key content directly').classes('text-sm text-gray-600')
                    
                    # Private key
                    privkey_data = next((k for k in ssh_keys if k.get('type') == 'private'), None)
                    privkey_source_value = 'None'
                    privkey_file_value = ''
                    privkey_text_value = ''
                    
                    if privkey_data:
                        if privkey_data.get('file'):
                            privkey_source_value = 'File path'
                            privkey_file_value = privkey_data['file']
                        elif privkey_data.get('content'):
                            privkey_source_value = 'Direct text'
                            privkey_text_value = privkey_data['content']
                    
                    # Private key configuration
                    with ui.column().classes('w-full'):
                        ui.label('Private Key (copy into container)').classes('font-medium text-gray-700 mb-2')
                        
                        privkey_source = ui.radio(['None', 'File path', 'Direct text'], value=privkey_source_value).props('inline')
                        
                        # File path input
                        privkey_file_container = ui.column().classes('mt-2')
                        privkey_file_container.bind_visibility_from(privkey_source, 'value', lambda v: v == 'File path')
                        with privkey_file_container:
                            with ui.row().classes('gap-2'):
                                privkey_file_input = ui.input(
                                    placeholder='~  or  /path/to/private.key',
                                    value=privkey_file_value
                                ).classes('flex-1')
                                ui.button('📁', on_click=lambda: ui.notify('File browser not implemented')).classes('bg-gray-500 hover:bg-gray-600 text-white')
                            ui.label('Use ~ for auto-discovery or specify file path').classes('text-sm text-gray-600')
                        
                        # Text input
                        privkey_text_container = ui.column().classes('mt-2')
                        privkey_text_container.bind_visibility_from(privkey_source, 'value', lambda v: v == 'Direct text')
                        with privkey_text_container:
                            privkey_text_input = ui.textarea(
                                placeholder='-----BEGIN OPENSSH PRIVATE KEY-----\n...',
                                value=privkey_text_value
                            ).props('rows=8').classes('w-full')
                            ui.label('Paste your private key content directly').classes('text-sm text-gray-600')
                
                # Store row data
                row_data = {
                    'index': index,
                    'card': user_card,
                    'user_data': user_data,
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
                self.user_rows.append(row_data)
                
                # Update user data on changes
                def update_user_field(field: str, value: Any, data: Dict[str, Any] = row_data) -> None:
                    data['user_data'][field] = value
                    self.app.ui_state.mark_modified()
                
                # Bind change handlers for inputs using proper on_value_change
                username_input.on_value_change(lambda e: update_user_field('name', e.value))
                password_input.on_value_change(lambda e: self._validate_and_update_password(e.value, password_input, row_data))
                
                # UID change handler
                def update_uid(data: Dict[str, Any] = row_data) -> None:
                    if data['uid_enabled'].value:
                        uid_val = data['uid'].value
                        data['user_data']['uid'] = int(uid_val) if uid_val else None
                    else:
                        data['user_data']['uid'] = None
                    self.app.ui_state.mark_modified()
                
                uid_enabled.on_value_change(lambda e: update_uid())
                uid_input.on_value_change(lambda e: update_uid())
                
                # SSH key change handlers
                def update_ssh_keys(data: Dict[str, Any] = row_data) -> None:
                    ssh_keys = []
                    
                    # Public key
                    if data['pubkey_source'].value == 'File path' and data['pubkey_file'].value:
                        ssh_keys.append({'type': 'public', 'file': data['pubkey_file'].value})
                    elif data['pubkey_source'].value == 'Direct text' and data['pubkey_text'].value:
                        ssh_keys.append({'type': 'public', 'content': data['pubkey_text'].value})
                    
                    # Private key
                    if data['privkey_source'].value == 'File path' and data['privkey_file'].value:
                        ssh_keys.append({'type': 'private', 'file': data['privkey_file'].value})
                    elif data['privkey_source'].value == 'Direct text' and data['privkey_text'].value:
                        ssh_keys.append({'type': 'private', 'content': data['privkey_text'].value})
                    
                    data['user_data']['ssh_keys'] = ssh_keys
                    self.app.ui_state.mark_modified()
                
                for component in [pubkey_source, pubkey_file_input, pubkey_text_input,
                                privkey_source, privkey_file_input, privkey_text_input]:
                    component.on_value_change(lambda e: update_ssh_keys())
    
    def _validate_and_update_password(self, password: str, password_input: ui.input, row_data: Dict[str, Any]) -> None:
        """Validate password and update user data."""
        # Check if password contains only allowed characters
        if password and not re.match(r'^[a-zA-Z0-9_-]*$', password):
            # Remove invalid characters
            valid_password = re.sub(r'[^a-zA-Z0-9_-]', '', password)
            password_input.set_value(valid_password)
            
            # Show error notification
            ui.notify('Password can only contain letters, numbers, dashes (-), and underscores (_)', 
                     type='negative', position='top', timeout=3000)
        else:
            # Update user data
            row_data['user_data']['password'] = password
            self.app.ui_state.mark_modified()
    
    def _add_user(self) -> None:
        """Add a new SSH user."""
        ssh_ui = self.app.ui_state.stage_1.ssh
        
        # Generate unique username
        user_count = len(ssh_ui.users) + 1
        username = f'user{user_count}'
        
        # Add new user to model
        new_user: Dict[str, Any] = {
            'name': username,
            'password': '',
            'uid': None,
            'ssh_keys': []
        }
        ssh_ui.users.append(new_user)
        
        # Create UI row
        self._create_user_row(len(ssh_ui.users) - 1, new_user)
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def _remove_user(self, index: int) -> None:
        """Remove a user."""
        ssh_ui = self.app.ui_state.stage_1.ssh
        
        # Remove from model
        if index < len(ssh_ui.users):
            ssh_ui.users.pop(index)
        
        # Re-render all users to update indices
        self._render_users()
        
        # Mark as modified
        self.app.ui_state.mark_modified()
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate SSH configuration."""
        errors = []
        ssh_ui = self.app.ui_state.stage_1.ssh
        
        if ssh_ui.enabled:
            # Validate port numbers
            try:
                port = int(ssh_ui.port)
                if not (1 <= port <= 65535):
                    errors.append("SSH container port must be between 1 and 65535")
            except ValueError:
                errors.append("SSH container port must be a valid number")
            
            try:
                host_port = int(ssh_ui.host_port)
                if not (1 <= host_port <= 65535):
                    errors.append("SSH host port must be between 1 and 65535")
            except ValueError:
                errors.append("SSH host port must be a valid number")
            
            # Validate users
            if not ssh_ui.users:
                errors.append("At least one SSH user must be configured when SSH is enabled")
            else:
                usernames = set()
                for i, user in enumerate(ssh_ui.users):
                    name = user.get('name', '').strip()
                    if not name:
                        errors.append(f"SSH user {i+1}: Username is required")
                    elif not re.match(r'^[a-z_][a-z0-9_-]{0,31}$', name):
                        errors.append(f"SSH user {i+1}: Invalid username format")
                    elif name in usernames:
                        errors.append(f"SSH user {i+1}: Duplicate username '{name}'")
                    else:
                        usernames.add(name)
                    
                    # Validate authentication
                    password = user.get('password', '')
                    ssh_keys = user.get('ssh_keys', [])
                    has_auth = password or any(k for k in ssh_keys if k.get('file') or k.get('content'))
                    
                    if not has_auth:
                        errors.append(f"SSH user '{name}': Must have either password or SSH keys")
        
        return len(errors) == 0, errors
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get SSH configuration data from UI state."""
        # This is now handled by the UIStateBridge
        # Keeping method for compatibility
        return {}
    
    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set SSH configuration data."""
        # This is now handled by the UIStateBridge during load
        # UI state is automatically bound, so we just need to refresh the view
        if self.users_container:
            self._render_users()