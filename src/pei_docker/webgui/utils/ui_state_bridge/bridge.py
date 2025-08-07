"""
Main UIStateBridge class that ties together all conversion, loading, and building logic.
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import attrs
import cattrs
from omegaconf import OmegaConf

from pei_docker.webgui.constants import CustomScriptLifecycleTypes
from pei_docker.webgui.models.ui_state import AppUIState
from pei_docker.webgui.models.config_adapter import AppConfigAdapter
from pei_docker.user_config import (
    UserConfig as AttrsUserConfig,
    env_str_to_dict
)
from pei_docker.webgui.utils.ui_state_bridge.converters import UIToAttrsConverter
from pei_docker.webgui.utils.ui_state_bridge.loaders import ConfigLoader
from pei_docker.webgui.utils.ui_state_bridge.utils import clean_config_dict


class UIStateBridge:
    """Converts between UI state models and attrs configuration models.
    
    This class provides the main interface for:
    - Validating UI state
    - Saving UI state to YAML files
    - Loading YAML files into UI state
    - Converting between UI state and configuration models
    """
    
    def __init__(self) -> None:
        """Initialize the UIStateBridge with its components."""
        self._converter = UIToAttrsConverter()
        self._loader = ConfigLoader()
    
    def validate_ui_state(self, ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Validate current UI state without modifying it.
        
        Args:
            ui_state: AppUIState to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Convert UI state to attrs config for validation
            _ = self._converter.ui_to_attrs_config(ui_state)
            
            # attrs validation happens during object construction
            # If we get here, validation passed
            return True, []
            
        except (TypeError, ValueError, attrs.exceptions.NotAnAttrsClassError) as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
            return False, errors
    
    def save_to_yaml(self, ui_state: AppUIState, file_path: str) -> Tuple[bool, List[str]]:
        """Save UI state to YAML file with validation.
        
        Data flow: GUI state -> ui-data-model -> peidocker-data-model -> OmegaConf -> YAML file
        
        Args:
            ui_state: AppUIState to save
            file_path: Path to save the YAML file
            
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        # First validate
        is_valid, validation_errors = self.validate_ui_state(ui_state)
        if not is_valid:
            return False, validation_errors
        
        try:
            # Convert UI state to user_config format
            config_dict = self._converter.ui_to_user_config_format(ui_state)
            
            # Create directory if needed
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save using OmegaConf for better structured data handling
            conf = OmegaConf.create(config_dict)
            OmegaConf.save(conf, file_path)
            
            return True, []
            
        except Exception as e:
            errors.append(f"Save failed: {str(e)}")
            return False, errors
    
    def load_from_yaml(self, file_path: str, ui_state: AppUIState) -> Tuple[bool, List[str]]:
        """Load YAML configuration into UI state using proper data flow.
        
        Flow: user_config.yml -> OmegaConf -> UserConfig (peidocker model) -> UI state
        
        Args:
            file_path: Path to the YAML file to load
            ui_state: AppUIState to populate
            
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        try:
            # Step 1: Load YAML file directly with OmegaConf
            config = OmegaConf.load(file_path)
            
            if not config:
                errors.append("Empty configuration file")
                return False, errors
            
            # Step 2: Convert to Python dict and prepare for cattrs
            config_dict = OmegaConf.to_container(config, resolve=True)
            
            # Step 3: Apply pre-processing transformations
            if isinstance(config_dict, dict):
                # Cast to ensure proper type
                preprocessed_dict: Dict[str, Any] = {str(k): v for k, v in config_dict.items()}
                self._preprocess_config_dict(preprocessed_dict)
                config_dict = preprocessed_dict
            
            # Step 4: Parse into UserConfig using cattrs
            user_config: AttrsUserConfig = cattrs.structure(config_dict, AttrsUserConfig)
            
            # Step 5: Convert UserConfig to UI state
            self._loader.load_user_config_into_ui(user_config, ui_state)
            
            # Step 6: Load inline scripts metadata
            self._loader.load_inline_scripts_metadata(config, ui_state)
            
            return True, []
            
        except FileNotFoundError:
            errors.append(f"Configuration file not found: {file_path}")
            return False, errors
        except (TypeError, ValueError) as e:
            errors.append(f"Invalid configuration structure: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Load failed: {str(e)}")
            return False, errors
    
    def ui_to_config(self, ui_state: AppUIState) -> Any:
        """Convert UI state to attrs-based config through adapter.
        
        Args:
            ui_state: AppUIState to convert
            
        Returns:
            AppConfigAdapter object
        """
        result: Any = self._converter.ui_to_config_adapter(ui_state)
        return result
    
    def _ui_to_user_config_format(self, ui_state: AppUIState) -> Dict[str, Any]:
        """Convert UI state to user_config.yml format.
        
        This method is called by the summary tab for preview.
        
        Args:
            ui_state: AppUIState to convert
            
        Returns:
            Dictionary ready for YAML serialization
        """
        result: Dict[str, Any] = self._converter.ui_to_user_config_format(ui_state)
        return result
    
    def _preprocess_config_dict(self, config_dict: Dict[str, Any]) -> None:
        """Apply pre-processing transformations to config dict.
        
        This handles special cases like environment variable conversion
        and on_entry format normalization.
        
        Args:
            config_dict: Configuration dictionary to preprocess (modified in place)
        """
        for stage in ['stage_1', 'stage_2']:
            if stage not in config_dict:
                continue
            
            # Handle environment conversion from list to dict
            if 'environment' in config_dict[stage]:
                env = config_dict[stage]['environment']
                if env is not None and isinstance(env, list):
                    config_dict[stage]['environment'] = env_str_to_dict(env)
            
            # Handle on_entry conversion from string to list
            if 'custom' in config_dict[stage] and config_dict[stage]['custom'] is not None:
                custom = config_dict[stage]['custom']
                if CustomScriptLifecycleTypes.ON_ENTRY in custom and custom[CustomScriptLifecycleTypes.ON_ENTRY] is not None:
                    on_entry = custom[CustomScriptLifecycleTypes.ON_ENTRY]
                    if isinstance(on_entry, str):
                        # Convert string to single-element list
                        config_dict[stage]['custom'][CustomScriptLifecycleTypes.ON_ENTRY] = [on_entry]