"""Custom input widgets for PeiDocker GUI with enhanced validation."""

import re
from pathlib import Path
from typing import Optional

from textual.validation import ValidationResult, Validator
from textual.widgets import Input


class DockerImageValidator(Validator):
    """Validator for Docker image names."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate Docker image name format."""
        if not value:
            return self.failure("Docker image name is required")
        
        # Basic Docker image name validation
        # Format: [registry/]namespace/repository[:tag]
        pattern = r'^([a-z0-9]+([._-][a-z0-9]+)*(/[a-z0-9]+([._-][a-z0-9]+)*)*(:[a-zA-Z0-9][a-zA-Z0-9._-]{0,127})?)?$'
        
        if not re.match(pattern, value.lower()):
            return self.failure("Invalid Docker image name format")
        
        return self.success()


class EnvironmentVariableValidator(Validator):
    """Validator for environment variables (KEY=VALUE format)."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate environment variable format."""
        if not value:
            return self.success()  # Optional field
        
        if '=' not in value:
            return self.failure("Format must be KEY=VALUE")
        
        key, _ = value.split('=', 1)
        key = key.strip()
        
        if not key:
            return self.failure("Environment variable key cannot be empty")
        
        # Key should start with letter or underscore, contain only alphanumeric and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
            return self.failure("Key must start with letter/underscore, contain only letters, numbers, underscores")
        
        return self.success()


class PortMappingValidator(Validator):
    """Validator for port mappings (host:container format)."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate port mapping format."""
        if not value:
            return self.success()  # Optional field
        
        if ':' not in value:
            return self.failure("Format must be host_port:container_port")
        
        try:
            host_part, container_part = value.split(':', 1)
            
            # Handle port ranges
            if '-' in host_part and '-' in container_part:
                host_start, host_end = map(int, host_part.split('-'))
                container_start, container_end = map(int, container_part.split('-'))
                
                if not (1 <= host_start <= host_end <= 65535):
                    return self.failure("Host port range must be 1-65535")
                if not (1 <= container_start <= container_end <= 65535):
                    return self.failure("Container port range must be 1-65535")
                if (host_end - host_start) != (container_end - container_start):
                    return self.failure("Host and container port ranges must have same size")
                
            elif '-' not in host_part and '-' not in container_part:
                host_port = int(host_part)
                container_port = int(container_part)
                
                if not (1 <= host_port <= 65535):
                    return self.failure("Host port must be 1-65535")
                if not (1 <= container_port <= 65535):
                    return self.failure("Container port must be 1-65535")
            else:
                return self.failure("Cannot mix port ranges with single ports")
                
            return self.success()
            
        except ValueError:
            return self.failure("Invalid port format - must be numbers")


class DockerImageInput(Input):
    """Specialized input for Docker image names with validation."""
    
    def __init__(self, **kwargs):
        super().__init__(
            placeholder="ubuntu:24.04",
            validators=[DockerImageValidator()],
            **kwargs
        )


class EnvironmentVariableInput(Input):
    """Specialized input for environment variables with KEY=VALUE validation."""
    
    def __init__(self, **kwargs):
        super().__init__(
            placeholder="NODE_ENV=production",
            validators=[EnvironmentVariableValidator()],
            **kwargs
        )


class PortMappingInput(Input):
    """Specialized input for port mappings with validation."""
    
    def __init__(self, **kwargs):
        super().__init__(
            placeholder="8080:80",
            validators=[PortMappingValidator()],
            **kwargs
        )


class PortNumberValidator(Validator):
    """Validator for port numbers (1-65535)."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate port number."""
        if not value.strip():
            return self.success()  # Empty is optional
        
        try:
            port = int(value.strip())
            if 1 <= port <= 65535:
                return self.success()
            else:
                return self.failure("Port must be between 1 and 65535")
        except ValueError:
            return self.failure("Must be a valid number")


class UserIDValidator(Validator):
    """Validator for user IDs (1100-65535 to avoid system conflicts)."""
    
    def validate(self, value: str) -> ValidationResult:
        """Validate user ID."""
        if not value.strip():
            return self.success()  # Empty is optional
        
        try:
            uid = int(value.strip())
            if 1100 <= uid <= 65535:
                return self.success()
            else:
                return self.failure("User ID must be between 1100 and 65535 (to avoid system conflicts)")
        except ValueError:
            return self.failure("Must be a valid number")


class PortNumberInput(Input):
    """Specialized input for port numbers (1-65535)."""
    
    def __init__(self, **kwargs):
        super().__init__(
            type="integer",
            placeholder="Port number",
            validators=[PortNumberValidator()],
            **kwargs
        )


class UserIDInput(Input):
    """Specialized input for user IDs (1100-65535 to avoid system conflicts)."""
    
    def __init__(self, **kwargs):
        super().__init__(
            type="integer",
            placeholder="User ID",
            validators=[UserIDValidator()],
            **kwargs
        )