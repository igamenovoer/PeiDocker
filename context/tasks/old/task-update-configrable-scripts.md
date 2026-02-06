problem:
- this project now supports custom scripts with arguments, see `pei_docker\templates\config-template-full.yml`, but many of the utility scripts in `pei_docker\project_files\installation\stage-{1,2}\system` are still using env variables to pass arguments, which is not consistent with the new design, we need to update them to use cli args

what to update:
- `pei_docker\project_files\installation\stage-1\system\ros2\install-ros2.sh`, the following options:
- - `ROS2_PREFER_DISTRO` controls which ROS2 distro to install, remove it, force user to specify it via `--distro`, if not specified, default to `rolling`, and warn the user about this.
- - add `--with-gui` option, if specified, install GUI packages like `rqt`, `rviz2`, otherwise install only CLI tools.
- - add `--with-nav2-full` option, if specified, install full Nav2 packages, otherwise install only minimal Nav2 packages (`lifecycle` and `util`)

- `pei_docker\project_files\installation\stage-1\system\ros2\setup-ros2-repo.sh`, the following options:
- - `ROS2_REPO_NAME` controls which ROS2 repository to use, remove it, force user to specify it via `--repo`, if not specified, default to `ros2`, and warn the user about this.