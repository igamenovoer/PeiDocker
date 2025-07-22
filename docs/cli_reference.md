# CLI Reference

## `pei_docker`

**Usage:** `python -m pei_docker.pei [OPTIONS] COMMAND [ARGS]...`

### Options

| Option | Description |
| --- | --- |
| `--help` | Show this message and exit. |

### Commands

| Command | Description |
| --- | --- |
| `create` | Creates a new PeiDocker project. |
| `configure` | Configures a PeiDocker project. |
| `remove` | Removes Docker images and containers created by this project. |

---

## `create`

**Usage:** `python -m pei_docker.pei create [OPTIONS]`

### Options

| Option | Description |
| --- | --- |
| `-p`, `--project-dir DIRECTORY` | project directory (required) |
| `-e`, `--with-examples` | copy example files to the project dir |
| `--with-contrib` | copy contrib directory to the project dir |
| `--help` | Show this message and exit. |

---

## `configure`

**Usage:** `python -m pei_docker.pei configure [OPTIONS]`

### Options

| Option | Description |
| --- | --- |
| `-p`, `--project-dir DIRECTORY` | project directory (required) |
| `-c`, `--config FILE` | config file name, relative to the project dir |
| `-f`, `--full-compose` | generate full compose file with x-??? sections |
| `--help` | Show this message and exit. |

---

## `remove`

**Usage:** `python -m pei_docker.pei remove [OPTIONS]`

### Options

| Option | Description |
| --- | --- |
| `-p`, `--project-dir DIRECTORY` | project directory (required) |
| `-y`, `--yes` | skip confirmation prompts |
| `--help` | Show this message and exit. |
