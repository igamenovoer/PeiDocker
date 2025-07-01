#!/usr/bin/env python3
"""
Test script for SSH key enhancement features.
This script tests the new SSH key functionality by processing a test configuration.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import omegaconf as oc
from pei_docker.config_processor import PeiConfigProcessor
from pei_docker.user_config import SSHUserConfig
from pei_docker.pei_utils import process_config_env_substitution

def test_ssh_user_config_validation():
    """Test SSHUserConfig validation logic"""
    print("Testing SSHUserConfig validation...")
    
    # Test 1: Valid configuration with password
    try:
        config = SSHUserConfig(password="test123", uid=1000)
        print("✓ Valid password configuration accepted")
    except Exception as e:
        print(f"✗ Password configuration failed: {e}")
        return False
    
    # Test 2: Valid configuration with pubkey_text
    try:
        config = SSHUserConfig(
            pubkey_text="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDFFy2DpsaaLcixgYgT8+7GxVR5mRGOx7urSe4rKjZ5G user@host",
            uid=1000
        )
        print("✓ Valid pubkey_text configuration accepted")
    except Exception as e:
        print(f"✗ Pubkey_text configuration failed: {e}")
        return False
    
    # Test 3: Valid configuration with privkey_text
    try:
        config = SSHUserConfig(
            privkey_text="""-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABCLeSpkKu
zfp8gLIO/O6v0GAAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIFPW+lmS7RfUgmm/
zHEwJ1qrxX//PVZ1IRBx9kgrr11+AAAAoE33cdhrQMyeBuE2jpkJE0NdiGdK80qW2cJjUc
/5JfZSvRIF0CRD6qDt2/aOig6KQVb60ky5pAaO2nymIzTZZaVE44+LNJ46f56vqnBDQrFO
/uLpyhpHFluGcphOt8myrp0F4kBJj2KObJubJLAcd4aVbWgNZ4kM+KfYnEiSG88d5JR136
ZkKSpbazcnFf58IrZOPghEQPoFUeVRvnlKWPE=
-----END OPENSSH PRIVATE KEY-----""",
            uid=1000
        )
        print("✓ Valid privkey_text configuration accepted")
    except Exception as e:
        print(f"✗ Privkey_text configuration failed: {e}")
        return False
    
    # Test 4: Invalid - conflicting pubkey options
    try:
        config = SSHUserConfig(
            pubkey_file="key.pub",
            pubkey_text="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDFFy2DpsaaLcixgYgT8+7GxVR5mRGOx7urSe4rKjZ5G user@host",
            uid=1000
        )
        print("✗ Conflicting pubkey options should have been rejected")
        return False
    except ValueError as e:
        print(f"✓ Conflicting pubkey options correctly rejected: {e}")
    
    # Test 5: Invalid - conflicting privkey options
    try:
        config = SSHUserConfig(
            privkey_file="key",
            privkey_text="-----BEGIN OPENSSH PRIVATE KEY-----...",
            uid=1000
        )
        print("✗ Conflicting privkey options should have been rejected")
        return False
    except ValueError as e:
        print(f"✓ Conflicting privkey options correctly rejected: {e}")
    
    # Test 6: Invalid - no authentication method
    try:
        config = SSHUserConfig(uid=1000)
        print("✗ No authentication method should have been rejected")
        return False
    except ValueError as e:
        print(f"✓ No authentication method correctly rejected: {e}")
    
    return True

def test_configuration_processing():
    """Test configuration processing with test data"""
    print("\nTesting configuration processing...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Load test configuration
        test_config_path = project_root / "context" / "working-memory" / "test-ssh-keys-config.yml"
        if not test_config_path.exists():
            print(f"✗ Test config file not found: {test_config_path}")
            return False
        
        try:
            # Load configurations
            user_config = oc.OmegaConf.load(test_config_path)
            if not isinstance(user_config, oc.DictConfig):
                print("✗ User config must be a dictionary")
                return False
                
            user_config = process_config_env_substitution(user_config)
            
            template_path = project_root / "pei_docker" / "templates" / "base-image-gen.yml"
            compose_template = oc.OmegaConf.load(template_path)
            if not isinstance(compose_template, oc.DictConfig):
                print("✗ Compose template must be a dictionary")
                return False
            
            # Create processor
            processor = PeiConfigProcessor.from_config(user_config, compose_template, temp_dir)
            
            # Process configuration (keep extra sections for testing)
            result = processor.process(remove_extra=False)
            
            print("✓ Configuration processed successfully")
            
            # Check if SSH key files were created
            ssh_keys_dir = Path(temp_dir) / "installation" / "stage-1" / "generated"
            if ssh_keys_dir.exists():
                key_files = list(ssh_keys_dir.glob("temp-*"))
                print(f"✓ Created {len(key_files)} SSH key files:")
                for key_file in key_files:
                    print(f"  - {key_file.name}")
                    
                # Verify key file contents
                for key_file in key_files:
                    if key_file.stat().st_size > 0:
                        print(f"  ✓ {key_file.name} has content ({key_file.stat().st_size} bytes)")
                    else:
                        print(f"  ✗ {key_file.name} is empty")
                        return False
            else:
                print("✗ SSH keys directory was not created")
                return False
            
            # Verify that the compose configuration includes our SSH settings
            ssh_config = result.get('x-cfg-stage-1', {}).get('build', {}).get('ssh', {})
            if ssh_config:
                print("✓ SSH configuration found in output")
                print(f"  - Users: {ssh_config.get('username', 'none')}")
                print(f"  - Public keys: {ssh_config.get('pubkey_file', 'none')}")
                print(f"  - Private keys: {ssh_config.get('privkey_file', 'none')}")
            else:
                print("✗ SSH configuration not found in output")
                print("Available keys in result:")
                for key in result.keys():
                    print(f"  - {key}")
                if 'x-cfg-stage-1' in result:
                    stage_config = result['x-cfg-stage-1']
                    print("Keys in x-cfg-stage-1:")
                    for key in stage_config.keys():
                        print(f"    - {key}")
                    if 'build' in stage_config:
                        build_config = stage_config['build']
                        print("Keys in x-cfg-stage-1.build:")
                        for key in build_config.keys():
                            print(f"      - {key}")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Configuration processing failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run all tests"""
    print("SSH Key Enhancement Feature Tests")
    print("=" * 50)
    
    success = True
    
    # Test validation
    if not test_ssh_user_config_validation():
        success = False
    
    # Test configuration processing
    if not test_configuration_processing():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
