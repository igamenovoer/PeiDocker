# Debugging the behavior of GUI when creating or loading a project

On startup, the GUI creates a new project or loads an existing one based on the user's selection, it has bug, the GUI does not set its user-facing configurations according to the project settings in the project's `user_config.yml`.

## Test Data

you can use `tmp/build-example` as test data, and start the GUI with the following command:

```bash
pei-docker-gui start --project-dir ./tmp/build-example --port <choose-a-port>
```

## Problem Description

you can see that `tmp/build-example/user_config.yml` already has some settings, for example, in the `ssh` section:

```yaml
  # ssh settings
  ssh:
    enable: true

    # port in container, if given, this port WILL be set inside container as SSH port
    port: 22  

    # mapped port on host machine, if given, this port will be mapped to the container SSH port
    host_port: 2222

    # ssh users, the key is user name, value is user info
    users:
      me:
        password: '123456'

        # SSH Key Options (choose one method per key type):
        
        # Public key options (mutually exclusive):
        pubkey_file: null    # Path to public key file (relative to installation directory)
        pubkey_text: null    # Direct public key content (conflicts with pubkey_file)
        
        # Private key options (mutually exclusive):
        privkey_file: null   # Path to private key file (relative to installation directory)
        privkey_text: null   # Direct private key content (conflicts with privkey_file)
        
        uid: 1000
        
      you:
        password: '654321'
        pubkey_file: null
        pubkey_text: null
        privkey_file: null
        privkey_text: null
        privkey_file: null
        privkey_text: null
        uid: 1001
        
      root: # you can configure root user here
        password: root
        pubkey_file: null
        pubkey_text: null
        privkey_file: null
        privkey_text: null
        uid: 0  # root uid, always 0 regardless of what you put here
```

It has some default users, these are not reflected in the GUI. Other settings have the same issue too. You should load the project and set GUI states accordingly.

Also, when I change SSH settings in the GUI, and save it, the changes are not reflected in the `user_config.yml` file. It should overwrite the whole `ssh` section in the file with the new settings. Similarly for other sections.