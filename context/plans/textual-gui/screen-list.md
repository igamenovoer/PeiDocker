# PeiDocker GUI Screen List

## Screen Overview

| Screen | Index | Name | Major Functionality |
|--------|-------|------|-------------------|
| SC-0 | 0 | Application Startup | System validation, Docker availability check |
| SC-1 | 1 | Project Directory Selection | Project location setup and validation |
| SC-2 | 2 | Wizard Controller | Controller framework for configuration wizard (not user-facing) |
| SC-3 | 3 | Project Information (Step 1) | Project name and base Docker image selection |
| SC-4 | 4 | SSH Configuration (Step 2) | SSH access setup with ports, users, and authentication |
| SC-5 | 5 | Proxy Configuration (Step 3) | HTTP proxy settings for container networking |
| SC-6 | 6 | APT Configuration (Step 4) | APT repository mirror selection |
| SC-7 | 7 | Port Mapping (Step 5) | Additional host-to-container port mappings |
| SC-8 | 8 | Environment Variables (Step 6) | Custom environment variable configuration |
| SC-9 | 9 | Device Configuration (Step 7) | GPU and hardware device access setup |
| SC-10 | 10 | Additional Mounts (Step 8) | Volume mount configuration |
| SC-11 | 11 | Custom Entry Point (Step 9) | Custom entry point script setup |
| SC-12 | 12 | Custom Scripts (Step 10) | Custom hook script configuration |
| SC-13 | 13 | Configuration Summary (Step 11) | Final review and save configuration |

## Navigation Flow

- **Linear progression**: SC-0 → SC-1 → SC-3 to SC-13 (via SC-2 controller)
- **SC-2 note**: Controller framework that orchestrates Steps 1-11, not directly user-facing
- **Step navigation**: Only consecutive steps allowed (no jumping)
- **Memory-based**: SC-1 creates project files, SC-3 to SC-13 are memory-only until saved
