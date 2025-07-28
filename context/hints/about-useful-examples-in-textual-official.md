# About Useful Examples in Textual Official Documentation

This guide analyzes the most valuable Textual examples from the official documentation for building complex TUI applications, particularly wizard-style interfaces like PeiDocker GUI.

## 📚 **Critical Example Categories**

### 🏗️ **1. Application Architecture & Multi-Screen Patterns**

#### **Progressive Development Tutorial (stopwatch01-06 series)**
**Location:** `docs/examples/tutorial/stopwatch01.py` to `stopwatch06.py`

**Key Learning:** How to build complex applications incrementally

```python
# stopwatch01.py - Basic foundation
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

class StopwatchApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
```

```python
# stopwatch02.py - Widget composition
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, Digits

class Stopwatch(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")
```

**PeiDocker Application:** Start with basic screen structure, progressively add form widgets, validation, and styling.

#### **Demo Application Structure**
**Location:** `src/textual/demo/demo_app.py`

**Key Learning:** Mode-based multi-screen architecture

```python
class DemoApp(App):
    MODES = {
        "game": GameScreen,
        "home": HomeScreen,
        "projects": ProjectsScreen,
        "widgets": WidgetsScreen,
    }
    DEFAULT_MODE = "home"
    
    BINDINGS = [
        Binding("h", "app.switch_mode('home')", "Home"),
        Binding("g", "app.switch_mode('game')", "Game"),
    ]
```

**PeiDocker Application:** Implement similar mode-based architecture where each wizard step is a mode with validation gates.

### 🖥️ **2. Screen Management & Navigation**

#### **Basic Screen Definition**
**Location:** `docs/examples/guide/screens/screen01.py`, `screen02.py`

**Key Learning:** Screen registration and navigation patterns

```python
# Method 1: Static registration
class BSODApp(App):
    SCREENS = {"bsod": BSOD}
    BINDINGS = [("b", "push_screen('bsod')", "BSOD")]

# Method 2: Dynamic installation  
class BSODApp(App):
    def on_mount(self) -> None:
        self.install_screen(BSOD(), name="bsod")
```

**PeiDocker Application:** Use dynamic screen installation for wizard steps with stack-based navigation.

#### **Question-Style Screens** ⭐
**Location:** `docs/examples/guide/screens/questions01.py`

**Key Learning:** Perfect pattern for wizard steps

```python
class QuestionScreen(Screen[bool]):
    def __init__(self, question: str) -> None:
        self.question = question
        super().__init__()
    
    def compose(self) -> ComposeResult:
        yield Label(self.question)
        yield Button("Yes", id="yes", variant="success")
        yield Button("No", id="no")
    
    @on(Button.Pressed, "#yes")
    def handle_yes(self) -> None:
        self.dismiss(True)  # Return result to parent

# Usage with await pattern
@work
async def on_mount(self) -> None:
    if await self.push_screen_wait(QuestionScreen("Do you like Textual?")):
        self.notify("Good answer!")
```

**PeiDocker Application:** Each wizard step is a parameterized screen that collects configuration and returns data.

### 📝 **3. Form Input & Validation Patterns**

#### **Comprehensive Input Validation** ⭐
**Location:** `docs/examples/widgets/input_validation.py`

**Key Learning:** Real-time validation with visual feedback

```python
class InputApp(App):
    CSS = """
    Input.-valid { border: tall $success 60%; }
    Input.-valid:focus { border: tall $success; }
    """
    
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Enter a number...",
            validators=[
                Number(minimum=1, maximum=100),
                Function(is_even, "Value is not even."),
                Palindrome(),  # Custom validator
            ],
        )
    
    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        if not event.validation_result.is_valid:
            self.query_one(Pretty).update(event.validation_result.failure_descriptions)
```

**PeiDocker Application:** Implement comprehensive validation for project names, paths, ports with real-time feedback.

#### **Boolean & Choice Controls**
**Location:** `docs/examples/widgets/checkbox.py`, `radio_button.py`

```python
# Checkbox for boolean options
yield Checkbox("Enable SSH", value=True, id="ssh-enable")

# Radio button groups for exclusive choices
with RadioSet():
    yield RadioButton("ubuntu:24.04", value=True)
    yield RadioButton("ubuntu:22.04")
    yield RadioButton("nvidia/cuda:12.6")
```

**PeiDocker Application:** SSH enable/disable, GPU support, mirror selection, proxy settings.

### ⚡ **4. State Management & Reactivity**

#### **Reactive Properties with Validation**
**Location:** `docs/examples/guide/reactivity/validate01.py`

**Key Learning:** Automatic state validation and UI synchronization

```python
class ValidateApp(App):
    count = reactive(0)
    
    def validate_count(self, count: int) -> int:
        """Auto-called validation with bounds clamping."""
        if count < 0:
            count = 0
        elif count > 10:
            count = 10
        return count
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.count += 1  # UI automatically updates
```

**PeiDocker Application:** Use reactive properties for wizard configuration state with validation ensuring data integrity.

### 🎨 **5. Layout & UI Organization**

#### **Container Organization**
**Location:** `docs/examples/guide/layout/vertical_layout.py`

