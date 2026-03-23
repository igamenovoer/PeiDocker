## ADDED Requirements

### Requirement: Index page routes users by audience
The index page (`docs/index.md`) SHALL provide audience-based navigation with three clear paths: first-time users → manual/getting-started, returning users → manual/guides and scripts, developers/contributors → developer/.

#### Scenario: First-time user finds their starting point
- **WHEN** a first-time user lands on the docs index
- **THEN** they are directed to the getting-started section within the first screen

#### Scenario: Returning user finds reference material
- **WHEN** a returning user visits the docs index looking for a specific guide
- **THEN** they find links to guides, scripts catalog, and CLI reference without scrolling through beginner content

### Requirement: Index page includes examples section
The index page SHALL include a section pointing to both basic and advanced examples with brief descriptions of what each section offers.

#### Scenario: User wants to learn by example
- **WHEN** a user prefers learning from examples
- **THEN** the index page offers a clear path to both basic (single-feature) and advanced (scenario-driven) examples

### Requirement: Examples section has its own index
The examples directory SHALL have an `index.md` that explains the two-tier structure (basic vs advanced), how to use the examples, and a complete listing of all examples with one-line descriptions.

#### Scenario: User browses example catalog
- **WHEN** a user opens the examples index
- **THEN** they see all basic and advanced examples listed with one-line descriptions and can find the relevant one
