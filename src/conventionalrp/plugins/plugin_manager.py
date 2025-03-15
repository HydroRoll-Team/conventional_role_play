import os
import importlib


class PluginManager:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins = []

    def load_plugins(self):
        for plugin in os.listdir(self.plugin_dir):
            if plugin.endswith(".py"):
                plugin_name = plugin.split(".")[0]
                module = importlib.import_module(f"{self.plugin_dir}.{plugin_name}")
                self.plugins.append(module)

    def run_plugins(self):
        for plugin in self.plugins:
            plugin.run()
