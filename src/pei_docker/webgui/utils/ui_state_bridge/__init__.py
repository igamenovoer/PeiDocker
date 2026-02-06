"""
Bridge layer for converting between UI state and configuration models.

This module provides the UIStateBridge class that handles conversions between
NiceGUI bindable dataclasses (UI state) and attrs-based configuration models
through the adapter layer, as well as YAML serialization/deserialization.
"""

from pei_docker.webgui.utils.ui_state_bridge.bridge import UIStateBridge

__all__ = ['UIStateBridge']