# How to Create Forms with Validation in NiceGUI

This guide covers creating forms, implementing validation, and managing form state in NiceGUI applications.

## Basic Form Elements

### Text Inputs
```python
from nicegui import ui

# Basic input
name_input = ui.input('Name', placeholder='Enter your name')

# Password input
password_input = ui.input('Password', password=True)

# Input with validation
email_input = ui.input('Email').props('type=email')

# Textarea for multi-line
description = ui.textarea('Description').props('rows=4')

# Number input
age_input = ui.number('Age', min=0, max=120, step=1)
```

### Selection Elements
```python
# Dropdown select
ui.select(
    options=['ubuntu:22.04', 'ubuntu:20.04', 'debian:11'],
    label='Base Image',
    value='ubuntu:22.04'
)

# Radio buttons
ui.radio(
    options=['Stage-1', 'Stage-2'], 
    value='Stage-1'
).props('inline')

# Checkbox
ui.checkbox('Enable SSH', value=True)

# Switch toggle
ui.switch('Enable Proxy', value=False)
```

## Form Validation

### Real-time Validation
```python
def create_validated_input():
    """Input with real-time validation"""
    
    def validate_email(value):
        import re
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        is_valid = bool(re.match(pattern, value))
        
        # Update visual feedback
        email_input.props('error' if not is_valid else '')
        error_msg.set_text('' if is_valid else 'Invalid email format')
        return is_valid
    
    email_input = ui.input('Email', on_change=lambda e: validate_email(e.value))
    error_msg = ui.label('').classes('text-red text-xs')
    
    return email_input
```

### Form-wide Validation
```python
class FormValidator:
    """Validate entire form"""
    
    def __init__(self):
        self.errors = {}
        self.fields = {}
    
    def add_field(self, name, element, validator):
        """Register field with validator"""
        self.fields[name] = {
            'element': element,
            'validator': validator
        }
    
    def validate_all(self):
        """Validate all fields"""
        self.errors.clear()
        is_valid = True
        
        for name, field in self.fields.items():
            value = field['element'].value
            error = field['validator'](value)
            
            if error:
                self.errors[name] = error
                field['element'].props('error')
                is_valid = False
            else:
                field['element'].props('')
        
        return is_valid

# Usage
validator = FormValidator()

# Define validators
def required(value):
    return 'Required' if not value else None

def min_length(length):
    return lambda value: f'Minimum {length} characters' if len(value) < length else None

# Create form
name = ui.input('Name')
validator.add_field('name', name, required)

password = ui.input('Password', password=True)
validator.add_field('password', password, min_length(8))
```

## Complex Form Patterns

### Dynamic Form Fields
```python
def create_dynamic_list(label, default_items=None):
    """Create dynamic list with add/remove"""
    
    items = default_items or []
    container = ui.column()
    
    def render_items():
        container.clear()
        with container:
            for i, item in enumerate(items):
                with ui.row().classes('items-center gap-2'):
                    ui.input(value=item, on_change=lambda e, idx=i: update_item(idx, e.value))
                    ui.button(icon='delete', on_click=lambda idx=i: remove_item(idx)).props('flat')
    
    def add_item():
        items.append('')
        render_items()
    
    def remove_item(index):
        items.pop(index)
        render_items()
    
    def update_item(index, value):
        items[index] = value
    
    # UI
    ui.label(label).classes('text-h6')
    render_items()
    ui.button('Add Item', icon='add', on_click=add_item).props('outline')
    
    return items

# Usage
port_mappings = create_dynamic_list('Port Mappings', ['8080:80', '2222:22'])
```

