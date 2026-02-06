# How to Implement Bidirectional Data Binding in NiceGUI

This guide covers bidirectional data binding techniques in the NiceGUI framework, focusing on specialized dataclasses and comparing them with Pydantic-based data models for GUI binding.

## Overview

NiceGUI provides built-in support for bidirectional data binding between UI elements and data models. This allows automatic synchronization between the user interface and the underlying data without manual event handling.

## 1. Basic Data Binding

### Simple Class Binding

```python
from nicegui import ui

class Demo:
    def __init__(self):
        self.number = 1

demo = Demo()
ui.slider(min=1, max=3).bind_value(demo, 'number')
ui.toggle({1: 'A', 2: 'B', 3: 'C'}).bind_value(demo, 'number')
ui.number().bind_value(demo, 'number')
```

## 2. NiceGUI Bindable Properties (High Performance)

For maximum performance, use `BindableProperty` which automatically detects write access and triggers value propagation immediately.

```python
from nicegui import binding, ui

class Demo:
    number = binding.BindableProperty()

    def __init__(self):
        self.number = 1

demo = Demo()
ui.slider(min=1, max=3).bind_value(demo, 'number')
ui.toggle({1: 'A', 2: 'B', 3: 'C'}).bind_value(demo, 'number')
ui.number(min=1, max=3).bind_value(demo, 'number')
```

## 3. Bindable Dataclass (Specialized Approach)

The `@bindable_dataclass` decorator provides the most convenient way to create classes with bindable properties. It automatically makes all dataclass fields bindable while retaining all benefits of regular dataclasses.

```python
from nicegui import binding, ui

@binding.bindable_dataclass
class UserProfile:
    name: str = "John Doe"
    age: int = 25
    email: str = "john@example.com"
    is_active: bool = True

# Create model instance
profile = UserProfile()

# Bind UI elements to model properties
ui.input('Name').bind_value(profile, 'name')
ui.number('Age', min=0, max=120).bind_value(profile, 'age')
ui.input('Email').bind_value(profile, 'email')
ui.checkbox('Active').bind_value(profile, 'is_active')

# Display current values (automatically updates)
ui.label().bind_text_from(profile, 'name', 
                         backward=lambda n: f'Hello, {n}!')
ui.label().bind_text_from(profile, 'age', 
                         backward=lambda a: f'Age: {a} years')
```

### Advanced Dataclass with Type Hints

```python
from nicegui import binding, ui
from typing import Optional
from dataclasses import field

@binding.bindable_dataclass
class ApplicationSettings:
    theme: str = "light"
    font_size: int = 14
    notifications: bool = True
    user_name: str = ""
    tags: list = field(default_factory=list)
    
settings = ApplicationSettings()

# Bind various UI controls
ui.select(['light', 'dark', 'auto'], value='light').bind_value(settings, 'theme')
ui.slider(min=8, max=24, value=14).bind_value(settings, 'font_size')
ui.checkbox('Enable notifications').bind_value(settings, 'notifications')
```

## 4. Transformation Functions

Use `forward` and `backward` transformation functions to convert values during binding:

```python
from nicegui import ui

i = ui.input(value='Lorem ipsum')
ui.label().bind_text_from(i, 'value',
                          backward=lambda text: f'{len(text)} characters')
```

## 5. Pydantic-Based Data Models Comparison

### Pydantic Approach

```python
from pydantic import BaseModel, Field, validator
from nicegui import ui

class UserModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=120)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.title()

# For NiceGUI binding, you need wrapper properties
class BindableUserModel:
    def __init__(self):
        self._model = UserModel(name="John", age=25, email="john@example.com")
    
    @property
    def name(self):
        return self._model.name
    
    @name.setter
    def name(self, value):
        try:
            self._model = self._model.copy(update={'name': value})
        except ValueError as e:
            ui.notify(str(e), type='negative')
    
    # Similar for other properties...

user = BindableUserModel()
ui.input('Name').bind_value(user, 'name')
```

### Comparison: Bindable Dataclass vs Pydantic

| Feature | Bindable Dataclass | Pydantic BaseModel |
|---------|-------------------|-------------------|
| **Performance** | ✅ High (built-in binding) | ⚠️ Requires wrapper layer |
| **Validation** | ⚠️ Manual via `__post_init__` | ✅ Automatic with decorators |
| **Type Safety** | ✅ Python type hints | ✅ Runtime validation |
| **Serialization** | ⚠️ Manual | ✅ Built-in JSON/dict support |
| **Learning Curve** | ✅ Simple, familiar dataclass syntax | ⚠️ Pydantic-specific features |
| **GUI Integration** | ✅ Native NiceGUI support | ⚠️ Requires binding adapters |
| **Field Constraints** | ⚠️ Manual validation | ✅ Rich field constraints |

## 6. Best Practices

### When to Use Bindable Dataclass

- **Primary GUI applications** where binding performance is critical
- **Simple to moderate data validation** requirements
- **Rapid prototyping** with immediate UI feedback
- **Performance-sensitive** applications with frequent UI updates

```python
@binding.bindable_dataclass
class FormData:
    username: str = ""
    password: str = ""
    remember_me: bool = False
    
    def __post_init__(self):
        # Simple validation
        if len(self.username) > 50:
            raise ValueError("Username too long")
```

### When to Use Pydantic with Adapters

- **Complex data validation** requirements
- **API integration** where serialization is important
- **Enterprise applications** with strict data governance
- **Backend-frontend data synchronization**

```python
from pydantic import BaseModel
from nicegui import binding

class PydanticAdapter:
    """Adapter to make Pydantic models work with NiceGUI binding"""
    
    def __init__(self, pydantic_model: BaseModel):
        self._model = pydantic_model
        self._bindings = {}
    
    def bind_property(self, prop_name: str):
        if prop_name not in self._bindings:
            self._bindings[prop_name] = binding.BindableProperty()
            setattr(self, prop_name, self._bindings[prop_name])
        return self._bindings[prop_name]
```

## 7. Advanced Binding Patterns

### Dictionary Binding

```python
from nicegui import ui

data = {'name': 'Bob', 'age': 17}

ui.label().bind_text_from(data, 'name', backward=lambda n: f'Name: {n}')
ui.label().bind_text_from(data, 'age', backward=lambda a: f'Age: {a}')
ui.button('Turn 18', on_click=lambda: data.update(age=18))
```

### Storage Binding

```python
from nicegui import app, ui

@ui.page('/')
def index():
    ui.textarea('This note is kept between visits')
        .classes('w-full').bind_value(app.storage.user, 'note')
```

## Performance Considerations

1. **Bindable Properties**: Immediate propagation, no polling overhead
2. **Active Links**: Checked every 0.1 seconds (configurable via `binding_refresh_interval`)
3. **Complex Objects**: Can be costly with active links; prefer bindable properties

### Performance Monitoring

```python
from nicegui import binding

# Configure propagation time threshold (default: 0.01 seconds)
binding.MAX_PROPAGATION_TIME = 0.005  # Show warning if binding takes >5ms
```

## Resources

- [NiceGUI Binding Documentation](https://nicegui.io/documentation/section_binding_properties)
- [Python Dataclasses Documentation](https://docs.python.org/3/library/dataclasses.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Bindable Dataclass GitHub Discussion](https://github.com/zauberzeug/nicegui/discussions/3957)

## Summary

Choose **Bindable Dataclass** for GUI-focused applications where binding performance and simplicity are priorities. Choose **Pydantic** with adapters when you need complex validation, serialization, and integration with data APIs, but be prepared for additional complexity in the binding layer.
