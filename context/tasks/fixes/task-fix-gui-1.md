# Do this task

Fix the following issues of the GUI. We use the terminology as said in `context/tasks/prefix/prefix-terminology.md`.

## State is lost when switching between tabs without explicitly saving

Currently, when you switch between different tabs in the GUI, any unsaved changes are lost. This can lead to frustration as users may forget to save their work before navigating away. When switching between tabs, the GUI should not lose the current state, because the user will expect that the current state is in memory and can be saved later.

For this, you should create an automatic test that verifies that the state is preserved when switching between tabs, using `playwright` or similar tools. The test should simulate the following steps:
1. Open the GUI and make changes in one tab.
2. Switch to another tab.
3. Switch back to the original tab.
4. Verify that the changes are still present.
5. Go to summary tab to see if the changes are reflected there.

## Project Information Tab

- "Base Docker Image" should be a text input field, not a dropdown, it should be the same image tag as used in `docker pull` command.

## SSH Settings Tab

- The public key and private key input areas are too narrow, make sure they are using the full width of the parent container. You should refer to the `script` tab for reference on how to use the full width, just like the inline script field does.

- The password input field should not mask the text, just show the password in plain text, it is not sensitive information in this context. The password should only contain letters, numbers, dashes, and underscores, prevent users from entering other characters. If they do, mark the field as invalid and show an error message.

## Network Settings Tab

### Apt Configuration

- missing `cn.archive.ubuntu.com` in the list of apt mirrors, name it as `Ubuntu CN Mirror`.
- for all mirrors, show it like this: `full_name(short_name): URL`, for example, `Tsinghua University (tuna): https://mirrors.tuna.tsinghua.edu.cn/ubuntu/`.

### Port Mappings

- Show a warning that the port mapping will be applied to both stages (`stage-1` and `stage-2`). For more customization, users can edit the `user_config.yml` file directly.
- Show available port mapping format:
  ```yaml
  # single port mapping
  <host_port>:<container_port>
  # range port mapping
  <host_port_start>-<host_port_end>:<container_port_start>-<container_port_end>
  ```
- "Warning: Port < 1024 requires root privileges" is not needed, remove it.
- "Docker Compose Format:" is not needed, remove it, the whole info box can be removed.
- validate the port mapping format, particularly for the range format, and show an error message if the number of ports in the host and container do not match, or if the format is incorrect.

## Storage Settings Tab

- combine " Key Concepts:" and "Storage Note:" into one section, how in the current "key concepts" section, explain the key concepts of storage and mounts in the PeiDocker context, their intended usecase and constraints.

## Scripts Tab

- "ℹ️ Important: Script Path Access Rules" section uses too much vertical space, reduce the space between the lines to make it more compact.
- "**Why?** Stage-1 builds first and becomes the foundation. Stage-2 builds on top of Stage-1, inheriting all its resources." can be removed, add this information to the "Stage-2 Scripts" text section instead.

## Summary Tab

- "Generated user_config.yml Preview"  section should be directly below the "Validation Status" section.
- Besides "Generated user_config.yml Preview" and "Validation Status", other sections should be removed, as they are already covered by the `user_config.yml` preview.

### GUI-to-`user_config.yml` mapping is WRONG

currently it will generate something like this:

```yaml
stage_1:
  image:
    base: ubuntu:22.04
    output: peidocker-20250804-003934:stage-1
  ssh:
    enable: true
    port: 22
    host_port: 2222
    users:
      user1:
        password: '1234213'
        pubkey_file: null
        pubkey_text: null
        privkey_file: null
        privkey_text: null
  device:
    type: cpu
stage_2:
  image:
    output: peidocker-20250804-003934:stage-2
  scripts:
    on_build:
    - type: inline
      name: script-9585837d.bash
      content: '#!/bin/bash

        echo ''Inline script content'''
    - type: file
      path: stage-2/custom/script-fc41bac9.bash
```

This is wrong, particularly for the `scripts` section, you should see the `config-template-full.yml` file for the correct format, and check `docs/` and the `src/pei_docker/examples` for more info.