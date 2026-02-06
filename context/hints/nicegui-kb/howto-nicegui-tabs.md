# How to Implement Tabs in NiceGUI

This guide shows how to create and manage tabbed interfaces in NiceGUI, including basic tabs, dynamic content, and tab state management.

## Basic Tab Implementation

### Simple Tabs
```python
from nicegui import ui

# Create tabs and panels
with ui.tabs() as tabs:
    tab1 = ui.tab('Project')
    tab2 = ui.tab('SSH')
    tab3 = ui.tab('Network')

with ui.tab_panels(tabs, value=tab1):
    with ui.tab_panel(tab1):
        ui.label('Project configuration')
    with ui.tab_panel(tab2):
        ui.label('SSH settings')
    with ui.tab_panel(tab3):
        ui.label('Network configuration')
```

### Tabs with Icons
```python
with ui.tabs() as tabs:
    project_tab = ui.tab('Project').props('icon=folder')
    ssh_tab = ui.tab('SSH').props('icon=lock')
    network_tab = ui.tab('Network').props('icon=language')
```

## Dynamic Tab Management

### Programmatic Tab Selection
```python
# Store tabs reference
tabs_ref = ui.tabs()
with tabs_ref as tabs:
    tab1 = ui.tab('First')
    tab2 = ui.tab('Second')

# Switch tabs programmatically
ui.button('Go to Second', on_click=lambda: tabs_ref.set_value(tab2))
```

### Tracking Active Tab
```python
# Using reactive state
active_tab = ui.state('project')

def on_tab_change(e):
    active_tab.value = e.value
    ui.notify(f'Switched to {e.value}')

with ui.tabs(on_change=on_tab_change) as tabs:
    ui.tab('project', label='Project')
    ui.tab('ssh', label='SSH')
```

## Advanced Tab Features

### Tab Validation Indicators
```python
# Track validation state
tab_errors = {
    'project': False,
    'ssh': True,  # Has errors
    'network': False
}

with ui.tabs() as tabs:
    # Add error styling conditionally
    project_tab = ui.tab('Project')
    ssh_tab = ui.tab('SSH').classes('text-red' if tab_errors['ssh'] else '')
    network_tab = ui.tab('Network')
```

### Nested Tabs
```python
with ui.tabs() as main_tabs:
    storage_tab = ui.tab('Storage')
    scripts_tab = ui.tab('Scripts')

with ui.tab_panels(main_tabs, value=storage_tab):
    with ui.tab_panel(storage_tab):
        # Nested tabs within storage panel
        with ui.tabs() as storage_tabs:
            stage1_tab = ui.tab('Stage-1')
            stage2_tab = ui.tab('Stage-2')
        
        with ui.tab_panels(storage_tabs, value=stage1_tab):
            with ui.tab_panel(stage1_tab):
                ui.label('Stage-1 storage configuration')
            with ui.tab_panel(stage2_tab):
                ui.label('Stage-2 storage configuration')
```

## Tab Content Organization

### Using Cards within Tabs
```python
with ui.tab_panel(network_tab):
    with ui.card().classes('w-full'):
        ui.label('Proxy Configuration').classes('text-h6')
        with ui.row():
            ui.switch('Enable proxy')
            ui.input('Proxy address', value='host.docker.internal:7890')
    
    with ui.card().classes('w-full mt-4'):
        ui.label('Port Mappings').classes('text-h6')
        # Port mapping content
```

### Scrollable Tab Content
```python
with ui.tab_panel(scripts_tab):
    with ui.scroll_area().classes('w-full h-96'):
        # Long content that scrolls
        for i in range(20):
            with ui.card():
                ui.label(f'Script {i}')
```

## Tab State Management

### Preserving Tab State
```python
from nicegui import app

# Store active tab in session
if 'active_tab' not in app.storage.user:
    app.storage.user['active_tab'] = 'project'

# Create tabs with stored value
with ui.tabs(value=app.storage.user['active_tab'], 
            on_change=lambda e: app.storage.user.update({'active_tab': e.value})) as tabs:
    ui.tab('project', label='Project')
    ui.tab('ssh', label='SSH')
```

### Tab Change Confirmation
```python
# Track unsaved changes
has_unsaved_changes = ui.state(False)

async def handle_tab_change(e):
    if has_unsaved_changes.value:
        # Show confirmation dialog
        with ui.dialog() as dialog, ui.card():
            ui.label('You have unsaved changes. Switch tabs anyway?')
            with ui.row():
                ui.button('Cancel', on_click=dialog.close)
                ui.button('Switch', on_click=lambda: [
                    dialog.close(),
                    tabs.set_value(e.value)
                ])
        dialog.open()
        # Prevent tab change
        e.sender.set_value(e.old_value)
```

## Styling Tabs

### Custom Tab Appearance
```python
# Apply custom classes
with ui.tabs().classes('bg-primary text-white') as tabs:
    ui.tab('Tab 1').classes('custom-tab')
    ui.tab('Tab 2').classes('custom-tab')

# Add custom CSS
ui.add_css('''
    .custom-tab {
        min-width: 120px;
        font-weight: bold;
    }
    .q-tab--active {
        background-color: rgba(255,255,255,0.2);
    }
''')
```

### Responsive Tab Design
```python
# Tabs that stack on mobile
with ui.tabs().classes('flex-wrap') as tabs:
    ui.tab('Project').classes('flex-auto')
    ui.tab('Configuration').classes('flex-auto')
    ui.tab('Advanced').classes('flex-auto')
```

## Common Patterns

### Tab with Action Buttons
```python
with ui.row().classes('w-full items-center'):
    with ui.tabs() as tabs:
        ui.tab('Overview')
        ui.tab('Details')
    
    ui.space()  # Push buttons to the right
    
    ui.button('Save', on_click=save_config)
    ui.button('Reset', on_click=reset_config)
```

### Dynamic Tab Creation
```python
# Create tabs from data
tab_configs = [
    {'id': 'project', 'label': 'Project', 'icon': 'folder'},
    {'id': 'ssh', 'label': 'SSH', 'icon': 'lock'},
    {'id': 'network', 'label': 'Network', 'icon': 'language'}
]

with ui.tabs() as tabs:
    tab_refs = {}
    for config in tab_configs:
        tab_refs[config['id']] = ui.tab(config['label']).props(f"icon={config['icon']}")

with ui.tab_panels(tabs):
    for config in tab_configs:
        with ui.tab_panel(tab_refs[config['id']]):
            ui.label(f"{config['label']} content")
```

## Best Practices

1. **Consistent Navigation**: Keep tab order and labels consistent
2. **Visual Feedback**: Show which tabs have errors or unsaved changes
3. **Lazy Loading**: Load tab content only when accessed for performance
4. **Mobile Friendly**: Test tab behavior on smaller screens
5. **Keyboard Navigation**: Tabs support keyboard navigation by default

## Resources

- NiceGUI Tabs Documentation: https://nicegui.io/documentation/tabs
- Quasar Tabs Component: https://quasar.dev/vue-components/tabs