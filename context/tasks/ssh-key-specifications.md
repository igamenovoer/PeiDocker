# Allow specifying SSH keys in config

Currently, in the configuration `pei_docker\templates\base-image-gen.yml`, there is an `ssh` section, under which you can specify the public key file via `pubkey_file`, and if that is set, the public key represents an authorized key for accesing this container.

Now, implement more features about the ssh keys:
- add `pubkey_text`, where user can provide a public key via plain text, this conflicts with `pubkey_file`. If both are given, raise error. The given `pubkey_text` will be written into the system as authorized keys.
- add `privkey_text` and `privkey_file`, the private key to be imported as ssh key, can only specify one of them. If specified, the key will be imported as ssh key. You should recognize the key type and deal with that properly.

For these new features, document them clearly in the configuration file, gives example.