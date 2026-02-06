"""
Converters for transforming between UI state and attrs configuration models.
"""

from typing import Dict, Any, Optional
import cattrs

from pei_docker.user_config import (
    UserConfig as AttrsUserConfig,
    StageConfig as AttrsStageConfig,
)
from pei_docker.webgui.models.ui_state import (
    AppUIState, StageUI, ProjectUI
)
from pei_docker.webgui.models.config_adapter import create_app_config_adapter
from pei_docker.webgui.utils.ui_state_bridge.builders import ConfigBuilder
from pei_docker.webgui.utils.ui_state_bridge.stage_processor import StageProcessor
from pei_docker.webgui.utils.ui_state_bridge.utils import (
    clean_config_dict,
    extract_project_info
)


class UIToAttrsConverter:
    """Converts UI state to attrs configuration models."""
    
    def ui_to_attrs_config(self, ui_state: AppUIState) -> AttrsUserConfig:
        """Convert UI state to attrs UserConfig.
        
        Args:
            ui_state: AppUIState object
            
        Returns:
            AttrsUserConfig object
        """
        stage_1 = self._ui_stage_to_attrs(ui_state.stage_1, ui_state.project, 1)
        stage_2 = self._ui_stage_to_attrs(ui_state.stage_2, ui_state.project, 2)
        
        return AttrsUserConfig(
            stage_1=stage_1,
            stage_2=stage_2
        )
    
    def _ui_stage_to_attrs(
        self,
        ui_stage: StageUI,
        ui_project: ProjectUI,
        stage_num: int
    ) -> Optional[AttrsStageConfig]:
        """Convert UI stage to attrs StageConfig.
        
        Args:
            ui_stage: StageUI object
            ui_project: ProjectUI object
            stage_num: Stage number (1 or 2)
            
        Returns:
            AttrsStageConfig object or None
        """
        # Build individual configurations using ConfigBuilder
        image = ConfigBuilder.build_image_config(ui_project, stage_num)
        
        # SSH config (stage 1 only)
        ssh = None
        if stage_num == 1:
            ssh = ConfigBuilder.build_ssh_config(ui_stage.ssh, ui_stage.ssh.enabled)
        
        # Proxy config
        proxy = ConfigBuilder.build_proxy_config(
            ui_stage.network.proxy_enabled,
            ui_stage.network.http_proxy
        )
        
        # APT config (stage 1 only)
        apt = None
        if stage_num == 1:
            apt = ConfigBuilder.build_apt_config(
                ui_stage.network.apt_mirror,
                proxy is not None
            )
        
        # Device config
        device = ConfigBuilder.build_device_config(ui_stage.environment.device_type)
        
        # Environment variables
        environment = ui_stage.environment.env_vars if ui_stage.environment.env_vars else None
        
        # Port mappings
        ports = ConfigBuilder.build_port_mappings(ui_stage.network.port_mappings)
        
        # Custom scripts
        custom = ConfigBuilder.build_custom_scripts(ui_stage.scripts)
        
        # Storage config (stage 2 only)
        storage = None
        if stage_num == 2:
            storage = ConfigBuilder.build_storage_config(ui_stage.storage)
        
        # Mount config
        mount = ConfigBuilder.build_mount_config(ui_stage.storage)
        
        return AttrsStageConfig(
            image=image,
            ssh=ssh,
            proxy=proxy,
            apt=apt,
            environment=environment,
            ports=ports,
            device=device,
            custom=custom,
            storage=storage,
            mount=mount
        )
    
    def ui_to_config_adapter(self, ui_state: AppUIState) -> Any:
        """Convert UI state to attrs-based config through adapter.
        
        Args:
            ui_state: AppUIState object
            
        Returns:
            AppConfigAdapter object
        """
        attrs_config = self.ui_to_attrs_config(ui_state)
        project_info = extract_project_info(ui_state.project)
        return create_app_config_adapter(attrs_config, project_info)
    
    def ui_to_user_config_format(self, ui_state: AppUIState) -> Dict[str, Any]:
        """Convert UI state to user_config.yml format.
        
        Data flow: UI state -> peidocker-data-model (attrs) -> dict -> YAML format
        This ensures consistency with save_to_yaml and eliminates code duplication.
        
        Args:
            ui_state: AppUIState object
            
        Returns:
            Dictionary ready for YAML serialization
        """
        try:
            # Step 1: Convert UI state to attrs UserConfig
            attrs_config = self.ui_to_attrs_config(ui_state)
            
            # Step 2: Convert attrs config to dict using cattrs
            config_dict = cattrs.unstructure(attrs_config)
            
            # Step 3: Add inline scripts metadata
            config_dict = self._add_inline_scripts_metadata(config_dict, ui_state)
            
            # Step 4: Clean up the config dict
            config_dict = clean_config_dict(config_dict)
            
            return config_dict
            
        except Exception:
            # If conversion fails, return a minimal config
            return {
                'stage_1': {'image': {'base': 'ubuntu:latest', 'output': 'pei-image:stage-1'}},
                'stage_2': {'image': {'output': 'pei-image:stage-2'}}
            }
    
    def _add_inline_scripts_metadata(
        self,
        config_dict: Dict[str, Any],
        ui_state: AppUIState
    ) -> Dict[str, Any]:
        """Add inline scripts metadata to the configuration dictionary.
        
        This preserves inline script content as metadata in the YAML for reconstruction.
        
        Args:
            config_dict: Configuration dictionary
            ui_state: AppUIState object
            
        Returns:
            Updated configuration dictionary
        """
        result = config_dict.copy()
        
        # Process stage-1 inline scripts
        if 'stage_1' in result:
            inline_scripts_1 = StageProcessor.build_inline_scripts_metadata(
                ui_state.stage_1.scripts,
                'stage_1'
            )
            if inline_scripts_1:
                result['stage_1']['_inline_scripts'] = inline_scripts_1
        
        # Process stage-2 inline scripts
        if 'stage_2' in result:
            inline_scripts_2 = StageProcessor.build_inline_scripts_metadata(
                ui_state.stage_2.scripts,
                'stage_2'
            )
            if inline_scripts_2:
                result['stage_2']['_inline_scripts'] = inline_scripts_2
        
        return result