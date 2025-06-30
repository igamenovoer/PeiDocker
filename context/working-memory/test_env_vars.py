#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from pei_docker.pei_utils import substitute_env_vars

# Test configuration with environment variables
test_config = """stage_1:
  image:
    base: ubuntu:24.04
    output: test-env-vars:stage-1
  ssh:
    enable: true
    port: 22
    host_port: "${SSH_HOST_PORT:-2222}"
    users:
      me:
        password: '123456'
stage_2:
  image:
    output: test-env-vars:stage-2
  mount:
    shared_host:
      type: host
      host_path: "${SHARED_HOST_PATH:-C:\\tmp\\default-shared}"
      dst_path: "/shared"
"""

print('=== Testing without environment variables ===')
expanded = substitute_env_vars(test_config)
print(expanded)

print('\n=== Testing with environment variables set ===')
os.environ['SSH_HOST_PORT'] = '3333'
os.environ['SHARED_HOST_PATH'] = 'D:\\my-custom-path'

expanded_with_env = substitute_env_vars(test_config)
print(expanded_with_env)

# Clean up
if 'SSH_HOST_PORT' in os.environ:
    del os.environ['SSH_HOST_PORT']
if 'SHARED_HOST_PATH' in os.environ:
    del os.environ['SHARED_HOST_PATH']
