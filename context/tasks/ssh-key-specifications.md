# Allow specifying SSH keys in config

Currently, in the configuration `pei_docker\templates\config-template-full.yml`, there is an `ssh` section, under which you can specify the public key file via `pubkey_file`, and if that is set, the public key represents an authorized key for accesing this container.

Now, implement more features about the ssh keys:
- add `pubkey_text`, where user can provide a public key in  form, this conflicts with `pubkey_file`. If both are given, raise error. The given `pubkey_text` will be written into the system as authorized keys.
- add `privkey_text` and `privkey_file`, the private key to be imported as ssh key, can only specify one of them. If specified, the key will be imported as ssh key. You should recognize the key type and deal with that properly, and generate the public key automatically, also add the generated public key to authorized keys.
- note that, the given private kay and public key are NOT PAIRED, so do not assume such, the given public key should be added to authorized keys and your public key should be generated from private key.

For these new features, document them clearly in the configuration file, gives example.

## Test data
you can use the following data for testing. Note that, the given private key and public key are NOT PAIRED.

- private key:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABCLeSpkKu
zfp8gLIO/O6v0GAAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIFPW+lmS7RfUgmm/
zHEwJ1qrxX//PVZ1IRBx9kgrr11+AAAAoE33cdhrQMyeBuE2jpkJE0NdiGdK80qW2cJjUc
/5JfZSvRIF0CRD6qDt2/aOig6KQVb60ky5pAaO2nymIzTZZaVE44+LNJ46f56vqnBDQrFO
/uLpyhpHFluGcphOt8myrp0F4kBJj2KObJubJLAcd4aVbWgNZ4kM+KfYnEiSG88d5JR136
ZkKSpbazcnFf58IrZOPghEQPoFUeVRvnlKWPE=
-----END OPENSSH PRIVATE KEY-----
```

- publik key:
  
```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDFFy2DpsaaLcixgYgT8+7GxVR5mRGOx7urSe4rKjZ5G igamenovoer@IGAMEWORK-7770
```
