# How to Use Storage in NiceGUI

NiceGUI provides multiple storage options for persisting data across sessions, tabs, and users. This guide covers all storage types and best practices.

## Storage Types Overview

### 1. app.storage.user
- **Scope**: Per user/browser session
- **Persistence**: Across page reloads and browser restarts
- **Requirement**: Needs `storage_secret` in `ui.run()`
- **Use Case**: User preferences, session data

### 2. app.storage.tab  
- **Scope**: Per browser tab
- **Persistence**: Until tab is closed
- **Use Case**: Tab-specific state, form data

### 3. app.storage.client
- **Scope**: Per WebSocket connection
- **Persistence**: Until connection closes
- **Use Case**: Temporary UI state

### 4. app.storage.browser
- **Scope**: Browser localStorage
- **Persistence**: Permanent (until cleared)
- **Use Case**: Client-side preferences

### 5. app.storage.general
- **Scope**: Server-wide, all users
- **Persistence**: Server lifetime
- **Use Case**: Shared application state

## Basic Usage

### Setting Up Storage
```python
from nicegui import ui, app

# Required for user storage
ui.run(storage_secret='your-secret-key-here')
```

### User Storage
```python
@ui.page('/')
def main_page():
    # Initialize storage with defaults
    if 'username' not in app.storage.user:
        app.storage.user['username'] = 'Guest'
        app.storage.user['preferences'] = {
            'theme': 'light',
            'language': 'en'
        }
    
    # Read from storage
    username = app.storage.user.get('username', 'Guest')
    ui.label(f'Welcome, {username}!')
    
    # Update storage
    def update_username(e):
        app.storage.user['username'] = e.value
    
    ui.input('Username', value=username, on_change=update_username)
```

### Tab Storage
```python
@ui.page('/form')
def form_page():
    # Store form data per tab
    if 'form_data' not in app.storage.tab:
        app.storage.tab['form_data'] = {
            'name': '',
            'email': '',
            'message': ''
        }
    
    form_data = app.storage.tab['form_data']
    
    # Bind to inputs
    ui.input('Name').bind_value(form_data, 'name')
    ui.input('Email').bind_value(form_data, 'email')
    ui.textarea('Message').bind_value(form_data, 'message')
```

## State Management Patterns

### Configuration State
```python
class ConfigurationManager:
    """Manage configuration state with storage"""
    
    def __init__(self):
        # Initialize from storage or defaults
        self.config = app.storage.user.get('config', self.get_defaults())
    
    def get_defaults(self):
        return {
            'project_name': 'my-project',
            'base_image': 'ubuntu:22.04',
            'ssh_enabled': True,
            'ports': []
        }
    
    def update(self, key, value):
        """Update configuration and persist"""
        self.config[key] = value
        app.storage.user['config'] = self.config
        ui.notify(f'Updated {key}')
    
    def reset(self):
        """Reset to defaults"""
        self.config = self.get_defaults()
        app.storage.user['config'] = self.config
        ui.notify('Configuration reset')

# Usage
config_manager = ConfigurationManager()
```

### Reactive Storage Pattern
```python
from nicegui import ui, app

def create_reactive_storage(key, default_value):
    """Create reactive storage that auto-persists"""
    
    # Initialize storage
    if key not in app.storage.user:
        app.storage.user[key] = default_value
    
    # Create reactive state
    state = ui.state(app.storage.user[key])
    
    # Auto-persist on change
    def persist():
        app.storage.user[key] = state.value
    
    # Watch for changes
    state.on_change = persist
    
    return state

# Usage
counter = create_reactive_storage('counter', 0)
ui.label().bind_text_from(counter, 'value')
ui.button('+', on_click=lambda: counter.set(counter.value + 1))
```

## Complex Data Structures

### Storing Lists and Dicts
```python
@ui.page('/projects')
def projects_page():
    # Initialize project list
    if 'projects' not in app.storage.user:
        app.storage.user['projects'] = []
    
    projects = app.storage.user['projects']
    
    # Add project
    def add_project(name):
        project = {
            'id': len(projects),
            'name': name,
            'created': datetime.now().isoformat(),
            'status': 'active'
        }
        projects.append(project)
        app.storage.user['projects'] = projects  # Trigger update
        refresh_project_list()
    
    # Display projects
    @ui.refreshable
    def project_list():
        for project in projects:
            with ui.card():
                ui.label(project['name'])
                ui.label(f"Created: {project['created']}")
    
    project_list()
```

### Nested Storage Updates
```python
# Correct way to update nested structures
config = app.storage.user.get('config', {})
config['stage_1'] = config.get('stage_1', {})
config['stage_1']['ssh'] = {
    'enabled': True,
    'port': 22
}
# Must reassign to trigger update
app.storage.user['config'] = config

# Alternative using update()
app.storage.user.update({
    'config': {
        **app.storage.user.get('config', {}),
        'stage_1': {
            **app.storage.user.get('config', {}).get('stage_1', {}),
            'ssh': {'enabled': True, 'port': 22}
        }
    }
})
```

## Session Management

