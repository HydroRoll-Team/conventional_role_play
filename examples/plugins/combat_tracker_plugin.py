import sys
import os
from pathlib import Path
import re
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from conventionalrp.plugins.base import ProcessorPlugin


class CombatTrackerPlugin(ProcessorPlugin):
    """战斗数据追踪插件"""
    
    def __init__(self):
        super().__init__("CombatTracker", "1.0.0")
        self.damage_pattern = re.compile(r'(\d+)\s*点?(伤害|damage|dmg)', re.IGNORECASE)
        self.heal_pattern = re.compile(r'(\d+)\s*点?(治疗|healing|heal)', re.IGNORECASE)
    
    def initialize(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.total_damage = 0
        self.total_healing = 0
        self.character_stats = {}
        self.logger.info("CombatTrackerPlugin initialized")
    
    def process_token(self, token: Dict[str, Any]) -> Dict[str, Any]:
        content = token.get("content", "")
        speaker = token.get("speaker", "Unknown")
        
        damage_match = self.damage_pattern.search(content)
        if damage_match:
            damage = int(damage_match.group(1))
            self.total_damage += damage
            
            if speaker not in self.character_stats:
                self.character_stats[speaker] = {"damage_dealt": 0, "healing_done": 0}
            self.character_stats[speaker]["damage_dealt"] += damage
            
            token["combat_data"] = {
                "type": "damage",
                "amount": damage,
                "total_damage": self.total_damage,
            }
        
        heal_match = self.heal_pattern.search(content)
        if heal_match:
            healing = int(heal_match.group(1))
            self.total_healing += healing
            
            if speaker not in self.character_stats:
                self.character_stats[speaker] = {"damage_dealt": 0, "healing_done": 0}
            self.character_stats[speaker]["healing_done"] += healing
            
            token["combat_data"] = {
                "type": "healing",
                "amount": healing,
                "total_healing": self.total_healing,
            }
        
        return token
    
    def get_combat_summary(self) -> Dict[str, Any]:
        return {
            "total_damage": self.total_damage,
            "total_healing": self.total_healing,
            "net_damage": self.total_damage - self.total_healing,
            "character_stats": self.character_stats,
        }
    
    def reset_stats(self):
        self.total_damage = 0
        self.total_healing = 0
        self.character_stats.clear()
        self.logger.info("Combat stats reset")


if __name__ == "__main__":
    plugin = CombatTrackerPlugin()
    plugin.initialize()
    
    test_tokens = [
        {"type": "dialogue", "speaker": "战士", "content": "我攻击兽人，造成12点伤害"},
        {"type": "dialogue", "speaker": "法师", "content": "火球术命中，造成28点伤害"},
        {"type": "dialogue", "speaker": "牧师", "content": "治疗术，恢复15点生命值"},
        {"type": "dialogue", "speaker": "战士", "content": "再次攻击，造成8点伤害"},
    ]

    for token in test_tokens:
        processed = plugin.process_token(token)
        if "combat_data" in processed:
            print(f"  {processed['speaker']}: {processed['combat_data']}")
            
    summary = plugin.get_combat_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
