# docs-examples-advanced Specification

## Purpose
TBD - created by archiving change rewrite-docs-structure. Update Purpose after archive.
## Requirements
### Requirement: Advanced examples are scenario-driven
Each advanced example SHALL be framed as a user goal (e.g., "I want a GPU ML dev environment with Pixi and Jupyter") and compose multiple features to achieve that goal. The doc page SHALL include the complete `user_config.yml` embedded inline, explain why each feature is included, and provide the full workflow from create to connect.

#### Scenario: User builds an ML development environment
- **WHEN** a user reads the ML dev GPU example
- **THEN** they get a complete config combining GPU, pixi, storage volumes, SSH, and port mapping for Jupyter, with explanations of each choice

### Requirement: Advanced examples have corresponding configs in examples/
Each advanced example doc page SHALL have a corresponding `examples/advanced/<slug>/` directory with a `user_config.yml` and any supporting files (custom scripts, .env files). The doc page SHALL reference this source path.

#### Scenario: User copies an advanced example
- **WHEN** a user wants to use an advanced example as a starting point
- **THEN** they find the source path in the doc and can copy the `examples/advanced/<slug>/` directory

### Requirement: Advanced examples cover real-world scenarios
The advanced examples set SHALL include at minimum: ML development with GPU, Node.js web development, team shared development environment, corporate proxy in China, ROS2 robotics development, and OpenGL/OpenCV vision development.

#### Scenario: User finds a scenario matching their use case
- **WHEN** a user browses the advanced examples index
- **THEN** they find a scenario description matching their goal and can use it as a starting point

### Requirement: Advanced examples reference concepts and basic examples
Each advanced example SHALL reference the relevant concept docs and basic examples for deeper understanding of individual features used.

#### Scenario: User wants to understand a specific feature in an advanced example
- **WHEN** a user sees GPU configuration in an advanced example and wants more detail
- **THEN** the example links to `manual/concepts/two-stage-architecture.md` and `examples/basic/02-gpu-container.md`

### Requirement: Advanced examples adapted from existing legacy configs where applicable
Advanced examples SHALL incorporate and improve upon relevant legacy configs from `src/pei_docker/examples/legacy/` (e.g., `pixi-ml-gpu.yml` → `ml-dev-gpu`, `gpu-with-host-mount.yml` → content absorbed into relevant scenarios) rather than being written from scratch where good prior art exists.

#### Scenario: Legacy pixi-ml-gpu config is modernized
- **WHEN** creating the ML dev GPU advanced example
- **THEN** the config builds on `legacy/pixi-ml-gpu.yml` patterns with updated explanations and any corrections needed

