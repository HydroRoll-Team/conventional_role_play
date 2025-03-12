from .base import BaseRenderer

class JSONRenderer(BaseRenderer):
    def render(self, data):
        import json
        return json.dumps(data, ensure_ascii=False, indent=4)

    def set_style(self, style):
        self.style = style  # Placeholder for potential styling options in the future