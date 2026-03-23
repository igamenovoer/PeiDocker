## ADDED Requirements

### Requirement: CLI reference documents all commands with options
The CLI reference (`manual/cli-reference.md`) SHALL document all CLI commands (create, configure, remove, gui) with their full option sets, default values, and usage examples.

#### Scenario: User checks configure command options
- **WHEN** a user reads the CLI reference section for `configure`
- **THEN** they find all options (`-p`, `-c`, `-f`, `--with-merged`) with descriptions, defaults, and examples

### Requirement: CLI reference includes quick template descriptions
The CLI reference SHALL document all available quick templates (minimal, cn-dev, cn-demo, cn-ml) with what each template provides.

#### Scenario: User chooses a quick template
- **WHEN** a user reads the quick templates section
- **THEN** they can select the template that best matches their use case
