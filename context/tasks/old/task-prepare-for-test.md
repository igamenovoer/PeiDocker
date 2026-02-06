problem:
- currently, to test a build, we have a lot of apt packages to download, repeatedly for each test case, which is time-consuming, we want to create a dir in `<workspace_root>/tmp/apt-cache` to cache the apt packages, so that we can reuse them in subsequent tests.

do this:
- create a minimal test case, and mount the `<workspace_root>/tmp/apt-cache` into the container to store all the apt packages, and in future tests, we can reuse the cached packages.
- note that, because you cannot mount dir during build, but you can see that `pei_docker\project_files\installation\stage-{1,2}\tmp` is designed for this purpose, you can copy the cached packages to this dir (NOT in the source repo, but in your created project using `pei.py`), and then use it during build because they will be copied to the container during build.
- see `pei_docker\templates\config-template-full.yml` about how to mount host directories into the container