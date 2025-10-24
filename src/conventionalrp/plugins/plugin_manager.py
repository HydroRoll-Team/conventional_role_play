"""
插件管理器
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
import logging

from .base import Plugin

logger = logging.getLogger(__name__)


class PluginManager:
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugin_dirs = plugin_dirs or []
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_classes: Dict[str, Type[Plugin]] = {}
        
        logger.info("PluginManager initialized with %d directories", 
                   len(self.plugin_dirs))
    
    def add_plugin_dir(self, directory: str):

        if directory not in self.plugin_dirs:
            self.plugin_dirs.append(directory)
            logger.info(f"Added plugin directory: {directory}")
    
    def discover_plugins(self) -> List[str]:
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            path = Path(plugin_dir)
            if not path.exists():
                logger.warning(f"Plugin directory does not exist: {plugin_dir}")
                continue
            
            if str(path.parent) not in sys.path:
                sys.path.insert(0, str(path.parent))

            for py_file in path.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                
                module_name = py_file.stem
                discovered.append(module_name)
                logger.debug(f"Discovered plugin module: {module_name}")
        
        logger.info(f"Discovered {len(discovered)} plugin modules")
        return discovered
    
    def load_plugin_from_file(self, file_path: str) -> Optional[Type[Plugin]]:
        try:
            module_name = Path(file_path).stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            
            if spec is None or spec.loader is None:
                logger.error(f"Failed to load plugin spec: {file_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, Plugin) and 
                    obj is not Plugin):
                    logger.info(f"Loaded plugin class: {name} from {file_path}")
                    return obj
            
            logger.warning(f"No Plugin subclass found in: {file_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading plugin from {file_path}: {e}")
            return None
    
    def load_plugin(self, module_name: str) -> Optional[str]:
        try:
            module = importlib.import_module(module_name)
            
            # 查找 Plugin 子类
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, Plugin) and 
                    obj is not Plugin):
                    
                    plugin_class = obj
                    self.plugin_classes[name] = plugin_class
                    logger.info(f"Loaded plugin class: {name}")
                    return name
            
            logger.warning(f"No Plugin subclass found in module: {module_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading plugin module {module_name}: {e}")
            return None
    
    def register_plugin(
        self,
        plugin: Plugin,
        replace: bool = False
    ) -> bool:
        if plugin.name in self.plugins and not replace:
            logger.warning(f"Plugin {plugin.name} already registered")
            return False
        
        self.plugins[plugin.name] = plugin
        plugin.on_enable()
        logger.info(f"Registered plugin: {plugin.name}")
        return True
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} not found")
            return False
        
        plugin = self.plugins[plugin_name]
        plugin.on_disable()
        del self.plugins[plugin_name]
        logger.info(f"Unregistered plugin: {plugin_name}")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        return [plugin.get_metadata() for plugin in self.plugins.values()]
    
    def enable_plugin(self, plugin_name: str) -> bool:
        plugin = self.plugins.get(plugin_name)
        if plugin is None:
            logger.warning(f"Plugin {plugin_name} not found")
            return False
        
        if not plugin.enabled:
            plugin.enabled = True
            plugin.on_enable()
            logger.info(f"Enabled plugin: {plugin_name}")
        
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        plugin = self.plugins.get(plugin_name)
        if plugin is None:
            logger.warning(f"Plugin {plugin_name} not found")
            return False
        
        if plugin.enabled:
            plugin.enabled = False
            plugin.on_disable()
            logger.info(f"Disabled plugin: {plugin_name}")
        
        return True
    
    def execute_plugins(
        self,
        data: Any,
        plugin_type: Optional[Type[Plugin]] = None
    ) -> Any:
        result = data
        
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
            
            if plugin_type is not None and not isinstance(plugin, plugin_type):
                continue
            
            try:
                result = plugin.process(result)
                logger.debug(f"Executed plugin: {plugin.name}")
            except Exception as e:
                logger.error(f"Error executing plugin {plugin.name}: {e}")
        
        return result
    
    def clear_plugins(self):
        for plugin_name in list(self.plugins.keys()):
            self.unregister_plugin(plugin_name)
        
        self.plugin_classes.clear()
        logger.info("Cleared all plugins")
    
    def get_statistics(self) -> Dict[str, Any]:
        enabled_count = sum(1 for p in self.plugins.values() if p.enabled)
        
        return {
            "total_plugins": len(self.plugins),
            "enabled_plugins": enabled_count,
            "disabled_plugins": len(self.plugins) - enabled_count,
            "plugin_classes": len(self.plugin_classes),
            "plugin_directories": len(self.plugin_dirs),
        }
    
    def __repr__(self) -> str:
        return f"PluginManager(plugins={len(self.plugins)}, enabled={sum(1 for p in self.plugins.values() if p.enabled)})"
