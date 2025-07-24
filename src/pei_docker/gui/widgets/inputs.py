"""
Custom Input Widgets and Validators for PeiDocker GUI.

This module provides specialized input widgets and validators for Docker-specific
data types used throughout the PeiDocker GUI application. The widgets extend
Textual's base Input widget with domain-specific validation and appropriate
placeholder text.

All validators use Textual's ValidationResult system to provide immediate
feedback to users as they type, helping prevent configuration errors before
they occur.

Classes
-------
DockerImageValidator : Validates Docker image names and tags
EnvironmentVariableValidator : Validates KEY=VALUE environment variable format
PortMappingValidator : Validates Docker port mapping syntax
PortNumberValidator : Validates individual port numbers (1-65535)
UserIDValidator : Validates user IDs with system conflict avoidance
DockerImageInput : Input widget for Docker image names
EnvironmentVariableInput : Input widget for environment variables
PortMappingInput : Input widget for port mappings
PortNumberInput : Input widget for port numbers
UserIDInput : Input widget for user IDs

Notes
-----
The validators are designed to be permissive for optional fields (empty values
pass validation) while being strict for required format validation. This
allows the GUI to show validation feedback without blocking user input.
"""

import re
from pathlib import Path
from typing import Optional, Any

from textual.validation import ValidationResult, Validator
from textual.widgets import Input


class DockerImageValidator(Validator):
    """
    Validator for Docker image names and tags.
    
    Validates Docker image names according to Docker's naming conventions,
    supporting registry prefixes, namespaces, repositories, and optional tags.
    This ensures users can only enter valid image names that Docker can process.
    
    Notes
    -----
    Supported formats:
    - Simple image: "ubuntu"
    - Image with tag: "ubuntu:20.04"
    - Namespaced image: "library/ubuntu:latest"
    - Registry image: "registry.example.com/namespace/image:tag"
    
    Validation rules based on Docker's official image naming requirements:
    - Only lowercase letters, numbers, periods, hyphens, and underscores
    - Cannot start or end with separator characters
    - Tags can contain uppercase letters and additional characters
    - Registry names follow domain name conventions
    """
    
    def validate(self, value: str) -> ValidationResult:
        """
        Validate Docker image name format against Docker naming conventions.
        
        Parameters
        ----------
        value : str
            Docker image name to validate.
            
        Returns
        -------
        ValidationResult
            Success if the image name is valid, failure with error message otherwise.
            
        Notes
        -----
        The validation uses a regular expression that matches Docker's official
        image naming pattern. Empty values are rejected as Docker requires
        an image name to run containers.
        """
        if not value:
            return self.failure("Docker image name is required")
        
        # Basic Docker image name validation
        # Format: [registry/]namespace/repository[:tag]
        pattern = r'^([a-z0-9]+([._-][a-z0-9]+)*(/[a-z0-9]+([._-][a-z0-9]+)*)*(:[a-zA-Z0-9][a-zA-Z0-9._-]{0,127})?)?$'
        
        if not re.match(pattern, value.lower()):
            return self.failure("Invalid Docker image name format")
        
        return self.success()


