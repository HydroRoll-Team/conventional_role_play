from .base import BaseRenderer
from typing import List, Dict, Any, Union


class MarkdownRenderer(BaseRenderer):
    def render(self, data: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
        """
        Renders the given data in Markdown format.

        Args:
            data: The data to render (can be list or dict).

        Returns:
            str: The rendered Markdown string.
        """
        if isinstance(data, list):
            return self._render_list(data)
        elif isinstance(data, dict):
            return self._render_dict(data)
        else:
            return str(data)
    
    def _render_list(self, data: List[Dict[str, Any]]) -> str:
        """渲染列表数据为 Markdown"""
        markdown_output = "# TRPG Log\n\n"
        
        for i, entry in enumerate(data, 1):
            if entry.get("type") == "metadata":
                markdown_output += f"## Entry {i}\n\n"
                markdown_output += f"**Timestamp**: {entry.get('timestamp', 'N/A')}  \n"
                markdown_output += f"**Speaker**: {entry.get('speaker', 'N/A')}  \n\n"
                
                content_items = entry.get("content", [])
                if content_items:
                    markdown_output += "**Content**:\n\n"
                    for content in content_items:
                        content_type = content.get("type", "unknown")
                        content_text = content.get("content", "")
                        markdown_output += f"- [{content_type}] {content_text}\n"
                    markdown_output += "\n"
            else:
                markdown_output += f"- {entry}\n"
        
        return markdown_output
    
    def _render_dict(self, data: Dict[str, Any]) -> str:
        """渲染字典数据为 Markdown"""
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
