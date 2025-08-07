pixi installation script:
`pei_docker\project_files\installation\stage-2\system\pixi\install-pixi.bash`

we are going to modify this script to support parameters for the Pixi installation. 

The script should accept parameters:
- `--cache-dir=cache_dir`, set the dir for pixi cache, it is path inside the container, absolute path. If not set, just use pixi default cache dir. The setting will be permanent for the user, that is, save it to `.bashrc`.
- `--install-dir=install_dir`, set the dir for pixi installation, it is path inside the container, absolute path. If not set, just use pixi default install dir. The user should still be able to call `pixi` command after installation directly within shell.
- `--verbose`, enable verbose output during installation, mainly for debugging purposes.

The script's behavior should be changed to:
- no longer look for env variable `PIXI_INSTALL_AT_HOME`, it should always install at user's home directory, which is the defualt pixi behavior.