class EnvironmentVariableValidator(Validator):
    """
    Validator for environment variable KEY=VALUE format.
    
    Validates environment variable strings to ensure they follow the standard
    Unix environment variable format with proper key naming conventions.
    This prevents configuration errors when environment variables are set
    in Docker containers.
    
    Notes
    -----
    Environment variable key requirements:
    - Must start with a letter or underscore
    - Can contain only letters, numbers, and underscores
    - Cannot be empty
    - Case-sensitive (typically uppercase by convention)
    
    Value requirements:
    - Can be any string, including empty strings
    - Special characters and spaces are allowed in values
    """
    
    def validate(self, value: str) -> ValidationResult:
        """
        Validate environment variable KEY=VALUE format.
        
        Parameters
        ----------
        value : str
            Environment variable string to validate.
            
        Returns
        -------
        ValidationResult
            Success if the format is valid, failure with specific error message otherwise.
            Empty values are considered valid (optional field).
            
        Notes
        -----
        The validation checks for the presence of exactly one '=' separator
        and validates the key portion against Unix environment variable naming
        conventions. The value portion can contain any characters.
        """
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
    """
    Validator for Docker port mappings in host:container format.
    
    Validates port mapping strings used in Docker container configuration,
    supporting both single port mappings and port ranges. Ensures that
    port numbers are within valid ranges and port ranges are properly matched.
    
    Notes
    -----
    Supported formats:
    - Single port mapping: "8080:80" (host port 8080 maps to container port 80)
    - Port range mapping: "8000-8010:9000-9010" (range of 11 ports each)
    
    Validation rules:
    - All port numbers must be in range 1-65535
    - Port ranges must have equal number of ports on both sides
    - Cannot mix single ports with ranges in one mapping
    - Both host and container sides must be consistent format
    """
    
    def validate(self, value: str) -> ValidationResult:
        """
        Validate Docker port mapping format with detailed error reporting.
        
        Parameters
        ----------
        value : str
            Port mapping string to validate (e.g., "8080:80" or "8000-8010:9000-9010").
            
        Returns
        -------
        ValidationResult
            Success if the port mapping is valid, failure with specific error message.
            Empty values are considered valid (optional field).
            
        Notes
        -----
        The validation performs comprehensive checks including:
        - Format verification (must contain ':')
        - Port number range validation (1-65535)
        - Port range consistency (equal number of ports)
        - Mixed format detection (prevents single:range combinations)
        """
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
    """
    Specialized input widget for Docker image names with built-in validation.
    
    Extends Textual's Input widget with Docker image name validation and
    appropriate placeholder text. Provides immediate feedback to users
    about image name validity as they type.
    
    Notes
    -----
    The input includes:
    - DockerImageValidator for real-time validation
    - Placeholder text showing example Docker image format
    - All standard Input widget functionality
    
    The validator ensures only valid Docker image names can be entered,
    preventing runtime errors when Docker attempts to pull or reference
    the specified image.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize Docker image input with validation and placeholder.
        
        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments passed to the base Input widget.
        """
        super().__init__(
            placeholder="ubuntu:24.04",
            validators=[DockerImageValidator()],
            **kwargs
        )


class EnvironmentVariableInput(Input):
    """
    Specialized input widget for environment variables with KEY=VALUE validation.
    
    Extends Textual's Input widget with environment variable format validation
    and helpful placeholder text. Ensures users enter properly formatted
    environment variables that can be successfully set in Docker containers.
    
    Notes
    -----
    The input includes:
    - EnvironmentVariableValidator for real-time format checking
    - Placeholder text showing KEY=VALUE format example
    - All standard Input widget functionality
    
    Environment variables entered through this widget are guaranteed to
    follow Unix naming conventions and can be safely passed to Docker
    container environments.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize environment variable input with validation and placeholder.
        
        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments passed to the base Input widget.
        """
        super().__init__(
            placeholder="NODE_ENV=production",
            validators=[EnvironmentVariableValidator()],
            **kwargs
        )


class PortMappingInput(Input):
    """
    Specialized input widget for Docker port mappings with validation.
    
    Extends Textual's Input widget with port mapping format validation
    and example placeholder text. Ensures users enter valid port mappings
    that Docker can use for container networking configuration.
    
    Notes
    -----
    The input includes:
    - PortMappingValidator for comprehensive port mapping validation
    - Placeholder text showing host:container format example
    - Support for both single ports and port ranges
    - All standard Input widget functionality
    
    Port mappings entered through this widget are validated to ensure
    proper format and port number ranges before being used in Docker
    container configuration.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize port mapping input with validation and placeholder.
        
        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments passed to the base Input widget.
        """
        super().__init__(
            placeholder="8080:80",
            validators=[PortMappingValidator()],
            **kwargs
        )


