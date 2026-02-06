# Task: Update Screen 0 with Project Directory Analysis

## Command Summary
Update the Screen 0 documentation in `@context\plans\gui\screens\sc-0\` to handle project directory analysis when `--project-dir` is provided.

## Requirements

### 1. Project Structure Reference
- If project directory is given, the project will look like `@context\summaries\user-project-structure.md`
- Save the top-level structure in the documentation

### 2. Existing Project Detection
- Look for `user_config.yml` in the project directory
- If found: This means pre-existing project
  - Load `user_config.yml` into memory
  - Map it to wizard states for pre-population
  - Show a flag indicating "existing project"

### 3. New Project Detection  
- If `user_config.yml` does not exist: This is a new project
- Create user_config from scratch during wizard
- Show a flag indicating "new project"

### 4. Error Handling
- If `user_config.yml` exists but failed to load:
  - Show an error in the status summary
  - Note that the file will be recreated
  - Treat this as a new project

### 5. Display Requirements
- **Updated requirement**: No need to show detailed project structure in the summary
- Keep status display clean and minimal
- Show only project type flags (existing/new/error) with configuration loading status

## Files Referenced
- `@context\plans\gui\screens\sc-0\` - Target documentation directory
- `@context\summaries\user-project-structure.md` - Project structure reference
- `user_config.yml` - Configuration file to detect/load

## Implementation Focus
- Project directory validation and analysis
- Configuration file loading and error handling  
- State mapping for wizard pre-population
- Clean status display without structure trees