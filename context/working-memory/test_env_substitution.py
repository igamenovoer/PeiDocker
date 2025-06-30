#!/usr/bin/env python3
"""
Test script for environment variable substitution in PeiDocker
"""

import os
import sys
import tempfile
import yaml

# Add the pei_docker module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pei_docker.pei_utils import substitute_env_vars, process_config_env_substitution
import omegaconf as oc

def test_env_substitution():
    """Test environment variable substitution functionality"""
    
    print("Testing environment variable substitution...")
    
    # Set up test environment variables
    os.environ['TEST_HOST_PATH'] = '/test/host/path'
    os.environ['TEST_PORT'] = '8080'
    
    # Test cases
    test_cases = [
        # (input, expected_output, description)
        ('${TEST_HOST_PATH}', '/test/host/path', 'Simple variable substitution'),
        ('${UNDEFINED_VAR:-/default/path}', '/default/path', 'Fallback for undefined variable'),
        ('${TEST_HOST_PATH:-/fallback}', '/test/host/path', 'Defined variable with fallback (should use defined)'),
        ('prefix-${TEST_PORT}-suffix', 'prefix-8080-suffix', 'Variable within string'),
        ('${SHARED_HOST_PATH:-/mnt/d/docker-space/workspace/minimal-gpu}', 
         '/mnt/d/docker-space/workspace/minimal-gpu', 'Real-world example'),
        ('normal/path/without/vars', 'normal/path/without/vars', 'String without variables'),
    ]
    
    for input_str, expected, description in test_cases:
        result = substitute_env_vars(input_str)
        status = "✓" if result == expected else "✗"
        print(f"{status} {description}")
        print(f"   Input:    {input_str}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}")
        print()

def test_config_processing():
    """Test environment variable substitution in configuration objects"""
    
    print("Testing configuration processing...")
    
    # Set up test environment
    os.environ['SHARED_HOST_PATH'] = '/custom/shared/path'
    os.environ['SSH_PORT'] = '3333'
    
    # Create test configuration
    test_config_yaml = """
stage_2:
  mount:
    shared_host:
      type: host
      host_path: "${SHARED_HOST_PATH:-/mnt/d/docker-space/workspace/minimal-gpu}"
    another_mount:
      type: host
      host_path: "${UNDEFINED_PATH:-/default/mount/path}"
  ssh:
    host_port: "${SSH_PORT:-2222}"
    port: 22
  environment:
    - "CUSTOM_VAR=${CUSTOM_VAR:-default_value}"
    - "ANOTHER_VAR=static_value"
"""
    
    # Parse with OmegaConf
    config = oc.OmegaConf.create(yaml.safe_load(test_config_yaml))
    
    print("Original config:")
    print(oc.OmegaConf.to_yaml(config))
    
    # Process environment substitution
    processed_config = process_config_env_substitution(config)
    
    print("Processed config:")
    print(oc.OmegaConf.to_yaml(processed_config))
    
    # Verify results
    expected_shared_path = "/custom/shared/path"  # From environment
    expected_undefined_path = "/default/mount/path"  # From fallback
    expected_ssh_port = "3333"  # From environment
    
    actual_shared_path = processed_config.stage_2.mount.shared_host.host_path
    actual_undefined_path = processed_config.stage_2.mount.another_mount.host_path
    actual_ssh_port = processed_config.stage_2.ssh.host_port
    
    print(f"✓ shared_host.host_path: {actual_shared_path} == {expected_shared_path}")
    print(f"✓ another_mount.host_path: {actual_undefined_path} == {expected_undefined_path}")
    print(f"✓ ssh.host_port: {actual_ssh_port} == {expected_ssh_port}")

if __name__ == '__main__':
    test_env_substitution()
    print("=" * 50)
    test_config_processing()
    print("\nAll tests completed!")
