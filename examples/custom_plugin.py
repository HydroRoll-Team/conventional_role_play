#!/usr/bin/env python3
"""
自定义插件示例
演示如何创建和使用自定义插件来扩展 ConventionalRP 的功能
"""

import sys
from typing import List, Dict, Any
from pathlib import Path

# 添加 src 目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from conventionalrp.core.parser import Parser
from conventionalrp.core.processor import Processor


class DiceRollAnalyzer:
    """骰子统计分析插件"""
    
    def __init__(self):
        self.name = "Dice Roll Analyzer"
        
    def analyze(self, parsed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析日志中的所有骰子投掷
        
        Args:
            parsed_data: 解析后的日志数据
            
        Returns:
            统计结果
        """
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
        """
        提取所有角色对话
        
        Args:
            parsed_data: 解析后的日志数据
            
        Returns:
            对话列表
        """
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
    print("=" * 60)
    print("ConventionalRP 自定义插件示例")
    print("=" * 60)
    
    # 准备数据
    example_dir = Path(__file__).parent
    rules_file = example_dir / "rules" / "dnd5e_rules.json5"
    log_file = example_dir / "logs" / "combat_log.txt"
    
    print("\n[1] 解析日志...")
    parser = Parser()
    parser.load_rules(str(rules_file))
    parsed_data = parser.parse_log(str(log_file))
    print(f"✓ 解析完成，共 {len(parsed_data)} 条记录")
    
    # 使用骰子分析插件
    print("\n[2] 运行骰子统计分析插件...")
    dice_analyzer = DiceRollAnalyzer()
    dice_stats = dice_analyzer.analyze(parsed_data)
    
    print(f"\n骰子统计结果:")
    print(f"  总投掷次数: {dice_stats['total_rolls']}")
    print(f"\n  按角色统计:")
    for character, count in dice_stats['by_character'].items():
        print(f"    {character}: {count} 次")
    print(f"\n  按骰子类型统计:")
    for dice_type, count in dice_stats['dice_types'].items():
        print(f"    d{dice_type}: {count} 次")
    
    # 使用对话提取插件
    print("\n[3] 运行对话提取插件...")
    dialogue_extractor = DialogueExtractor()
    dialogues = dialogue_extractor.extract(parsed_data)
    
    print(f"\n提取到 {len(dialogues)} 条对话:")
    for i, dialogue in enumerate(dialogues[:5], 1):  # 只显示前5条
        print(f"\n  [{i}] {dialogue['speaker']} ({dialogue['timestamp']})")
        print(f"      {dialogue['dialogue']}")
    
    if len(dialogues) > 5:
        print(f"\n  ... 还有 {len(dialogues) - 5} 条对话")
    
    print("\n" + "=" * 60)
    print("✓ 插件演示完成！")
    print("=" * 60)
    print("\n提示: 你可以创建自己的插件来实现:")
    print("  - 战斗统计分析")
    print("  - 角色行为分析")
    print("  - 关键词提取")
    print("  - 情感分析")
    print("  - 自动摘要生成")
    print("  - ... 以及更多!")


if __name__ == "__main__":
    main()
