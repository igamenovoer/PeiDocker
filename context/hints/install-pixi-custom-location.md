You can install pixi in a custom location by setting the `PIXI_HOME` environment variable before installation. Here are the methods:

## Method 1: Set environment variable before installation

```bash
export PIXI_HOME=/path/to/your/custom/location
curl -fsSL https://pixi.sh/install.sh | bash
```

Or for PowerShell on Windows:
```powershell
$env:PIXI_HOME = "C:\path\to\your\custom\location"
iwr -useb https://pixi.sh/install.ps1 | iex
```

## Method 2: One-liner installation

```bash
PIXI_HOME=/path/to/your/custom/location curl -fsSL https://pixi.sh/install.sh | bash
```

## Method 3: Manual installation

1. Download the appropriate binary for your system from the [GitHub releases page](https://github.com/prefix-dev/pixi/releases)
2. Extract it to your desired location
3. Add that location to your PATH

## After installation

Make sure to add the custom pixi location to your PATH. Add this to your shell configuration file (`.bashrc`, `.zshrc`, etc.):

```bash
export PATH="/path/to/your/custom/location/bin:$PATH"
```

The `PIXI_HOME` environment variable tells the installer where to place pixi instead of the default `~/.pixi` directory. The pixi binary will be installed in `$PIXI_HOME/bin/pixi`.