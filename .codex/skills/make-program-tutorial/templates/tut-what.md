---
tutorial_name: {{tutorial-name}}
created_at: {{yyyy-mm-ddThh:mm:ssZ}}
base_commit: {{git_commit_hash}}
topic: {{Service/Library Name}} - {{Task Name}}
runtime:
  os: {{os}}
  python: {{python_version}}
  device: {{cpu|cuda|rocm|mps}}
  notes: {{optional}}
---

# Template: How to {{Task Name}} with {{Service/Library Name}}

> Note: Replace placeholders (`{{...}}`) with real values. Keep this tutorial runnable and reproducible.

## Question

How do I {{perform a specific action / solve a specific problem}} using {{Service/Library Name}}?

## Prerequisites

This tutorial assumes prerequisites are already met; it does not walk through full setup.

- **Service status:** {{e.g., local service is running (if applicable)}}
- **Environment:** {{e.g., pixi/venv ready; how to run commands in this repo}}
- **Configuration:** {{e.g., required env vars / config files; no secrets in the doc}}
- **Data:** {{e.g., sample inputs available under `inputs/`}}

## Implementation Idea

Briefly describe the high-level flow.

- **Approach:**
  1. {{Initialize client / load model / import modules}}
  2. {{Construct input / request payload}}
  3. {{Execute call}}
  4. {{Parse output / write artifacts to `outputs/`}}

## Critical Example Code

Provide a clear, self-contained, copy/pasteable example. Use rich comments to explain each step.

### {{Primary Implementation}} (e.g., Python)

```python
import os

# 1) Configuration / initialization
# - Keep configuration explicit.
# - Do not embed secrets; read from env vars or config files.

def run_example() -> None:
    """
    Demonstrate how to {{task}} with {{Service/Library Name}}.
    """

    # 2) Prepare inputs
    # - Read from `inputs/` (prefer real files).
    # - If you must synthesize inputs, explain why and keep it minimal.

    # 3) Execute the call
    # - Show the exact API calls needed.
    # - Include basic error handling so users can diagnose failures.
    try:
        result = None  # replace with actual call
    except Exception as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc

    # 4) Process outputs
    # - Write outputs under `outputs/` so users can inspect artifacts.
    print(result)

if __name__ == "__main__":
    run_example()
```

### Optional equivalent (e.g., REST/cURL)

```bash
# Replace placeholders and keep the request copy/pasteable.
# Avoid printing secrets (use env vars).
curl -X POST "{{endpoint_url}}" \
  -H "Authorization: Bearer ${{API_KEY_ENV_VAR}}" \
  -H "Content-Type: application/json" \
  -d '{{json_payload}}'
```

## Input and Output

### Input

Describe the input contract and show a concrete example.

- {{param}} ({{type}}): {{description}}
- {{param}} ({{type}}): {{description}}

If the tutorial involves images:
- If ≤ 5 images: embed directly using `![alt](inputs/<file>)`.
- If > 5 images: list the image paths/descriptions instead.

### Output

Describe the output contract and show representative output (logs / JSON / file artifacts).

If the tutorial produces images:
- If ≤ 5 images: embed directly using `![alt](outputs/<file>)`.
- If > 5 images: list the output image paths instead.

```json
{{example_output_json}}
```

## Verification

- Run: `{{command_to_run_example}}`
- Confirm:
  - Expected output files exist under `outputs/`
  - Output matches the documented contract (shapes/counts/keys)

## Appendix

### Troubleshooting

- `ModuleNotFoundError: {{pkg}}`: {{how to add/install deps in this environment}}
- `{{common error}}`: {{likely cause and fix}}
- Device selection issues (GPU/CPU): {{how to force device selection}}

### Key parameters

| Name | Meaning | Value used by this tutorial |
|---|---|---|
| {{param_name}} | {{what it controls}} | {{value}} |

## References

- Docs: {{url}}
- Source: {{url}}
- Version pin (optional): {{tag_or_commit}}
