from .base import BaseRenderer

class MarkdownRenderer(BaseRenderer):
    def render(self, data):
        """
        Renders the given data in Markdown format.
        
        Args:
            data (dict): The data to render.
        
        Returns:
            str: The rendered Markdown string.
        """
        markdown_output = ""
        for key, value in data.items():
            markdown_output += f"## {key}\n\n{value}\n\n"
        return markdown_output

    def set_style(self, style):
        """
        Sets the style for the Markdown renderer.
        
        Args:
            style (dict): A dictionary of style options.
        """
        self.style = style  # Currently, Markdown does not support styling, but this can be extended.