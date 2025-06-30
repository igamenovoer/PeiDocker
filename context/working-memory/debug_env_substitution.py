#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

import omegaconf as oc
from pei_docker.pei_utils import process_config_env_substitution

# Set environment variables
os.environ['PROJECT_NAME'] = 'debug-test-app'
os.environ['SSH_PORT'] = '4444'
os.environ['APT_MIRROR'] = 'ustc'

# Load and process the config
config_path = "test-integration/user_config.yml"
print(f"Loading config from: {config_path}")

in_config = oc.OmegaConf.load(config_path)
print("Original config:")
print(oc.OmegaConf.to_yaml(in_config))

print("\nProcessing environment variable substitution...")
processed_config = process_config_env_substitution(in_config)
print("Processed config:")
print(oc.OmegaConf.to_yaml(processed_config))

# Check specific values
print(f"\nSpecific values:")
print(f"Base image: {processed_config.stage_1.image.base}")
print(f"Output image: {processed_config.stage_1.image.output}")
print(f"SSH port: {processed_config.stage_1.ssh.host_port}")
print(f"APT source: {processed_config.stage_1.apt.repo_source}")
