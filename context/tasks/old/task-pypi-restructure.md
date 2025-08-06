restructure the project, to make it suitable for pypi publish, see `https://raw.githubusercontent.com/igamenovoer/quicknote/refs/heads/main/dev-guide/project-init-guide.md` for details.

attention:
- do not touch the current `context` dir, leave it as is
- do not touch the current `contribs` dir, leave it as is
- for any dir covered by `.gitignore`, do not touch it, leave it as is
- we use `pixi` for python package management, but it can be integrated into `pyproject.toml`, so remove `pixi` related files and use `pyproject.toml` instead, after integration