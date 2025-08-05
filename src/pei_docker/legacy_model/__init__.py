"""
Legacy data models package.

This package contains deprecated data models that have been replaced by the
adapter pattern implementation. These models are kept for reference only and
should not be used in new code.

The main refactoring eliminated duplicate pydantic models by creating adapters
that wrap the attrs-based models from user_config.py.
"""

# Legacy models are not exported by default to discourage their use