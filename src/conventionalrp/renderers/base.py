class BaseRenderer:
    def render(self, data):
        raise NotImplementedError("Render method must be implemented by subclasses.")

    def set_style(self, style):
        self.style = style