```python
class VerticalLayoutExample(App):
    def compose(self) -> ComposeResult:
        yield Static("Header", classes="header")
        yield Static("Content", classes="content") 
        yield Static("Footer", classes="footer")
```

**CSS Integration:**
```css
.header { height: 3; background: $primary; }
.content { height: 1fr; }  /* Flexible height */
.footer { height: 3; background: $secondary; }
```

**PeiDocker Application:** Vertical layouts for wizard steps with horizontal button groups for navigation.

### 🔄 **6. Dynamic Content & Lists**

#### **Dynamic Option Lists**
**Location:** `docs/examples/widgets/option_list_strings.py`

```python
class OptionListApp(App):
    def compose(self) -> ComposeResult:
        yield OptionList(
            "tuna - Tsinghua University (China)",
            "aliyun - Alibaba Cloud (China)", 
            "default - Ubuntu Default",
        )
```

**PeiDocker Application:** Mirror selection, port mapping lists, environment variable management.

#### **Key Binding Patterns**
**Location:** `docs/examples/guide/actions/actions01.py`

```python
class ActionsApp(App):
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "continue", "Continue"),
        ("ctrl+p", "previous", "Previous"),
        ("ctrl+n", "next", "Next"),
    ]
    
    def action_previous(self) -> None:
        # Navigate to previous wizard step
        pass
```

## 🎯 **Implementation Strategy by PeiDocker Screen**

### **SC-0 (Startup Screen)**
**Study Examples:**
- `examples/splash.py` - Splash screen patterns
- `widgets/loading_indicator.py` - System validation display

```python
class StartupScreen(Screen):
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()
        yield Static("Checking Docker availability...")
```

### **SC-1 (Project Directory Selection)**
**Study Examples:**
- `widgets/input.py`, `input_validation.py` - Path input validation
- `widgets/directory_tree.py` - Directory selection

```python
class ProjectDirScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Project directory...",
            validators=[DirectoryValidator()],
        )
        yield Button("Browse...", id="browse")
```

### **SC-3-13 (Wizard Configuration Steps)**
**Study Examples:**
- `guide/screens/questions01.py` - Question interface pattern
- `widgets/radio_button.py`, `checkbox.py` - Option selection
- `guide/reactivity/watch01.py` - State management

```python
class WizardStep(Screen[dict]):
    def __init__(self, step_data: dict) -> None:
        self.step_data = step_data
        super().__init__()
    
    def compose(self) -> ComposeResult:
        yield Static(f"Step {self.step_data['number']} of 11")
        # Step-specific form widgets
        yield Button("Previous", id="prev")
        yield Button("Next", id="next")
    
    @on(Button.Pressed, "#next")
    def handle_next(self) -> None:
        if self.validate_step():
            self.dismiss(self.collect_data())
```

## 🔧 **Advanced Patterns for Complex Applications**

### **CSS Integration & Styling**
**Location:** `examples/calculator.tcss`, `guide/styles/`

```css
/* External CSS file for maintainable styling */
.wizard-step {
    layout: vertical;
    align: center top;
    padding: 2;
}

.form-section {
    border: round $accent;
    margin: 1;
    padding: 1;
}

.navigation-buttons {
    layout: horizontal;
    align: center bottom;
    height: 3;
}
```

### **Error Handling & User Feedback**
**Study Examples:**
- `widgets/toast.py` - Success/error notifications
- Input validation patterns with visual feedback

```python
def validate_and_notify(self, value: str) -> bool:
    if not self.is_valid(value):
        self.notify("Invalid input", severity="error")
        return False
    return True
```

## 📋 **Development Workflow**

### **Phase 1: Foundation**
1. Study `tutorial/stopwatch01.py` - Basic app structure
2. Implement basic screen navigation from `guide/screens/screen01.py`
3. Set up mode-based architecture from `demo_app.py`

### **Phase 2: Core Functionality**
1. Study `guide/screens/questions01.py` - Implement wizard steps
2. Add form validation from `widgets/input_validation.py`
3. Implement state management from `guide/reactivity/validate01.py`

### **Phase 3: Polish & Enhancement**
1. Add dynamic lists from `widgets/option_list_strings.py`
2. Implement styling from `examples/calculator.tcss`
3. Add advanced features like `widgets/toast.py` notifications

## 🔗 **Additional Resources**

- **Official Tutorial:** [Textual Tutorial](https://textual.textualize.io/tutorial/)
- **Widget Gallery:** [Textual Widget Gallery](https://textual.textualize.io/widget_gallery/)
- **Examples Repository:** `docs/examples/` directory in Textual repo
- **API Reference:** [Textual API Docs](https://textual.textualize.io/api/)

## ⭐ **Most Critical Examples for PeiDocker**

1. **`guide/screens/questions01.py`** - Perfect wizard step pattern
2. **`widgets/input_validation.py`** - Comprehensive form validation
3. **`tutorial/stopwatch01-06.py`** - Progressive development approach
4. **`src/textual/demo/demo_app.py`** - Multi-screen architecture
5. **`guide/reactivity/validate01.py`** - State management with validation

These examples provide the complete foundation for implementing PeiDocker's 11-step wizard interface with proper validation, navigation, and state management.
