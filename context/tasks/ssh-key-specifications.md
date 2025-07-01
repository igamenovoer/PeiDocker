# Allow specifying SSH keys in config

Currently, in the configuration `pei_docker\templates\config-template-full.yml`, there is an `ssh` section, under which you can specify the public key file via `pubkey_file`, and if that is set, the public key represents an authorized key for accesing this container.

Now, implement more features about the ssh keys:
- add `pubkey_text`, where user can provide a public key in  form, this conflicts with `pubkey_file`. If both are given, raise error. The given `pubkey_text` will be written into the system as authorized keys.
- add `privkey_text` and `privkey_file`, the private key to be imported as ssh key, can only specify one of them. If specified, the key will be imported as ssh key. You should recognize the key type and deal with that properly, and generate the public key automatically, also add the generated public key to authorized keys.
- note that, the given private kay and public key are NOT PAIRED, so do not assume such, the given public key should be added to authorized keys and your public key should be generated from private key.

For these new features, document them clearly in the configuration file, gives example.

## Implementation guide
- Because `config-template-full.yml` will be parsed by python, and then the parsed results are set into `pei_docker\templates\base-image-gen.yml` which a docker compose template, those plain text keys will be problematic as they are multi-line strings with spaces. As such, you should write the plain text keys into temporary files, and reference them in `pubkey_file` and `privkey_file` in the `pei_docker\templates\base-image-gen.yml` (note that `privkey_file` is not implemented yet, implement it as well)
- As such, `pubkey_text` and `privkey_text` only exists in `config-template-full.yml`, there is no corresponding keys in the docker compose template `base-image-gen.yml`.

## Test data
you can use the following data for testing. Note that, the given private key and public key are NOT PAIRED.

To test two-user configurations, you can use both keys.

For single user case, just select one key.

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

```text
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABA6KBy+eb
ZyS0HlPIAHbJj8AAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIGrvSeVzXGZgItH1
G053XzoLT3Z4Kk68Hj5PTdwLthyEAAAAoBpmljEs0pdgvVCTGtJjCkCb0cedqiVI8GZwWH
uMt8LHn06AW1m4XArj45KR03Sttn7BymZpBjkKgDAzfzM92mcex9tJOxqFauiNlgcpjn2w
S7NEK4oo/LjMUMydoSsC+3ppvTpIUyQj0WH2KaP/RTUQrwny1W0Kdo5B/WgOeupon9dakz
5lt6/wVYFPYahu1kYyV+6F6vJnI3BsjuDKhw0=
-----END OPENSSH PRIVATE KEY-----
```

- publik key:
  
```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDFFy2DpsaaLcixgYgT8+7GxVR5mRGOx7urSe4rKjZ5G igamenovoer@IGAMEWORK-7770
```

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICPecH+1R9qfb+561fSFn5vwcSkoPJcGYvjsxb+lD3F+ igamenovoer@IGAMEWORK-7770
```