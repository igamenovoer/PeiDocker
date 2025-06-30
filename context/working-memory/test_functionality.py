#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from pei_docker.pei_utils import substitute_env_vars

# Test basic functionality
test_str = "host_port: ${SSH_PORT:-2222}"
print('Test input:', test_str)
result = substitute_env_vars(test_str)
print('Without env var:', result)

# Test with environment variable set
os.environ['SSH_PORT'] = '3333'
result_with_env = substitute_env_vars(test_str)
print('With SSH_PORT=3333:', result_with_env)

# Test Windows path
test_path = "${DATA_PATH:-C:\\tmp\\default}"
print('\nTest path input:', test_path)
result_path = substitute_env_vars(test_path)
print('Without env var:', result_path)

os.environ['DATA_PATH'] = 'D:\\my-data'
result_path_with_env = substitute_env_vars(test_path)
print('With DATA_PATH=D:\\my-data:', result_path_with_env)

print('\n✅ Environment variable substitution is working!')
