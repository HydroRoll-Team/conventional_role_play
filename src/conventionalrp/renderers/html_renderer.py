from .base import BaseRenderer

class HTMLRenderer(BaseRenderer):
    def __init__(self):
        super().__init__()
        self.title = "TRPG Log Output"
    
    def render(self, data):
        html_content = f"<html><head><title>{self.title}</title></head><body>"
        html_content += "<h1>TRPG Log Output</h1>"
        html_content += "<ul>"
        
        for entry in data:
            html_content += f"<li>{entry}</li>"
        
        html_content += "</ul></body></html>"
        return html_content
    
    def set_style(self, style):
        # Implement style setting if needed
        pass