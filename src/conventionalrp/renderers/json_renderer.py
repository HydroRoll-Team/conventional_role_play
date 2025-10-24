import json
from typing import Any, Dict, List
from .base import BaseRenderer


class JSONRenderer(BaseRenderer):
    def __init__(self, pretty: bool = True, indent: int = 2, sort_keys: bool = False):
        super().__init__()
        self.pretty = pretty
        self.indent = indent if pretty else None
        self.sort_keys = sort_keys
        self.style = {}
    
    def render(self, data: Any) -> str:
        if self.pretty and isinstance(data, list):
            output = {
                "metadata": {
                    "total_entries": len(data),
                    "renderer": "ConventionalRP JSONRenderer",
                    "version": "1.0.0",
                },
                "statistics": self._calculate_stats(data),
                "data": data,
            }
        else:
            output = data
        
        return json.dumps(
            output,
            ensure_ascii=False,
            indent=self.indent,
            sort_keys=self.sort_keys,
        )
    
    def _calculate_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        stats = {
            "dialogue": 0,
            "dice": 0,
            "narration": 0,
            "system": 0,
            "success": 0,
            "failure": 0,
            "other": 0,
        }
        
        speakers = set()
        
        for item in data:
            if not isinstance(item, dict):
                continue
            
            token_type = item.get("type", "unknown")
            if token_type in stats:
                stats[token_type] += 1
            else:
                stats["other"] += 1
            
            if "speaker" in item and item["speaker"]:
                speakers.add(item["speaker"])
        
        stats["unique_speakers"] = len(speakers)
        stats["speakers"] = sorted(list(speakers))
        
        return stats

    def set_style(self, style):
        self.style = style
        
        # 从 style 中提取设置
        if isinstance(style, dict):
            if "pretty" in style:
                self.pretty = style["pretty"]
                self.indent = 2 if self.pretty else None
            if "indent" in style:
                self.indent = style["indent"]
            if "sort_keys" in style:
                self.sort_keys = style["sort_keys"]

