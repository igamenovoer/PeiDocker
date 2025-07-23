# PeiDocker GUI Validation Testing Plan

## Overview

Validation tests focus on testing input validation, error handling, and edge cases across all GUI components. These tests ensure that the GUI handles invalid inputs gracefully and provides helpful feedback to users.

## Test Categories

### 1. Input Validation Tests
### 2. Form Validation Tests  
### 3. Configuration Validation Tests
### 4. Error Handling Tests
### 5. Edge Case Tests
### 6. User Feedback Tests

## Validation Test Structure Template

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.utils.file_utils import validate_port_mapping

@pytest.mark.validation
def test_input_validation_scenario():
    """Test specific input validation scenario."""
    # Test valid inputs
    assert validate_function("valid_input") == True
    
    # Test invalid inputs
    assert validate_function("invalid_input") == False
    
    # Test edge cases
    assert validate_function("") == False
    assert validate_function(None) == False
```

## Project Directory Validation Tests

### Test: `test_project_validation.py`

```python
import pytest
from unittest.mock import patch, Mock
from pathlib import Path
from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
from pei_docker.gui.models.config import ProjectConfig

class TestProjectDirectoryValidation:
    """Test suite for project directory validation."""
    
    @pytest.mark.validation
    def test_valid_project_directories(self):
        """Test validation of valid project directories."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        valid_paths = [
            "/home/user/projects/my-project",
            "C:\\Users\\User\\Projects\\MyProject",
            "/tmp/test-project",
            "./relative/project/path",
            "../another/relative/path",
            "/projects/with-dashes",
            "/projects/with_underscores",
            "/projects/with.dots",
        ]
        
        for path in valid_paths:
            with patch('pathlib.Path.exists', return_value=False):
                with patch('pathlib.Path.parent') as mock_parent:
                    mock_parent.exists.return_value = True
                    with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=True):
                        result = screen._validate_project_dir(path)
                        assert result == True, f"Path should be valid: {path}"
    
    @pytest.mark.validation
    def test_invalid_project_directories(self):
        """Test validation of invalid project directories."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        invalid_paths = [
            "",  # Empty string
            "   ",  # Whitespace only
            "/",  # Root directory
            "//",  # Double slash
            "con",  # Windows reserved name
            "aux",  # Windows reserved name
            "prn",  # Windows reserved name
            "/path/with/\x00null",  # Null character
            "/path/with/\ttab",  # Tab character
            "/path/with/\nnewline",  # Newline character
        ]
        
        for path in invalid_paths:
            result = screen._validate_project_dir(path)
            assert result == False, f"Path should be invalid: {path}"
    
    @pytest.mark.validation
    def test_project_directory_edge_cases(self):
        """Test edge cases for project directory validation."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        # Test very long path
        long_path = "/very/long/path/" + "a" * 250 + "/project"
        result = screen._validate_project_dir(long_path)
        # Result depends on OS limits, but should not crash
        assert isinstance(result, bool)
        
        # Test path with Unicode characters
        unicode_path = "/projects/测试项目/my-project"
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.parent') as mock_parent:
                mock_parent.exists.return_value = True
                with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=True):
                    result = screen._validate_project_dir(unicode_path)
                    assert isinstance(result, bool)
    
    @pytest.mark.validation
    def test_project_directory_permission_scenarios(self):
        """Test project directory validation with various permission scenarios."""
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        test_path = "/test/project/path"
        
        # Test: Directory exists and is writable
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=True):
                    result = screen._validate_project_dir(test_path)
                    assert result == True
        
        # Test: Directory exists but is not writable
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=False):
                    result = screen._validate_project_dir(test_path)
                    assert result == False
        
        # Test: Path exists but is a file, not directory
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=False):
                result = screen._validate_project_dir(test_path)
                assert result == False
        
        # Test: Directory doesn't exist, parent is writable
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.parent') as mock_parent:
                mock_parent.exists.return_value = True
                with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=True):
                    result = screen._validate_project_dir(test_path)
                    assert result == True
        
        # Test: Directory doesn't exist, parent not writable
        with patch('pathlib.Path.exists', return_value=False):
            with patch('pathlib.Path.parent') as mock_parent:
                mock_parent.exists.return_value = True
                with patch('pei_docker.gui.utils.file_utils.check_path_writable', return_value=False):
                    result = screen._validate_project_dir(test_path)
                    assert result == False

class TestProjectNameValidation:
    """Test suite for project name validation."""
    
    @pytest.mark.validation
    async def test_valid_project_names(self):
        """Test validation of valid project names."""
        from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen
        
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        valid_names = [
            "my-project",
            "my_project",
            "myproject",
            "project123",
            "test-app-v2",
            "web-server",
            "data-processor",
            "ml-model-trainer",
        ]
        
        for name in valid_names:
            result = screen._validate_project_name(name)
            assert result == True, f"Project name should be valid: {name}"
    
    @pytest.mark.validation
    async def test_invalid_project_names(self):
        """Test validation of invalid project names."""
        from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen
        
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        invalid_names = [
            "",  # Empty string
            "   ",  # Whitespace only
            "My Project",  # Spaces not allowed
            "my/project",  # Slashes not allowed
            "my\\project",  # Backslashes not allowed
            "my:project",  # Colons not allowed
            "my*project",  # Asterisks not allowed
            "my?project",  # Question marks not allowed
            "my|project",  # Pipes not allowed
            "my<project",  # Angle brackets not allowed
            "my>project",  # Angle brackets not allowed
            "my\"project",  # Quotes not allowed
            "CON",  # Windows reserved name
            "AUX",  # Windows reserved name
            "-startswith-dash",  # Cannot start with dash
            "endswith-",  # Cannot end with dash
            "_startswith_underscore",  # May be invalid for Docker
            "UPPERCASE",  # May cause issues
        ]
        
        for name in invalid_names:
            result = screen._validate_project_name(name)
            assert result == False, f"Project name should be invalid: {name}"
    
    @pytest.mark.validation
    async def test_project_name_edge_cases(self):
        """Test edge cases for project name validation."""
        from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen
        
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        # Test very long name
        long_name = "a" * 100
        result = screen._validate_project_name(long_name)
        # Should be invalid due to length
        assert result == False
        
        # Test name with only numbers
        number_name = "123456"
        result = screen._validate_project_name(number_name)
        # May be valid or invalid depending on implementation
        assert isinstance(result, bool)
        
        # Test single character name
        single_char = "a"
        result = screen._validate_project_name(single_char)
        assert isinstance(result, bool)
```

## SSH Configuration Validation Tests

### Test: `test_ssh_validation.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.screens.simple.ssh_config import SSHConfigScreen
from pei_docker.gui.models.config import ProjectConfig
from pei_docker.gui.utils.file_utils import validate_ssh_key

class TestSSHValidation:
    """Test suite for SSH configuration validation."""
    
    @pytest.mark.validation
    def test_valid_ssh_keys(self):
        """Test validation of valid SSH keys."""
        valid_keys = [
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7vbqajDjI... user@host",
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIL... user@host",
            "ssh-dss AAAAB3NzaC1kc3MAAACBAJ... user@host",
            "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHA... user@host",
            # Key without comment
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7vbqajDjI...",
            # Key with complex comment
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC7vbqajDjI... user@host.example.com",
        ]
        
        for key in valid_keys:
            result = validate_ssh_key(key)
            assert result == True, f"SSH key should be valid: {key[:50]}..."
    
    @pytest.mark.validation
    def test_invalid_ssh_keys(self):
        """Test validation of invalid SSH keys."""
        invalid_keys = [
            "",  # Empty string
            "   ",  # Whitespace only
            "invalid-key",  # No proper format
            "ssh-rsa",  # Missing key data
            "ssh-rsa INVALID_BASE64",  # Invalid base64
            "rsa-ssh AAAAB3NzaC1yc2EAAAADAQABAAABAQC7vbqajDjI...",  # Wrong prefix
            "ssh-invalid AAAAB3NzaC1yc2EAAAADAQABAAABAQC7vbqajDjI...",  # Invalid algorithm
            "-----BEGIN RSA PRIVATE KEY-----",  # Private key format
            "AAAAB3NzaC1yc2EAAAADAQABAAABAQC7vbqajDjI...",  # Missing ssh- prefix
        ]
        
        for key in invalid_keys:
            result = validate_ssh_key(key)
            assert result == False, f"SSH key should be invalid: {key[:50]}..."
    
    @pytest.mark.validation
    async def test_ssh_port_validation(self):
        """Test SSH port validation."""
        config = ProjectConfig()
        screen = SSHConfigScreen(config)
        
        # Valid ports
        valid_ports = [22, 2222, 8022, 10022, 65535]
        for port in valid_ports:
            result = screen._validate_port(port)
            assert result == True, f"Port should be valid: {port}"
        
        # Invalid ports
        invalid_ports = [0, -1, 65536, 100000, "abc", "", None]
        for port in invalid_ports:
            result = screen._validate_port(port)
            assert result == False, f"Port should be invalid: {port}"
    
    @pytest.mark.validation
    async def test_ssh_password_validation(self):
        """Test SSH password validation."""
        config = ProjectConfig()
        screen = SSHConfigScreen(config)
        
        # Valid passwords
        valid_passwords = [
            "simplepass",
            "Complex123!",
            "verylongpasswordwithmanychars",
            "pass123",
            "P@ssw0rd",
        ]
        
        for password in valid_passwords:
            result = screen._validate_password(password)
            assert result == True, f"Password should be valid: {password}"
        
        # Invalid passwords (according to implementation constraints)
        invalid_passwords = [
            "",  # Empty password
            "pass word",  # Contains space
            "pass,word",  # Contains comma
            "pass\tword",  # Contains tab
            "pass\nword",  # Contains newline
        ]
        
        for password in invalid_passwords:
            result = screen._validate_password(password)
            assert result == False, f"Password should be invalid: {password}"
    
    @pytest.mark.validation
    async def test_ssh_username_validation(self):
        """Test SSH username validation."""
        config = ProjectConfig()
        screen = SSHConfigScreen(config)
        
        # Valid usernames
        valid_usernames = [
            "user",
            "admin",
            "developer",
            "user123",
            "test-user",
            "test_user",
            "a",  # Single character
        ]
        
        for username in valid_usernames:
            result = screen._validate_username(username)
            assert result == True, f"Username should be valid: {username}"
        
        # Invalid usernames
        invalid_usernames = [
            "",  # Empty string
            "   ",  # Whitespace only
            "user name",  # Contains space
            "user/name",  # Contains slash
            "user\\name",  # Contains backslash
            "user:name",  # Contains colon
            "user@name",  # Contains @ symbol
            "123user",  # Starts with number (may be invalid)
            "-user",  # Starts with dash
            "user-",  # Ends with dash
            "ROOT",  # System user (uppercase)
            "root",  # System user
            "bin",  # System user
            "daemon",  # System user
        ]
        
        for username in invalid_usernames:
            result = screen._validate_username(username)
            assert result == False, f"Username should be invalid: {username}"
    
    @pytest.mark.validation
    async def test_ssh_uid_validation(self):
        """Test SSH UID validation."""
        config = ProjectConfig()
        screen = SSHConfigScreen(config)
        
        # Valid UIDs
        valid_uids = [1100, 1200, 2000, 5000, 65534]
        for uid in valid_uids:
            result = screen._validate_uid(uid)
            assert result == True, f"UID should be valid: {uid}"
        
        # Invalid UIDs
        invalid_uids = [
            -1,  # Negative
            0,   # Root UID (may be restricted)
            1,   # System UID
            999, # System UID range
            1000, # Common user UID (may conflict)
            1001, # May conflict with groups
            65536, # Too large
            "abc", # Non-numeric
            "", # Empty
            None, # None
        ]
        
        for uid in invalid_uids:
            result = screen._validate_uid(uid)
            assert result == False, f"UID should be invalid: {uid}"

class TestSSHKeyFileValidation:
    """Test suite for SSH key file validation."""
    
    @pytest.mark.validation
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    async def test_ssh_key_file_validation(self, mock_is_file, mock_exists):
        """Test SSH key file path validation."""
        from pei_docker.gui.screens.simple.ssh_config import SSHConfigScreen
        
        config = ProjectConfig()
        screen = SSHConfigScreen(config)
        
        # Test valid file path
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        result = screen._validate_key_file("/home/user/.ssh/id_rsa")
        assert result == True
        
        # Test file doesn't exist
        mock_exists.return_value = False
        result = screen._validate_key_file("/home/user/.ssh/nonexistent")
        assert result == False
        
        # Test path is directory, not file
        mock_exists.return_value = True
        mock_is_file.return_value = False
        result = screen._validate_key_file("/home/user/.ssh")
        assert result == False
    
    @pytest.mark.validation
    async def test_ssh_key_file_path_formats(self):
        """Test various SSH key file path formats."""
        from pei_docker.gui.screens.simple.ssh_config import SSHConfigScreen
        
        config = ProjectConfig()
        screen = SSHConfigScreen(config)
        
        # Test tilde expansion
        with patch('pathlib.Path.expanduser') as mock_expand:
            mock_expand.return_value = Path("/home/user/.ssh/id_rsa")
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_file', return_value=True):
                    result = screen._validate_key_file("~/.ssh/id_rsa")
                    assert result == True
                    mock_expand.assert_called()
        
        # Test absolute paths
        valid_paths = [
            "/home/user/.ssh/id_rsa",
            "/home/user/.ssh/id_ed25519",
            "/home/user/keys/mykey",
            "C:\\Users\\User\\.ssh\\id_rsa",  # Windows path
        ]
        
        for path in valid_paths:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_file', return_value=True):
                    result = screen._validate_key_file(path)
                    assert result == True, f"Key file path should be valid: {path}"
        
        # Test invalid paths
        invalid_paths = [
            "",  # Empty string
            "   ",  # Whitespace only
            "/nonexistent/key",  # Non-existent path
            "~/key with spaces",  # Spaces in path (may be problematic)
            "key",  # Relative path without directory
        ]
        
        for path in invalid_paths:
            if path.strip():  # Only test non-empty paths with file operations
                with patch('pathlib.Path.exists', return_value=False):
                    result = screen._validate_key_file(path)
                    assert result == False, f"Key file path should be invalid: {path}"
            else:
                result = screen._validate_key_file(path)
                assert result == False, f"Key file path should be invalid: {path}"
```

## Port Mapping Validation Tests

### Test: `test_port_validation.py`

```python
import pytest
from pei_docker.gui.utils.file_utils import validate_port_mapping

class TestPortValidation:
    """Test suite for port mapping validation."""
    
    @pytest.mark.validation
    def test_valid_single_port_mappings(self):
        """Test validation of valid single port mappings."""
        valid_mappings = [
            "80:80",
            "8080:80",
            "3000:3000",
            "22:22",
            "443:443",
            "65535:65535",
            "1:1",
            "1024:80",
            "8443:443",
        ]
        
        for mapping in valid_mappings:
            result = validate_port_mapping(mapping)
            assert result == True, f"Port mapping should be valid: {mapping}"
    
    @pytest.mark.validation
    def test_valid_port_range_mappings(self):
        """Test validation of valid port range mappings."""
        valid_ranges = [
            "100-200:300-400",
            "1000-1010:2000-2010",
            "8000-8100:9000-9100",
            "3000-3005:4000-4005",
            "10000-10999:20000-20999",
        ]
        
        for mapping in valid_ranges:
            result = validate_port_mapping(mapping)
            assert result == True, f"Port range should be valid: {mapping}"
    
    @pytest.mark.validation
    def test_invalid_port_mapping_formats(self):
        """Test validation of invalid port mapping formats."""
        invalid_formats = [
            "",  # Empty string
            "   ",  # Whitespace only
            "80",  # Missing container port
            ":80",  # Missing host port
            "80:",  # Missing container port after colon
            "80-90",  # Missing container ports
            "80:90:100",  # Too many colons
            "abc:def",  # Non-numeric ports
            "80:abc",  # Non-numeric container port
            "abc:80",  # Non-numeric host port
            "80 : 90",  # Spaces around colon
            "80- 90:100-110",  # Space in range
            "80-90 :100-110",  # Space before colon
            "80-90: 100-110",  # Space after colon
        ]
        
        for mapping in invalid_formats:
            result = validate_port_mapping(mapping)
            assert result == False, f"Port mapping should be invalid: {mapping}"
    
    @pytest.mark.validation
    def test_invalid_port_numbers(self):
        """Test validation of invalid port numbers."""
        invalid_ports = [
            "0:80",  # Port 0 invalid
            "80:0",  # Port 0 invalid
            "-1:80",  # Negative port
            "80:-1",  # Negative port
            "65536:80",  # Port too high
            "80:65536",  # Port too high
            "100000:80",  # Port way too high
            "80:100000",  # Port way too high
        ]
        
        for mapping in invalid_ports:
            result = validate_port_mapping(mapping)
            assert result == False, f"Port mapping should be invalid: {mapping}"
    
    @pytest.mark.validation
    def test_invalid_port_ranges(self):
        """Test validation of invalid port ranges."""
        invalid_ranges = [
            "200-100:300-400",  # Invalid range (start > end)
            "100-200:400-300",  # Invalid container range
            "100-100:300-400",  # Single port range (ambiguous)
            "100-200:300-300",  # Single port container range
            "100-200:300-350",  # Mismatched range sizes
            "100-105:300-400",  # Mismatched range sizes
            "0-100:200-300",    # Range includes invalid port 0
            "100-200:0-100",    # Range includes invalid port 0
            "65535-65540:1000-1005",  # Range exceeds max port
            "1000-1005:65535-65540",  # Range exceeds max port
        ]
        
        for mapping in invalid_ranges:
            result = validate_port_mapping(mapping)
            assert result == False, f"Port range should be invalid: {mapping}"
    
    @pytest.mark.validation
    def test_port_mapping_edge_cases(self):
        """Test edge cases for port mapping validation."""
        edge_cases = [
            "1:65535",  # Min to max
            "65535:1",  # Max to min
            "1023:1024",  # Privileged to non-privileged
            "1024:1023",  # Non-privileged to privileged
            "22:2222",   # SSH typical mapping
            "80:8080",   # HTTP typical mapping
            "443:8443",  # HTTPS typical mapping
        ]
        
        for mapping in edge_cases:
            result = validate_port_mapping(mapping)
            # These should generally be valid
            assert result == True, f"Port mapping should be valid: {mapping}"
```

## Environment Variable Validation Tests

### Test: `test_environment_validation.py`

```python
import pytest
from pei_docker.gui.utils.file_utils import validate_environment_var

class TestEnvironmentVariableValidation:
    """Test suite for environment variable validation."""
    
    @pytest.mark.validation
    def test_valid_environment_variables(self):
        """Test validation of valid environment variables."""
        valid_vars = [
            "KEY=value",
            "NODE_ENV=production",
            "DEBUG=true",
            "PATH=/usr/bin:/bin",
            "DATABASE_URL=postgres://user:pass@host:5432/db",
            "API_KEY=abc123def456",
            "PORT=3000",
            "TIMEOUT=30",
            "FEATURE_FLAG=enabled",
            "LOG_LEVEL=info",
            "HOME=/home/user",
            "LANG=en_US.UTF-8",
            "TZ=America/New_York",
            # Empty value (valid)
            "EMPTY_VAR=",
            # Value with spaces
            "MESSAGE=Hello World",
            # Value with special characters
            "COMPLEX=value-with_special.chars@123",
            # Numeric key
            "VAR123=value",
            # Mixed case
            "MyVar=MyValue",
        ]
        
        for var in valid_vars:
            result = validate_environment_var(var)
            assert result == True, f"Environment variable should be valid: {var}"
    
    @pytest.mark.validation
    def test_invalid_environment_variables(self):
        """Test validation of invalid environment variables."""
        invalid_vars = [
            "",  # Empty string
            "   ",  # Whitespace only
            "KEY",  # Missing equals sign
            "=value",  # Missing key
            "KEY=",  # Empty value (may be valid depending on implementation)
            "KEY WITH_SPACES=value",  # Spaces in key
            "KEY\tWITH_TAB=value",  # Tab in key
            "KEY\nWITH_NEWLINE=value",  # Newline in key
            "KEY=value=extra",  # Multiple equals signs (may be valid)
            "123=value",  # Key starts with number (may be invalid)
            "-KEY=value",  # Key starts with dash
            "KEY-=value",  # Key ends with dash
            ".KEY=value",  # Key starts with dot
            "KEY.=value",  # Key ends with dot
            # Special characters in key
            "KEY@HOST=value",  # @ in key
            "KEY#TAG=value",   # # in key
            "KEY$VAR=value",   # $ in key
            "KEY%VAR=value",   # % in key
            "KEY^VAR=value",   # ^ in key
            "KEY&VAR=value",   # & in key
            "KEY*VAR=value",   # * in key
            "KEY(VAR=value",   # ( in key
            "KEY)VAR=value",   # ) in key
            "KEY+VAR=value",   # + in key
            "KEY|VAR=value",   # | in key
            "KEY\\VAR=value",  # \ in key
            "KEY/VAR=value",   # / in key
            "KEY<VAR=value",   # < in key
            "KEY>VAR=value",   # > in key
            "KEY?VAR=value",   # ? in key
            "KEY[VAR=value",   # [ in key
            "KEY]VAR=value",   # ] in key
            "KEY{VAR=value",   # { in key
            "KEY}VAR=value",   # } in key
            "KEY\"VAR=value",  # " in key
            "KEY'VAR=value",   # ' in key
        ]
        
        for var in invalid_vars:
            result = validate_environment_var(var)
            assert result == False, f"Environment variable should be invalid: {var}"
    
    @pytest.mark.validation
    def test_environment_variable_edge_cases(self):
        """Test edge cases for environment variable validation."""
        edge_cases = [
            # Very long key
            ("A" * 100 + "=value", False),  # Too long
            # Very long value
            ("KEY=" + "A" * 1000, True),  # Long value should be OK
            # Unicode characters
            ("UNICODE_KEY=测试值", True),  # Unicode in value
            ("测试KEY=value", False),  # Unicode in key (may be invalid)
            # Case sensitivity
            ("key=value", True),  # Lowercase key
            ("KEY=value", True),  # Uppercase key
            ("Key=Value", True),  # Mixed case
            # Numbers
            ("KEY123=456", True),  # Numbers in key and value
            ("123KEY=value", False),  # Key starts with number
            # Underscores and dashes
            ("KEY_NAME=value", True),  # Underscore in key
            ("KEY_123=value", True),  # Underscore and number
            ("KEY-NAME=value", False),  # Dash in key (may be invalid)
        ]
        
        for var, expected in edge_cases:
            result = validate_environment_var(var)
            assert result == expected, f"Environment variable '{var}' should be {expected}"
```

## Docker Image Validation Tests

### Test: `test_docker_image_validation.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen
from pei_docker.gui.models.config import ProjectConfig

class TestDockerImageValidation:
    """Test suite for Docker image validation."""
    
    @pytest.mark.validation
    async def test_valid_docker_image_names(self):
        """Test validation of valid Docker image names."""
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        valid_images = [
            "ubuntu",
            "ubuntu:24.04",
            "ubuntu:latest",
            "python:3.11",
            "python:3.11-slim",
            "nginx:1.21-alpine",
            "node:18-bullseye",
            "postgres:15.2",
            "redis:7-alpine",
            "mysql:8.0",
            "elasticsearch:8.7.0",
            "registry.hub.docker.com/library/ubuntu:22.04",
            "docker.io/library/python:3.11",
            "quay.io/prometheus/prometheus:latest",
            "gcr.io/google-containers/busybox:latest",
            "nvidia/cuda:12.1-cudnn8-devel-ubuntu22.04",
            "jupyter/scipy-notebook:latest",
            "tensorflow/tensorflow:2.13.0-gpu",
            "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime",
        ]
        
        for image in valid_images:
            result = screen._validate_image_format(image)
            assert result == True, f"Docker image should be valid: {image}"
    
    @pytest.mark.validation
    async def test_invalid_docker_image_names(self):
        """Test validation of invalid Docker image names."""
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        invalid_images = [
            "",  # Empty string
            "   ",  # Whitespace only
            "UPPERCASE",  # Uppercase not allowed
            "image:TAG",  # Uppercase tag
            "my image",  # Spaces not allowed
            "my/image name",  # Spaces in name
            "image:",  # Empty tag
            ":tag",  # Empty image name
            "image::tag",  # Double colon
            "image:tag:extra",  # Multiple colons
            "image@sha256",  # Missing digest
            "image@",  # Empty digest
            "-image",  # Starting with dash
            "image-",  # Ending with dash
            ".image",  # Starting with dot
            "image.",  # Ending with dot
            "_image",  # Starting with underscore
            "image_",  # Ending with underscore
            "registry/",  # Trailing slash
            "/image",  # Leading slash
            "registry//image",  # Double slash
            "image/",  # Trailing slash in name
            "image:v1.0.0-",  # Tag ending with dash
            "image:v1.0.0.",  # Tag ending with dot
            "image:-tag",  # Tag starting with dash
            "image:.tag",  # Tag starting with dot
            # Special characters
            "image:tag@",  # @ in tag
            "image:tag#",  # # in tag
            "image:tag$",  # $ in tag
            "image:tag%",  # % in tag
            "image:tag^",  # ^ in tag
            "image:tag&",  # & in tag
            "image:tag*",  # * in tag
            "image:tag+",  # + in tag
            "image:tag|",  # | in tag
            "image:tag\\",  # \ in tag
            "image:tag<",  # < in tag
            "image:tag>",  # > in tag
            "image:tag?",  # ? in tag
            "image:tag[",  # [ in tag
            "image:tag]",  # ] in tag
            "image:tag{",  # { in tag
            "image:tag}",  # } in tag
            "image:tag\"",  # " in tag
            "image:tag'",  # ' in tag
        ]
        
        for image in invalid_images:
            result = screen._validate_image_format(image)
            assert result == False, f"Docker image should be invalid: {image}"
    
    @pytest.mark.validation
    @patch('subprocess.run')
    async def test_docker_image_existence_check(self, mock_run):
        """Test Docker image existence checking."""
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        # Mock image exists
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"Id": "sha256:abc123"}'
        mock_run.return_value = mock_result
        
        result = screen._validate_docker_image("ubuntu:24.04")
        assert result == True
        
        # Verify Docker command was called
        mock_run.assert_called_with(
            ["docker", "image", "inspect", "ubuntu:24.04"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Mock image doesn't exist
        mock_result.returncode = 1
        mock_result.stderr = "Error: No such image"
        mock_run.return_value = mock_result
        
        result = screen._validate_docker_image("nonexistent:tag")
        assert result == False
    
    @pytest.mark.validation
    @patch('subprocess.run')
    async def test_docker_image_validation_timeout(self, mock_run):
        """Test Docker image validation with timeout."""
        import subprocess
        
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(
            ["docker", "image", "inspect", "slow:image"], 30
        )
        
        result = screen._validate_docker_image("slow:image")
        assert result == False
    
    @pytest.mark.validation
    @patch('subprocess.run')
    async def test_docker_unavailable_during_validation(self, mock_run):
        """Test image validation when Docker is unavailable."""
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        # Mock Docker command not found
        mock_run.side_effect = FileNotFoundError()
        
        result = screen._validate_docker_image("ubuntu:24.04")
        # Should handle gracefully (may return False or True depending on implementation)
        assert isinstance(result, bool)
```

## Error Handling and User Feedback Tests

### Test: `test_error_handling.py`

```python
import pytest
from unittest.mock import patch, Mock
from pei_docker.gui.screens.simple.summary import SummaryScreen
from pei_docker.gui.models.config import ProjectConfig

class TestErrorHandling:
    """Test suite for error handling and user feedback."""
    
    @pytest.mark.validation
    async def test_configuration_save_error_handling(self):
        """Test error handling during configuration save."""
        config = ProjectConfig(
            project_name="test-project",
            project_dir="/invalid/path"
        )
        
        screen = SummaryScreen(config)
        mock_app = Mock()
        screen.app = mock_app
        
        # Mock file write error
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = screen._save_configuration()
            
            assert result == False
            # Should show error notification
            mock_app.notify.assert_called_with(
                "Failed to save configuration", 
                severity="error"
            )
    
    @pytest.mark.validation
    async def test_project_creation_error_handling(self):
        """Test error handling during project creation."""
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        
        config = ProjectConfig()
        config.project_dir = "/restricted/path"
        screen = ModeSelectionScreen(config)
        
        # Mock permission error during project creation
        with patch('os.path.exists', side_effect=PermissionError("Access denied")):
            result = screen._create_project()
            
            assert result == False
            # Should log error (check if logging is implemented)
    
    @pytest.mark.validation
    async def test_input_validation_feedback(self):
        """Test user feedback for input validation errors."""
        from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen
        
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        # Mock the app for notifications
        mock_app = Mock()
        screen.app = mock_app
        
        # Test invalid project name
        screen._validate_and_notify_project_name("")
        
        # Should provide helpful error message
        # (Implementation specific - check for appropriate notification)
    
    @pytest.mark.validation
    async def test_docker_connection_error_handling(self):
        """Test handling of Docker connection errors."""
        from pei_docker.gui.screens.startup import StartupScreen
        
        config = ProjectConfig()
        screen = StartupScreen(config)
        
        mock_app = Mock()
        screen.app = mock_app
        
        # Mock Docker connection error
        with patch('pei_docker.gui.utils.docker_utils.check_docker_available') as mock_check:
            mock_check.side_effect = Exception("Connection failed")
            
            await screen.on_mount()
            
            # Should handle error gracefully
            assert screen.docker_available == False
            # Should not crash the application
    
    @pytest.mark.validation
    async def test_file_system_error_recovery(self):
        """Test recovery from file system errors."""
        from pei_docker.gui.screens.mode_selection import ModeSelectionScreen
        
        config = ProjectConfig()
        screen = ModeSelectionScreen(config)
        
        # Test path validation with file system error
        with patch('pathlib.Path.exists', side_effect=OSError("File system error")):
            result = screen._validate_project_dir("/test/path")
            
            # Should return False and not crash
            assert result == False
    
    @pytest.mark.validation
    async def test_validation_error_accumulation(self):
        """Test accumulation and display of multiple validation errors."""
        from pei_docker.gui.screens.simple.ssh_config import SSHConfigScreen
        
        config = ProjectConfig()
        screen = SSHConfigScreen(config)
        
        mock_app = Mock()
        screen.app = mock_app
        
        # Set multiple invalid values
        screen.ssh_port = 0  # Invalid port
        screen.ssh_user = ""  # Empty username
        screen.ssh_password = "pass word"  # Invalid password (contains space)
        
        # Validate form
        is_valid = screen.is_valid()
        
        assert is_valid == False
        # Should collect and display all validation errors
        # (Implementation specific - check for error collection mechanism)
    
    @pytest.mark.validation
    async def test_graceful_degradation(self):
        """Test graceful degradation when features are unavailable."""
        from pei_docker.gui.screens.simple.project_info import ProjectInfoScreen
        
        config = ProjectConfig()
        screen = ProjectInfoScreen(config)
        
        # Mock Docker unavailable
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            # Should still allow form submission without Docker validation
            result = screen._validate_docker_image("ubuntu:24.04")
            
            # Should gracefully handle Docker unavailability
            # May return True (skip validation) or False (require user awareness)
            assert isinstance(result, bool)
    
    @pytest.mark.validation
    async def test_user_notification_system(self):
        """Test user notification system for various scenarios."""
        from pei_docker.gui.screens.simple.summary import SummaryScreen
        
        config = ProjectConfig(
            project_name="test-project",
            project_dir="/test/path"
        )
        
        screen = SummaryScreen(config)
        mock_app = Mock()
        screen.app = mock_app
        
        # Test success notification
        with patch('builtins.open', Mock()):
            with patch('yaml.dump', Mock()):
                result = screen._save_configuration()
                
                if result:
                    # Should show success notification
                    mock_app.notify.assert_called()
                    
                    # Check notification content
                    call_args = mock_app.notify.call_args
                    assert "saved" in call_args[0][0].lower() or "success" in call_args[0][0].lower()
```

This comprehensive validation testing plan ensures that all input validation, error handling, and user feedback mechanisms in the PeiDocker GUI are thoroughly tested and provide a robust user experience.