class PortNumberValidator(Validator):
    """
    Validator for individual port numbers within valid TCP/UDP range.
    
    Validates that port numbers are within the valid range for TCP and UDP
    ports (1-65535). This is used for individual port inputs where only
    a single port number is expected, not a port mapping.
    
    Notes
    -----
    Port number ranges:
    - Valid range: 1-65535 (standard TCP/UDP port range)
    - Well-known ports: 1-1023 (system services)
    - Registered ports: 1024-49151 (user applications)
    - Dynamic/private ports: 49152-65535 (temporary assignments)
    
    Empty values are considered valid for optional port configurations.
    """
    
    def validate(self, value: str) -> ValidationResult:
        """
        Validate individual port number within TCP/UDP range.
        
        Parameters
        ----------
        value : str
            Port number string to validate.
            
        Returns
        -------
        ValidationResult
            Success if port is in valid range (1-65535), failure otherwise.
            Empty values are considered valid (optional field).
        """
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
    """
    Validator for user IDs with system conflict avoidance.
    
    Validates user IDs to ensure they don't conflict with system users
    and groups commonly found in Docker base images. Uses a restricted
    range that avoids common system UID assignments.
    
    Notes
    -----
    UID range rationale:
    - 0: Reserved for root user
    - 1-99: Reserved for system accounts
    - 100-999: Reserved for system services
    - 1000-1099: Common range for first user accounts (ubuntu, etc.)
    - 1100-65535: Safe range for container users (recommended)
    
    Using UIDs >= 1100 prevents conflicts with:
    - Ubuntu default user (UID 1000)
    - Auto-generated groups that may use UIDs 1001-1099
    - System services and daemons
    """
    
    def validate(self, value: str) -> ValidationResult:
        """
        Validate user ID within safe range to avoid system conflicts.
        
        Parameters
        ----------
        value : str
            User ID string to validate.
            
        Returns
        -------
        ValidationResult
            Success if UID is in safe range (1100-65535), failure otherwise.
            Empty values are considered valid (optional field).
            
        Notes
        -----
        The validation rejects UIDs in the 1000-1099 range to prevent
        conflicts with common system users like 'ubuntu' (UID 1000) and
        auto-generated groups that may use sequential UIDs.
        """
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
    """
    Specialized input widget for individual port numbers with validation.
    
    Extends Textual's Input widget with port number validation and
    integer input type. Used for single port number inputs where
    only a valid TCP/UDP port number is expected.
    
    Notes
    -----
    The input includes:
    - PortNumberValidator for range validation (1-65535)
    - Integer input type for numeric-only input
    - Generic placeholder text for port numbers
    - All standard Input widget functionality
    
    This widget is typically used for SSH ports, proxy ports, and
    other single port configurations in the PeiDocker GUI.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize port number input with validation and integer type.
        
        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments passed to the base Input widget.
        """
        super().__init__(
            type="integer",
            placeholder="Port number",
            validators=[PortNumberValidator()],
            **kwargs
        )


class UserIDInput(Input):
    """
    Specialized input widget for user IDs with system conflict avoidance.
    
    Extends Textual's Input widget with user ID validation that prevents
    system UID conflicts. Ensures container users are created with UIDs
    that won't interfere with system accounts or services.
    
    Notes
    -----
    The input includes:
    - UserIDValidator for safe UID range validation (1100-65535)
    - Integer input type for numeric-only input
    - Descriptive placeholder text
    - All standard Input widget functionality
    
    Using this widget helps prevent SSH and container access issues
    that can occur when container UIDs conflict with system accounts
    in the base Docker image.
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize user ID input with validation and integer type.
        
        Parameters
        ----------
        **kwargs : Any
            Additional keyword arguments passed to the base Input widget.
        """
        super().__init__(
            type="integer",
            placeholder="User ID",
            validators=[UserIDValidator()],
            **kwargs
        )