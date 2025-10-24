from typing import Any, Dict, List, Optional
from .base import BaseRenderer


class HTMLRenderer(BaseRenderer):
    THEMES = {
        "light": {
            "bg_color": "#ffffff",
            "text_color": "#333333",
            "header_bg": "#f5f5f5",
            "border_color": "#e0e0e0",
            "dialogue_color": "#4CAF50",
            "dice_color": "#2196F3",
            "narration_color": "#FF9800",
            "system_color": "#9E9E9E",
            "success_color": "#43a047",
            "failure_color": "#e53935",
            "code_bg": "#f5f5f5",
        },
        "dark": {
            "bg_color": "#1e1e1e",
            "text_color": "#d4d4d4",
            "header_bg": "#2d2d30",
            "border_color": "#3e3e42",
            "dialogue_color": "#6adb8d",
            "dice_color": "#5fb3f5",
            "narration_color": "#ffb74d",
            "system_color": "#bdbdbd",
            "success_color": "#66bb6a",
            "failure_color": "#ef5350",
            "code_bg": "#2d2d30",
        },
        "fantasy": {
            "bg_color": "#f9f6f1",
            "text_color": "#3e2723",
            "header_bg": "#d7ccc8",
            "border_color": "#bcaaa4",
            "dialogue_color": "#8d6e63",
            "dice_color": "#5d4037",
            "narration_color": "#795548",
            "system_color": "#a1887f",
            "success_color": "#7cb342",
            "failure_color": "#c62828",
            "code_bg": "#efebe9",
        },
    }
    
    def __init__(self, theme: str = "light", custom_css: Optional[str] = None):
        super().__init__()
        self.title = "Rendered Log"
        self.theme = theme if theme in self.THEMES else "light"
        self.custom_css = custom_css
    
    def _get_css(self) -> str:
        colors = self.THEMES[self.theme]
        
        css = f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: {colors['bg_color']};
            color: {colors['text_color']};
            line-height: 1.6;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            background: linear-gradient(135deg, {colors['header_bg']} 0%, {colors['border_color']} 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            color: {colors['text_color']};
        }}
        
        .subtitle {{
            font-size: 1.1em;
            opacity: 0.8;
        }}
        
        .stats {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            background: {colors['bg_color']};
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 0.9em;
            border: 1px solid {colors['border_color']};
        }}
        
        .stat-label {{
            opacity: 0.7;
            margin-right: 5px;
        }}
        
        .stat-value {{
            font-weight: bold;
        }}
        
        .content-wrapper {{
            background: {colors['bg_color']};
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .token {{
            margin: 15px 0;
            padding: 15px;
            border-left: 4px solid {colors['border_color']};
            border-radius: 5px;
            background: {colors['header_bg']};
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .token:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .token.dialogue {{
            border-left-color: {colors['dialogue_color']};
        }}
        
        .token.dice {{
            border-left-color: {colors['dice_color']};
        }}
        
        .token.narration {{
            border-left-color: {colors['narration_color']};
        }}
        
        .token.system {{
            border-left-color: {colors['system_color']};
        }}
        
        .token.success {{
            border-left-color: {colors['success_color']};
            background: {colors['success_color']}15;
        }}
        
        .token.failure {{
            border-left-color: {colors['failure_color']};
            background: {colors['failure_color']}15;
        }}
        
        .token-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        
        .type-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .type-badge.dialogue {{
            background: {colors['dialogue_color']};
            color: white;
        }}
        
        .type-badge.dice {{
            background: {colors['dice_color']};
            color: white;
        }}
        
        .type-badge.narration {{
            background: {colors['narration_color']};
            color: white;
        }}
        
        .type-badge.system {{
            background: {colors['system_color']};
            color: white;
        }}
        
        .speaker {{
            font-weight: 700;
            font-size: 1.1em;
            color: {colors['text_color']};
        }}
        
        .content {{
            margin-top: 8px;
            line-height: 1.8;
            font-size: 1em;
        }}
        
        .metadata {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid {colors['border_color']};
            font-size: 0.85em;
            opacity: 0.7;
            flex-wrap: wrap;
        }}
        
        .metadata-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .tags {{
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}
        
        .tag {{
            background: {colors['code_bg']};
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            border: 1px solid {colors['border_color']};
        }}
        
        code {{
            background: {colors['code_bg']};
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .dice-result {{
            display: inline-block;
            background: {colors['dice_color']};
            color: white;
            padding: 3px 10px;
            border-radius: 5px;
            font-weight: bold;
            margin-left: 5px;
        }}
        
        footer {{
            margin-top: 40px;
            padding: 20px;
            text-align: center;
            opacity: 0.6;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            h1 {{
                font-size: 1.8em;
            }}
            
            .token {{
                padding: 10px;
            }}
        }}
        """
        
        if self.custom_css:
            css += "\n" + self.custom_css
        
        return css
    
    def render(self, data: List[Dict[str, Any]]) -> str:
        if data and not isinstance(data[0], dict):
            data = [{"type": "text", "content": str(item)} for item in data]
        
        stats = self._calculate_stats(data)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>{self._get_css()}</style>
</head>
<body>
    <header>
        <h1>🎲 {self.title}</h1>
        <div class="subtitle">完整的游戏日志与数据分析</div>
        <div class="stats">
            <div class="stat-item">
                <span class="stat-label">总条目:</span>
                <span class="stat-value">{stats['total']}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">对话:</span>
                <span class="stat-value">{stats['dialogue']}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">骰子:</span>
                <span class="stat-value">{stats['dice']}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">旁白:</span>
                <span class="stat-value">{stats['narration']}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">系统:</span>
                <span class="stat-value">{stats['system']}</span>
            </div>
        </div>
    </header>
    
    <div class="content-wrapper">
"""
        
        for item in data:
            html += self._render_token(item)
        
        html += """    </div>
    
    <footer>
        <p>Generated by ConventionalRP HTML Renderer</p>
        <p>Theme: """ + self.theme.capitalize() + """</p>
    </footer>
</body>
</html>"""
        
        return html
    
    def _render_token(self, token: Dict[str, Any]) -> str:
        token_type = token.get("type", "unknown")
        speaker = token.get("speaker", "")
        content = str(token.get("content", ""))
        
        content = (content
                  .replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;"))
        
        if token_type == "dice" and "result" in token:
            content += f' <span class="dice-result">{token["result"]}</span>'
        
        html = f'        <div class="token {token_type}">\n'
        html += '            <div class="token-header">\n'
        html += f'                <span class="type-badge {token_type}">{token_type}</span>\n'
        
        if speaker:
            html += f'                <span class="speaker">{speaker}</span>\n'
        
        html += '            </div>\n'
        html += f'            <div class="content">{content}</div>\n'
        
        metadata_items = []
        
        if "timestamp" in token:
            metadata_items.append(f'⏰ {token["timestamp"]}')
        
        if "tags" in token and token["tags"]:
            tags_html = '<div class="tags">'
            for tag in token["tags"]:
                tags_html += f'<span class="tag">{tag}</span>'
            tags_html += '</div>'
            metadata_items.append(tags_html)
        
        if "combat_data" in token:
            combat = token["combat_data"]
            if combat.get("type") == "damage":
                metadata_items.append(f'⚔️ 伤害: {combat["amount"]}')
            elif combat.get("type") == "healing":
                metadata_items.append(f'💚 治疗: {combat["amount"]}')
        
        if metadata_items:
            html += '            <div class="metadata">\n'
            for item in metadata_items:
                html += f'                <div class="metadata-item">{item}</div>\n'
            html += '            </div>\n'
        
        html += '        </div>\n'
        
        return html
    
    def _calculate_stats(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        stats = {
            "total": len(data),
            "dialogue": 0,
            "dice": 0,
            "narration": 0,
            "system": 0,
        }
        
        for item in data:
            token_type = item.get("type", "unknown")
            if token_type in stats:
                stats[token_type] += 1
        
        return stats
    
    def set_style(self, style):
        """设置样式（向后兼容）"""
        if style in self.THEMES:
            self.theme = style

