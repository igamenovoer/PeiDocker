"""
Common stage processing logic to eliminate duplication between stage-1 and stage-2.
"""

from typing import Dict, List, Any, Optional, Callable, TypeVar
from pei_docker.webgui.constants import (
    CustomScriptLifecycleTypes,
    ScriptTypes,
    EntryModes
)

T = TypeVar('T')

class StageProcessor:
    """Provides common stage processing functionality to reduce code duplication."""
    
    @staticmethod
    def process_inline_scripts_metadata(
        config: Any,
        stage_key: str,
        ui_scripts: Any,
        script_path_prefix: str = '/pei-docker/scripts/'
    ) -> None:
        """Process inline scripts metadata for a specific stage.
        
        Args:
            config: OmegaConf config object
            stage_key: 'stage_1' or 'stage_2'
            ui_scripts: UI scripts object (ScriptsUI)
            script_path_prefix: Prefix for script paths
        """
        if stage_key not in config:
            return
            
        if '_inline_scripts' not in config[stage_key]:
            return
            
        inline_scripts = config[stage_key]._inline_scripts
        ui_scripts._inline_scripts_metadata.clear()
        ui_scripts._inline_scripts_metadata.update(dict(inline_scripts))
        
        # Check if entry point is an inline script
        if 'custom' in config[stage_key] and CustomScriptLifecycleTypes.ON_ENTRY in config[stage_key].custom:
            entry_points = config[stage_key].custom[CustomScriptLifecycleTypes.ON_ENTRY]
            if entry_points and len(entry_points) > 0:
                entry_point = entry_points[0]
                if entry_point.startswith(script_path_prefix):
                    script_name = entry_point.replace(script_path_prefix, '')
                    if script_name in inline_scripts:
                        ui_scripts.entry_mode = EntryModes.INLINE
                        ui_scripts.entry_inline_name = script_name
                        ui_scripts.entry_inline_content = inline_scripts[script_name]
    
    @staticmethod
    def build_inline_scripts_metadata(
        ui_scripts: Any,
        stage_name: str
    ) -> Dict[str, str]:
        """Build inline scripts metadata from UI state for a specific stage.
        
        Args:
            ui_scripts: UI scripts object (ScriptsUI)
            stage_name: Stage identifier for debugging
            
        Returns:
            Dictionary mapping script names to their content
        """
        inline_scripts: Dict[str, str] = {}
        
        # Check entry point
        if ui_scripts.entry_mode == "inline":
            script_name = ui_scripts.entry_inline_name
            script_content = ui_scripts.entry_inline_content
            if script_name and script_content:
                inline_scripts[script_name] = script_content
        
        # Check lifecycle scripts
        for lifecycle_key, scripts in ui_scripts.lifecycle_scripts.items():
            for script_data in scripts:
                if isinstance(script_data, dict) and script_data.get('type') == 'inline':
                    name = script_data.get('name', '')
                    content = script_data.get('content', '')
                    if name and content:
                        inline_scripts[name] = content
        
        # Add metadata from _inline_scripts_metadata if present
        if ui_scripts._inline_scripts_metadata:
            # _inline_scripts_metadata is Dict[str, Dict[str, str]]
            # We need to flatten it to Dict[str, str] for inline_scripts
            for name, metadata in ui_scripts._inline_scripts_metadata.items():
                if name not in inline_scripts and 'content' in metadata:
                    inline_scripts[name] = metadata['content']
        
        return inline_scripts
    
    @staticmethod
    def process_lifecycle_scripts(
        lifecycle_scripts: Dict[str, List[Any]],
        lifecycle_type: str,
        processor_func: Callable[[Dict[str, Any]], Optional[str]]
    ) -> List[str]:
        """Process lifecycle scripts of a specific type.
        
        Args:
            lifecycle_scripts: Dictionary of lifecycle scripts
            lifecycle_type: Type of lifecycle (e.g., ON_BUILD, ON_FIRST_RUN)
            processor_func: Function to process each script entry
            
        Returns:
            List of processed script paths
        """
        result = []
        
        if lifecycle_type in lifecycle_scripts:
            for script_data in lifecycle_scripts[lifecycle_type]:
                processed = processor_func(script_data)
                if processed:
                    result.append(processed)
        
        return result
    
    @staticmethod
    def extract_script_path(script_data: Any, script_path_prefix: str = '/pei-docker/scripts/') -> Optional[str]:
        """Extract script path from script data.
        
        Args:
            script_data: Script data (dict or string)
            script_path_prefix: Prefix for inline script paths
            
        Returns:
            Script path or None if invalid
        """
        if isinstance(script_data, dict):
            if script_data.get('type') == ScriptTypes.FILE and 'path' in script_data:
                path: str = script_data['path']
                return path
            elif script_data.get('type') == ScriptTypes.INLINE and 'name' in script_data:
                # For inline scripts, use the proper path
                name: str = script_data['name']
                return f"{script_path_prefix}{name}"
        elif isinstance(script_data, str):
            return script_data
        
        return None
    
    @staticmethod
    def parse_script_with_args(script_str: str) -> tuple[str, str]:
        """Parse script string to separate path and arguments.
        
        Returns (path, args) tuple.
        """
        import shlex
        try:
            parts = shlex.split(script_str)
            if parts:
                path = parts[0]
                # Rejoin the remaining parts as arguments
                args = ' '.join(parts[1:]) if len(parts) > 1 else ''
                return path, args
        except (ValueError, SyntaxError):
            # Fallback for simple parsing when shlex fails
            parts = script_str.split(None, 1)
            if len(parts) == 2:
                return parts[0], parts[1]
        return script_str.strip(), ''
    
    @staticmethod
    def handle_port_value(port_value: Any, default: int) -> int:
        """Handle port values that might be int or str.
        
        Args:
            port_value: Port value (int, str, or None)
            default: Default port value
            
        Returns:
            Integer port value
        """
        if isinstance(port_value, str):
            return int(port_value) if port_value.isdigit() else default
        elif isinstance(port_value, int):
            return port_value
        else:
            return default