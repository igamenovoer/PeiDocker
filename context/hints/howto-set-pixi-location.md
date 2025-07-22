# How to Customize Pixi Installation and Cache Location

This guide explains how to install Pixi to a non-default directory and how to set a custom cache directory permanently.

## Installing Pixi to a Custom Location

To control where Pixi is installed, you can set the `PIXI_HOME` environment variable before running the installation script.

### Linux & macOS

Run the following command in your terminal, replacing `/path/to/your/custom/pixi` with your desired installation path:

```bash
PIXI_HOME=/path/to/your/custom/pixi sh -c "$(curl -fsSL https://pixi.sh/install.sh)"
```

### Windows (PowerShell)

Run the following commands in PowerShell, replacing `C:\path\to\your\custom\pixi` with your desired installation path:

```powershell
$env:PIXI_HOME="C:\path\to\your\custom\pixi"; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://pixi.sh/install.ps1'))
```

### Making the Custom Installation Permanent (Updating PATH)

After installation, you must manually add the `bin` directory of your custom installation to your system's `PATH`.

#### Linux & macOS

1.  Open your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`).
2.  Add this line, using the same path as `PIXI_HOME`:
    ```bash
    export PATH="/path/to/your/custom/pixi/bin:$PATH"
    ```
3.  Save the file and restart your shell or source the configuration file.

#### Windows (PowerShell)

1.  Run the following commands, replacing the path with your custom installation directory:
    ```powershell
    $newPath = "C:\path\to\your\custom\pixi\bin"
    $oldPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
    $newCombinedPath = $newPath + ';' + $oldPath
    [System.Environment]::SetEnvironmentVariable('Path', $newCombinedPath, 'User')
    ```
2.  Restart your terminal for the change to take effect.

## Setting a Permanent Custom Cache Directory

To change where Pixi stores cached packages, set the `PIXI_CACHE_DIR` environment variable.

### Linux & macOS

1.  Open your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`).
2.  Add the following line, replacing the path with your desired cache location:
    ```bash
    export PIXI_CACHE_DIR="/path/to/your/cache"
    ```
3.  Save and restart your shell or source the configuration file.

### Windows

#### Command Prompt

```cmd
setx PIXI_CACHE_DIR "C:\path\to\your\cache"
```

#### PowerShell

```powershell
[System.Environment]::SetEnvironmentVariable('PIXI_CACHE_DIR', 'C:\path\to\your\cache', 'User')
```

Restart your terminal after running the command.