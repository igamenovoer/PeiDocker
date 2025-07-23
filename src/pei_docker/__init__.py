"""
PeiDocker - A sophisticated Docker automation framework.

Transform YAML configurations into reproducible containerized environments
without requiring deep knowledge of Dockerfiles or docker-compose.
"""

try:
    from importlib.metadata import version
    __version__ = version("pei-docker")
except ImportError:
    __version__ = "0.1.0"

__all__ = ["__version__"]