import sys
from typing import List, Dict, Any
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from conventionalrp.core.parser import Parser
from conventionalrp.core.processor import Processor


class DiceRollAnalyzer:
    """骰点统计分析插件"""
    
    def __init__(self):
        self.name = "Dice Roll Analyzer"
        
    def analyze(self, parsed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        stats = {
            "total_rolls": 0,
            "by_character": {},
            "dice_types": {}
        }
        
        for entry in parsed_data:
            speaker = entry.get("speaker", "Unknown")
            for content in entry.get("content", []):
                if content.get("type") == "dice_roll":
                    stats["total_rolls"] += 1
                    
                    # 按角色统计
                    if speaker not in stats["by_character"]:
                        stats["by_character"][speaker] = 0
                    stats["by_character"][speaker] += 1
                    
                    # 按骰子类型统计
                    dice_type = content.get("dice_type", "unknown")
                    if dice_type not in stats["dice_types"]:
                        stats["dice_types"][dice_type] = 0
                    stats["dice_types"][dice_type] += 1
        
        return stats


class DialogueExtractor:
    """对话提取插件"""
    
    def __init__(self):
        self.name = "Dialogue Extractor"
        
    def extract(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        dialogues = []
        
        for entry in parsed_data:
            speaker = entry.get("speaker", "Unknown")
            timestamp = entry.get("timestamp", "")
            
            for content in entry.get("content", []):
                if content.get("type") == "dialogue":
                    dialogues.append({
                        "speaker": speaker,
                        "timestamp": timestamp,
                        "dialogue": content.get("dialogue_text", content.get("content", ""))
                    })
        
        return dialogues


def main():
    example_dir = Path(__file__).parent
    rules_file = example_dir / "rules" / "dnd5e_rules.json5"
    log_file = example_dir / "logs" / "combat_log.txt"

    print("\nLoading log...")
    parser = Parser()
    parser.load_rules(str(rules_file))
    parsed_data = parser.parse_log(str(log_file))
    print(f"Done, {len(parsed_data)} in total")
    
    dice_analyzer = DiceRollAnalyzer()
    dice_stats = dice_analyzer.analyze(parsed_data)

    print(f"\nStatistics:")
    print(f"  总投掷次数: {dice_stats['total_rolls']}")
    print(f"\n  按角色统计:")
    for character, count in dice_stats['by_character'].items():
        print(f"    {character}: {count} 次")
    print(f"\n  Statistics in Dice Types:")
    for dice_type, count in dice_stats['dice_types'].items():
        print(f"    d{dice_type}: {count} times")
    
    dialogue_extractor = DialogueExtractor()
    dialogues = dialogue_extractor.extract(parsed_data)

    print(f"\nExtracted {len(dialogues)} dialogues:")
    for i, dialogue in enumerate(dialogues[:5], 1):  # Only show the first 5
        print(f"\n  [{i}] {dialogue['speaker']} ({dialogue['timestamp']})")
        print(f"      {dialogue['dialogue']}")
    
    if len(dialogues) > 5:
        print(f"\n  ... and {len(dialogues) - 5} more dialogues")

if __name__ == "__main__":
    main()
