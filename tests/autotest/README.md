# GUI Automated Test Pipeline

This directory contains automated tests for the PeiDocker GUI application.

## Screenshots Captured

The test pipeline captures screenshots of the first two GUI screens:

- **SC-0: Application Startup Screen** - Shows system validation and branding
- **SC-1: Project Directory Selection Screen** - Shows directory input form and real-time log viewer

## Files

- `test_gui_screenshots.py` - Main pytest test file for GUI screenshot capture
- `gui_test_app.py` - Test wrapper around the main GUI application  
- `__snapshots__/` - Generated pytest snapshots for regression testing
- `README.md` - This documentation file

## Running Tests

### Individual Tests

```bash
# Test SC-0 (Startup Screen)
pixi run -e dev pytest tests/autotest/test_gui_screenshots.py::TestGUIScreenshots::test_sc0_startup_screen -v

# Test SC-1 (Project Setup Screen)  
pixi run -e dev pytest tests/autotest/test_gui_screenshots.py::TestGUIScreenshots::test_sc1_project_setup_screen -v
```

### All Tests

```bash
# Run all GUI screenshot tests
pixi run -e dev pytest tests/autotest/test_gui_screenshots.py -v
```

### Update Snapshots

When the GUI changes and you need to update the baseline snapshots:

```bash
# Update all snapshots after verifying changes are correct
pixi run -e dev pytest tests/autotest/test_gui_screenshots.py --snapshot-update
```

## Output Location

Screenshots are automatically saved to:
- Test snapshots: `tests/autotest/__snapshots__/test_gui_screenshots/`
- Output screenshots: `tmp/output/gui-screenshots/`
  - `sc-0-startup-screen.svg` - SC-0 Application Startup Screen
  - `sc-1-project-setup-screen.svg` - SC-1 Project Directory Selection Screen

## How It Works

1. **GUI Test App**: `gui_test_app.py` creates a testable wrapper around the main PeiDocker GUI
2. **Screenshot Capture**: Uses `pytest-textual-snapshot` to capture SVG screenshots headlessly
3. **Screen Navigation**: Simulates user interactions (waiting, key presses) to navigate between screens
4. **File Management**: Automatically copies generated snapshots to the output directory with descriptive names

## Dependencies

- `pytest-textual-snapshot` - For headless GUI screenshot capture
- `textual` - The GUI framework
- `pytest` - Test framework

All dependencies are managed through the pixi development environment.

## Terminal Size

Tests use a consistent terminal size of 120x40 characters to ensure reproducible screenshots across different development environments.

## Development Notes

- Tests run headlessly without opening actual GUI windows
- System validation checks are included (Docker availability, Python version, etc.)
- Real-time navigation between screens is tested
- Screenshots can be used for visual verification and regression testing