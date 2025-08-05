# Refactor Plan: Data Model Duplication Reduction

## What to Refactor

The PeiDocker project currently has duplicate data model implementations:

1. **peidocker-data-model** (`src/pei_docker/user_config.py`) - Uses `attrs` library with comprehensive validation
2. **business-data-model** (`src/pei_docker/webgui/models/config.py`) - Uses `pydantic` library with similar structure

Both models represent the same `user_config.yml` file structure but with different validation libraries and slightly different field names and structures. This duplication leads to:
- Maintenance overhead when updating schema
- Potential inconsistencies between CLI and GUI representations
- Redundant validation logic
- Complex bridging code to convert between models

## Why Refactor

1. **Reduce Code Duplication**: Having two separate implementations of the same data model violates DRY principles
2. **Improve Maintainability**: Changes to the configuration schema currently require updates in multiple places
3. **Ensure Consistency**: A single source of truth for the data model prevents divergence between CLI and GUI
4. **Simplify Architecture**: Remove the need for complex conversion logic between two nearly identical models
5. **Type Safety**: Leverage the existing comprehensive validation from the attrs-based model

## How to Refactor

### Phase 1: Analysis and Compatibility Layer
1. **Create a compatibility adapter** that allows pydantic-expecting code to work with attrs models
2. **Map field differences** between the two implementations (e.g., `enable` vs `enabled` in SSHConfig)
3. **Test the adapter** with existing GUI code to ensure no regressions

### Phase 2: Create Unified Model Interface
1. **Define a Protocol/Interface** that both attrs and pydantic models can implement
2. **Create wrapper classes** that adapt attrs models to work where pydantic models are expected
3. **Implement validation delegation** from pydantic wrappers to attrs validators

### Phase 3: Gradual Migration
1. **Replace pydantic models** in `config.py` with wrapper classes around attrs models
2. **Update UIStateBridge** to work directly with attrs models
3. **Maintain backward compatibility** during the transition

### Phase 4: Cleanup
1. **Remove duplicate pydantic models** once all code is migrated
2. **Simplify bridge layer** to only handle UI state ↔ attrs model conversion
3. **Update documentation** to reflect the unified model approach

## Expected Outcome

After refactoring:
1. **Single source of truth**: Only `user_config.py` defines the configuration schema
2. **Reduced code**: Eliminate ~300 lines of duplicate model definitions
3. **Simplified architecture**: Direct conversion between UI state and attrs models
4. **Better maintainability**: Schema changes only need to be made in one place
5. **Consistent validation**: Both CLI and GUI use the same validation logic
6. **Type safety maintained**: Full type hints and validation throughout

## Example Code

### Before Refactoring

```python
# In webgui/models/config.py (Duplicate model)
class SSHConfig(BaseModel):
    """Pydantic model for SSH validation"""
    enabled: bool = False
    port: int = Field(default=22, ge=1, le=65535)
    host_port: int = Field(default=2222, ge=1, le=65535)
    users: List[Dict[str, Any]] = Field(default_factory=list)
    
    @field_validator('users')
    @classmethod
    def validate_users(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Duplicate validation logic
        ...

# In user_config.py (Original model)
@define(kw_only=True)
class SSHConfig:
    """SSH server configuration for Docker container access."""
    enable: bool = field(default=True)  # Note: different field name!
    port: int = field(default=22)
    host_port: int | None = field(default=None)
    users: dict[str, SSHUserConfig] = field(factory=dict)
```

### After Refactoring

```python
# In webgui/models/config_adapter.py (New adapter)
from pei_docker.user_config import SSHConfig as AttrsSSHConfig
from typing import Protocol, runtime_checkable

@runtime_checkable
class SSHConfigProtocol(Protocol):
    """Protocol defining SSH configuration interface"""
    @property
    def enabled(self) -> bool: ...
    @property
    def port(self) -> int: ...
    @property
    def host_port(self) -> int: ...
    @property
    def users(self) -> List[Dict[str, Any]]: ...

class SSHConfigAdapter:
    """Adapter to make attrs SSHConfig work with pydantic-expecting code"""
    def __init__(self, attrs_config: AttrsSSHConfig):
        self._config = attrs_config
    
    @property
    def enabled(self) -> bool:
        return self._config.enable  # Map field name difference
    
    @property
    def port(self) -> int:
        return self._config.port
    
    @property
    def host_port(self) -> int:
        return self._config.host_port or 2222  # Handle None with default
    
    @property
    def users(self) -> List[Dict[str, Any]]:
        # Convert dict[str, SSHUserConfig] to List[Dict[str, Any]]
        return [
            {
                'name': username,
                'password': user.password,
                'uid': user.uid,
                'ssh_keys': self._extract_ssh_keys(user)
            }
            for username, user in self._config.users.items()
        ]
    
    def validate(self):
        # Validation is already done by attrs
        return True

# In webgui/models/config.py (Updated to use adapter)
from pei_docker.webgui.models.config_adapter import SSHConfigAdapter
from pei_docker.user_config import SSHConfig as AttrsSSHConfig

# Replace the duplicate pydantic model with adapter usage
def create_ssh_config(data: dict) -> SSHConfigAdapter:
    """Create SSH config from dictionary data"""
    attrs_config = AttrsSSHConfig(**data)
    return SSHConfigAdapter(attrs_config)
```

## References

- PeiDocker Data Model Implementation: `src/pei_docker/user_config.py`
- WebGUI Business Model (to be refactored): `src/pei_docker/webgui/models/config.py`
- UI State Bridge: `src/pei_docker/webgui/utils/ui_state_bridge.py`
- Project Terminology: `context/tasks/prefix/prefix-terminology.md`
- attrs Library Documentation: `/python-attrs/attrs`
- Pydantic Library Documentation: `/pydantic/pydantic`