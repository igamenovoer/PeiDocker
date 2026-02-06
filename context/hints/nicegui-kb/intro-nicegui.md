# Introduction to NiceGUI Framework

NiceGUI is a Python-based web UI framework that enables rapid development of web applications with minimal code. It's particularly well-suited for dashboards, control interfaces, and administrative tools.

## Core Features

### 1. Python-Centric Approach
- Write UI code entirely in Python
- No need for HTML, CSS, or JavaScript knowledge
- Real-time communication between browser and Python backend

### 2. Architecture
- **Backend**: FastAPI server
- **Frontend**: Vue.js/Quasar components
- **Communication**: WebSocket via socket.io
- **Server**: Single uvicorn worker for simplicity

### 3. Key Components
```python
from nicegui import ui, app, events

# Basic UI elements
ui.label('Hello World')
ui.button('Click me', on_click=lambda: ui.notify('Clicked!'))
ui.input('Enter text', on_change=lambda e: print(e.value))
```

## Layout System

### Containers
```python
# Rows and columns for layout
with ui.row():
    ui.label('Left')
    ui.label('Right')

with ui.column():
    ui.label('Top')
    ui.label('Bottom')

# Cards for grouping
with ui.card():
    ui.label('Card content')
```

### Flex Layout
- Default flex layout for containers
- Responsive design with Tailwind CSS classes
- Material Design components via Quasar

## Event Handling

### Direct Event Binding
```python
# Button click
ui.button('Click', on_click=lambda: handle_click())

# Input change
ui.input('Text', on_change=lambda e: process_input(e.value))

# Custom events
ui.on('custom-event', lambda e: handle_custom(e.args))
```

### Async Support
```python
async def fetch_data():
    # Async operations supported
    response = await httpx.get('https://api.example.com')
    return response.json()

ui.button('Fetch', on_click=fetch_data)
```

## State Management

### Reactive Variables
```python
# Create reactive state
count = ui.state(0)

# Bind to UI
ui.label().bind_text_from(count, 'value')
ui.button('Increment', on_click=lambda: count.set(count.value + 1))
```

### Data Binding
```python
# Two-way binding
data = {'name': 'John'}
ui.input().bind_value(data, 'name')
```

## Page and Routing

```python
@ui.page('/')
def index():
    ui.label('Home page')

@ui.page('/about')
def about():
    ui.label('About page')
    
ui.run()
```

## Running the Application

```python
# Basic run
ui.run()

# With configuration
ui.run(
    port=8080,
    title='My App',
    favicon='🚀',
    dark=True,
    reload=True  # Auto-reload on code changes
)
```

## Best Practices

1. **Component Organization**: Create reusable components as functions
2. **State Management**: Use reactive variables for dynamic UI
3. **Event Handling**: Prefer lambdas for simple actions
4. **Layout**: Use containers (row, column, card) for structure
5. **Styling**: Apply Tailwind classes via `.classes()` method

## Resources

- Official Documentation: https://nicegui.io/documentation
- GitHub Repository: https://github.com/zauberzeug/nicegui
- Examples: https://github.com/zauberzeug/nicegui/tree/main/examples