### Conditional Fields
```python
def create_storage_form():
    """Form with conditional fields"""
    
    storage_type = ui.select(
        options=['auto-volume', 'manual-volume', 'host', 'image'],
        label='Storage Type',
        value='auto-volume'
    )
    
    # Conditional inputs
    volume_name_input = ui.input('Volume Name').props('disable')
    host_path_input = ui.input('Host Path').props('disable')
    
    def update_fields():
        # Enable/disable based on selection
        volume_name_input.props('disable' if storage_type.value != 'manual-volume' else '')
        host_path_input.props('disable' if storage_type.value != 'host' else '')
        
        # Clear disabled fields
        if storage_type.value != 'manual-volume':
            volume_name_input.value = ''
        if storage_type.value != 'host':
            host_path_input.value = ''
    
    storage_type.on('change', update_fields)
    update_fields()  # Initial state
```

## Form State Management

### Dirty State Tracking
```python
class FormStateManager:
    """Track form modifications"""
    
    def __init__(self):
        self.original_state = {}
        self.current_state = {}
        self.is_dirty = ui.state(False)
    
    def initialize(self, data):
        """Set initial form state"""
        self.original_state = data.copy()
        self.current_state = data.copy()
        self.is_dirty.value = False
    
    def update_field(self, field, value):
        """Update field and check dirty state"""
        self.current_state[field] = value
        self.is_dirty.value = self.current_state != self.original_state
    
    def save(self):
        """Save current as original"""
        self.original_state = self.current_state.copy()
        self.is_dirty.value = False
    
    def reset(self):
        """Reset to original"""
        self.current_state = self.original_state.copy()
        self.is_dirty.value = False

# Usage
form_state = FormStateManager()

# Create form with state tracking
def create_project_form():
    form_state.initialize({
        'name': 'my-project',
        'base_image': 'ubuntu:22.04'
    })
    
    name = ui.input('Project Name', value=form_state.current_state['name'])
    name.on('change', lambda e: form_state.update_field('name', e.value))
    
    image = ui.select(
        options=['ubuntu:22.04', 'ubuntu:20.04'],
        value=form_state.current_state['base_image']
    )
    image.on('change', lambda e: form_state.update_field('base_image', e.value))
    
    # Save button enabled only when dirty
    save_btn = ui.button('Save', on_click=lambda: [
        save_configuration(),
        form_state.save()
    ])
    save_btn.bind_enabled_from(form_state.is_dirty, 'value')
```

### Form Submission
```python
async def handle_form_submission():
    """Handle form submission with validation"""
    
    # Create loading state
    submit_button.props('loading')
    
    try:
        # Validate
        if not validator.validate_all():
            ui.notify('Please fix validation errors', type='negative')
            return
        
        # Collect form data
        form_data = {
            field_name: field['element'].value 
            for field_name, field in validator.fields.items()
        }
        
        # Process submission
        await process_data(form_data)
        
        # Success feedback
        ui.notify('Form submitted successfully', type='positive')
        
        # Reset form
        form_state.save()
        
    except Exception as e:
        ui.notify(f'Error: {str(e)}', type='negative')
    
    finally:
        submit_button.props('loading=false')
```

## PeiDocker-Specific Forms

### SSH Configuration Form
```python
def create_ssh_form():
    """SSH configuration form with validation"""
    
    with ui.card():
        ui.label('SSH Configuration').classes('text-h6')
        
        # Enable SSH
        ssh_enabled = ui.switch('Enable SSH', value=True)
        
        # SSH fields container
        ssh_fields = ui.column()
        
        def render_ssh_fields():
            ssh_fields.clear()
            if not ssh_enabled.value:
                return
            
            with ssh_fields:
                # Port configuration
                with ui.row().classes('gap-4'):
                    ui.number('Container Port', value=22, min=1, max=65535)
                    ui.number('Host Port', value=2222, min=1, max=65535)
                
                # User configuration
                ui.input('Username', value='dev')
                password = ui.input('Password', password=True)
                ui.input('UID', value='1000').props('type=number')
                
                # SSH keys
                with ui.expansion('SSH Keys', icon='key'):
                    ui.textarea('Public Key').props('rows=3')
                    ui.textarea('Private Key').props('rows=3')
        
        ssh_enabled.on('change', render_ssh_fields)
        render_ssh_fields()
```

