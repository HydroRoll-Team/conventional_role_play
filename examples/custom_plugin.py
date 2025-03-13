from conventionalrp.plugins.plugin_manager import PluginManager

class CustomPlugin:
    def __init__(self):
        self.name = "Custom Plugin"
    
    def process(self, data):
        # Custom processing logic
        processed_data = data.upper()  # Example transformation
        return processed_data

def main():
    plugin_manager = PluginManager()
    custom_plugin = CustomPlugin()
    
    plugin_manager.register_plugin(custom_plugin)
    
    # Example data to process
    data = "This is a sample TRPG log."
    result = custom_plugin.process(data)
    
    print(f"Processed Data: {result}")

if __name__ == "__main__":
    main()