### Login/Logout Pattern
```python
@ui.page('/login')
def login_page():
    def do_login(username, password):
        # Validate credentials
        if validate_user(username, password):
            app.storage.user.update({
                'authenticated': True,
                'username': username,
                'login_time': datetime.now().isoformat()
            })
            ui.navigate.to('/')
        else:
            ui.notify('Invalid credentials', type='negative')
    
    username = ui.input('Username')
    password = ui.input('Password', password=True)
    ui.button('Login', on_click=lambda: do_login(username.value, password.value))

@ui.page('/')
def main_page():
    # Check authentication
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
        return
    
    # Logout function
    def logout():
        app.storage.user.clear()
        ui.navigate.to('/login')
    
    ui.button('Logout', on_click=logout)
```

### Multi-Tab Synchronization
```python
# Share data between tabs using general storage
@ui.page('/editor')
def editor_page():
    # Unique ID for this tab
    tab_id = str(uuid.uuid4())
    
    # Register tab
    active_tabs = app.storage.general.get('active_tabs', {})
    active_tabs[tab_id] = {
        'opened': datetime.now().isoformat(),
        'last_active': datetime.now().isoformat()
    }
    app.storage.general['active_tabs'] = active_tabs
    
    # Clean up on disconnect
    async def cleanup():
        active_tabs = app.storage.general.get('active_tabs', {})
        active_tabs.pop(tab_id, None)
        app.storage.general['active_tabs'] = active_tabs
    
    app.on_disconnect(cleanup)
```

## Performance Considerations

### Lazy Loading
```python
class LazyStorageLoader:
    """Load storage data only when needed"""
    
    def __init__(self, storage_key):
        self.storage_key = storage_key
        self._data = None
    
    @property
    def data(self):
        if self._data is None:
            self._data = app.storage.user.get(self.storage_key, {})
        return self._data
    
    def save(self):
        app.storage.user[self.storage_key] = self._data
```

### Batch Updates
```python
def batch_update_storage(updates):
    """Update multiple storage keys efficiently"""
    storage_data = app.storage.user.copy()
    storage_data.update(updates)
    app.storage.user.update(storage_data)
```

## Storage Patterns for PeiDocker

### Project State Management
```python
class ProjectState:
    """Manage PeiDocker project state"""
    
    def __init__(self):
        self.load_or_create()
    
    def load_or_create(self):
        """Load existing project or create new"""
        if 'project' not in app.storage.user:
            app.storage.user['project'] = {
                'directory': None,
                'config': {},
                'last_saved': None,
                'is_dirty': False
            }
    
    @property
    def project(self):
        return app.storage.user['project']
    
    def set_directory(self, directory):
        """Set project directory"""
        self.project['directory'] = str(directory)
        self._save()
    
    def update_config(self, config):
        """Update configuration"""
        self.project['config'] = config
        self.project['is_dirty'] = True
        self._save()
    
    def mark_saved(self):
        """Mark project as saved"""
        self.project['last_saved'] = datetime.now().isoformat()
        self.project['is_dirty'] = False
        self._save()
    
    def _save(self):
        """Persist to storage"""
        app.storage.user['project'] = self.project
```

### Form State Tracking
```python
def track_form_changes(form_id):
    """Track form changes for unsaved changes warning"""
    
    # Initialize form state
    if 'forms' not in app.storage.tab:
        app.storage.tab['forms'] = {}
    
    if form_id not in app.storage.tab['forms']:
        app.storage.tab['forms'][form_id] = {
            'original': {},
            'current': {},
            'is_dirty': False
        }
    
    form_state = app.storage.tab['forms'][form_id]
    
    def set_original(data):
        form_state['original'] = data.copy()
        form_state['current'] = data.copy()
        form_state['is_dirty'] = False
        app.storage.tab['forms'] = app.storage.tab['forms']
    
    def update_field(field, value):
        form_state['current'][field] = value
        form_state['is_dirty'] = form_state['current'] != form_state['original']
        app.storage.tab['forms'] = app.storage.tab['forms']
    
    return form_state, set_original, update_field
```

## Best Practices

1. **Initialize with defaults** - Always check if keys exist before accessing
2. **Use appropriate scope** - Choose the right storage type for your data
3. **Handle storage errors** - Storage might fail or be disabled
4. **Clean up resources** - Remove temporary data when no longer needed
5. **Avoid large objects** - Storage has size limits, use files for large data
6. **Secure sensitive data** - Don't store passwords or secrets in client-visible storage
7. **Version your schema** - Include version info for migration support

## Troubleshooting

### Common Issues
```python
# Issue: Changes not persisting
# Solution: Reassign the entire object
data = app.storage.user.get('data', {})
data['key'] = 'value'
app.storage.user['data'] = data  # Must reassign!

# Issue: Storage not available
# Solution: Check if running with storage_secret
if hasattr(app.storage, 'user'):
    # User storage available
    pass
else:
    # Fallback to client storage
    pass
```

## Resources

- NiceGUI Storage Documentation: https://nicegui.io/documentation/storage
- Browser Storage API: https://developer.mozilla.org/en-US/docs/Web/API/Storage