### Port Mapping Form
```python
def create_port_mapping_form():
    """Port mapping form with validation"""
    
    port_mappings = []
    
    def validate_port_mapping(value):
        """Validate port mapping format"""
        import re
        # Support single port or range
        pattern = r'^(\d{1,5}(-\d{1,5})?):(\d{1,5}(-\d{1,5})?)$'
        if not re.match(pattern, value):
            return 'Invalid format. Use HOST:CONTAINER or HOST_RANGE:CONTAINER_RANGE'
        
        # Validate port numbers
        parts = value.split(':')
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                if int(start) > int(end):
                    return 'Invalid range: start > end'
            else:
                port = int(part)
                if port < 1 or port > 65535:
                    return 'Port must be between 1 and 65535'
        
        return None
    
    def add_port_mapping():
        mapping_id = len(port_mappings)
        container = ui.row().classes('items-center gap-2')
        
        input_field = ui.input(
            placeholder='8080:80 or 9000-9099:9000-9099',
            on_change=lambda e: validate_and_update(mapping_id, e.value)
        ).classes('flex-grow')
        
        error_label = ui.label('').classes('text-red text-xs')
        
        def validate_and_update(idx, value):
            error = validate_port_mapping(value)
            error_label.text = error or ''
            input_field.props('error' if error else '')
            if not error and idx < len(port_mappings):
                port_mappings[idx] = value
        
        ui.button(
            icon='delete',
            on_click=lambda: remove_mapping(container, mapping_id)
        ).props('flat')
        
        port_mappings.append('')
        
        return container, input_field, error_label
    
    def remove_mapping(container, idx):
        container.delete()
        port_mappings.pop(idx)
    
    # UI
    ui.label('Port Mappings').classes('text-h6')
    mappings_container = ui.column()
    
    # Add default mappings
    with mappings_container:
        add_port_mapping()
    
    ui.button('Add Port Mapping', icon='add', on_click=lambda: mappings_container.add(add_port_mapping()[0]))
```

## Form Layout

### Responsive Form Grid
```python
def create_form_grid():
    """Responsive form layout"""
    
    with ui.grid(columns=2).classes('gap-4 w-full'):
        # First column
        ui.input('First Name').classes('col-span-2 sm:col-span-1')
        ui.input('Last Name').classes('col-span-2 sm:col-span-1')
        
        # Full width
        ui.input('Email').classes('col-span-2')
        
        # Half width on desktop
        ui.select(['Option 1', 'Option 2'], label='Choice').classes('col-span-2 sm:col-span-1')
        ui.number('Amount').classes('col-span-2 sm:col-span-1')
```

### Grouped Sections
```python
def create_grouped_form():
    """Form with grouped sections"""
    
    with ui.column().classes('gap-6'):
        # Basic Information
        with ui.card():
            ui.label('Basic Information').classes('text-h6 mb-4')
            ui.input('Project Name')
            ui.select(['ubuntu:22.04', 'debian:11'], label='Base Image')
        
        # Advanced Settings
        with ui.expansion('Advanced Settings', icon='settings').classes('w-full'):
            ui.checkbox('Enable GPU Support')
            ui.checkbox('Use Custom Entry Point')
```

## Best Practices

1. **Validate on blur** - Don't validate while user is typing
2. **Clear error messages** - Remove errors when user fixes them
3. **Disable submit during validation** - Prevent multiple submissions
4. **Show loading states** - Indicate when form is processing
5. **Save draft state** - Use storage to prevent data loss
6. **Provide helpful placeholders** - Guide users with examples
7. **Group related fields** - Use cards and expansions for organization
8. **Make required fields clear** - Use visual indicators

## Resources

- NiceGUI Input Documentation: https://nicegui.io/documentation/input
- NiceGUI Form Elements: https://nicegui.io/documentation/section_controls
- Quasar Form Components: https://quasar.dev/vue-components/input