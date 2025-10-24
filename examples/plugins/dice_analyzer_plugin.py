import sys
import os
from pathlib import Path
import re
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from conventionalrp.plugins.base import AnalyzerPlugin


class DiceAnalyzerPlugin(AnalyzerPlugin):
    """骰子投掷数据分析插件"""
    def __init__(self):
        super().__init__("DiceAnalyzer", "1.0.0")
        self.dice_pattern = re.compile(r'd(\d+)')
    
    def initialize(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.logger.info("DiceAnalyzerPlugin initialized")
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        if not isinstance(data, list):
            return {"error": "Input must be a list of tokens"}
        
        total_rolls = 0
        dice_types = {}
        success_count = 0
        failure_count = 0
        critical_hits = 0
        critical_fails = 0
        
        for token in data:
            if not isinstance(token, dict):
                continue
            
            token_type = token.get("type", "")
            content = token.get("content", "")
            
            if token_type == "dice":
                total_rolls += 1
                
                match = self.dice_pattern.search(content)
                if match:
                    dice_type = f"d{match.group(1)}"
                    dice_types[dice_type] = dice_types.get(dice_type, 0) + 1
            
            if token_type == "success":
                success_count += 1
            elif token_type == "failure":
                failure_count += 1
            
            if "critical" in content.lower():
                if "success" in token_type or "成功" in content:
                    critical_hits += 1
                elif "failure" in token_type or "失败" in content:
                    critical_fails += 1
        
        result = {
            "total_rolls": total_rolls,
            "dice_types": dice_types,
            "success_count": success_count,
            "failure_count": failure_count,
            "critical_hits": critical_hits,
            "critical_fails": critical_fails,
            "success_rate": success_count / total_rolls if total_rolls > 0 else 0,
            "critical_rate": (critical_hits + critical_fails) / total_rolls if total_rolls > 0 else 0,
        }
        
        self.logger.info(f"Analyzed {total_rolls} dice rolls")
        return result


if __name__ == "__main__":
    plugin = DiceAnalyzerPlugin()
    plugin.initialize()
    
    test_data = [
        {"type": "dice", "content": "d20=15"},
        {"type": "success", "content": "检定成功"},
        {"type": "dice", "content": "d6=4"},
        {"type": "dice", "content": "d20=20"},
        {"type": "success", "content": "大成功！Critical hit!"},
        {"type": "dice", "content": "d20=1"},
        {"type": "failure", "content": "大失败..."},
    ]
    
    result = plugin.analyze(test_data)
    for key, value in result.items():
        print(f"  {key}: {value}")
