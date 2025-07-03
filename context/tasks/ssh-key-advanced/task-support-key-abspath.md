# support absolute path to specify ssh keys

## Goal

in `pubkey_file` and `privkey_file`, allow the user to specify absolute path, and a single character `~` to represent current system ssh keys

In detail, like this:
- `privkey_file` can be absolute path, say for example, `/mypath/mykey.pub`. Previously, `privkey_file` will be copied alongside with the `/installation` folder into docker (via `ADD` command in dockerfile, see `pei_docker/project_files/stage-1.Dockerfile`), so the specified file path must be relative. Now if given abs path, it can refer to any file in the system (assuming you have permission to read it), the behavior is
- - read the file (via `cat` for example) and write the string into the temporary dir `installation/stage-1/generated` (not in the source repo, but in the created project dir via `python -m pei_docker.pei create` command)
- - pass the generated file path to the docker compose yml file (see `pei_docker/templates/base-image-gen.yml`, in `build.ssh.privkey_file`)
- - the processing is very much like how you handle `privkey_text`, but this time the text comes from a file outside of the project tree.
- the above also applies to `pubkey_file`

In case the user wants to refer to system ssh keys in `~/.ssh`, he will simply write a `~` in `pubkey_file` or `privkey_file`, and here is what you do:
- treat it as `~/.ssh/<the key file>`
- if multiple keys present, then the default priority order follows this, pick the highest priority one to use:
~/.ssh/id_rsa
~/.ssh/id_dsa
~/.ssh/id_ecdsa
~/.ssh/id_ed25519