import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from conventionalrp.core.rules import Rule, RuleEngine
from conventionalrp.core.processor import Processor


def example_1_simple_rules():
    rule = Rule(
        name="tag_dice_rolls",
        condition={"type": "dice_roll"},
        action={"type": "add_tag", "tag": "game_mechanics"},
        priority=100
    )
    
    engine = RuleEngine()
    engine.add_rule(rule)
    
    data = {"type": "dice_roll", "content": "[d20 = 18]"}
    
    print(f"Original data: {data}")
    result = engine.process(data)
    print(f"Processed result: {result}")
    print()


def example_2_conditional_rules():
    engine = RuleEngine()
    
    # Rule1: High rolls (>=15) get "success" tag
    engine.add_rule_dict(
        name="high_roll",
        condition={
            "type": "dice_roll",
            "result": {"type": "greater_than", "value": 15}
        },
        action={"type": "add_tag", "tag": "success"},
        priority=100
    )
    
    # Rule2: Low rolls (<10) get "failure" tag
    engine.add_rule_dict(
        name="low_roll",
        condition={
            "type": "dice_roll",
            "result": {"type": "less_than", "value": 10}
        },
        action={"type": "add_tag", "tag": "failure"},
        priority=100
    )
    
    test_cases = [
        {"type": "dice_roll", "result": 18, "content": "[d20 = 18]"},
        {"type": "dice_roll", "result": 5, "content": "[d20 = 5]"},
        {"type": "dice_roll", "result": 12, "content": "[d20 = 12]"},
    ]
    
    for data in test_cases:
        result = engine.process(data)
        print(f"结果: {data['result']} -> 标签: {result.get('tags', [])}")
    print()


def example_3_field_transformation():
    engine = RuleEngine()

    # Rule: Normalize speaker names
    engine.add_rule_dict(
        name="normalize_speaker",
        condition={"type": "metadata"},
        action={
            "type": "transform",
            "field": "speaker",
            "function": "upper"
        },
        priority=90
    )
    
    data = {
        "type": "metadata",
        "speaker": "艾莉娅",
        "timestamp": "2025-10-24 14:30:01"
    }

    print(f"Original data: {data}")
    result = engine.process(data)
    print(f"Processed result: {result}")
    print()


def example_4_processor_with_rules():
    processor = Processor()
    
    # Add rule: Highlight important dialogues
    processor.add_rule(Rule(
        name="highlight_important_dialogue",
        condition={
            "type": "dialogue",
            "content": {"type": "contains", "value": "重要"}
        },
        action={"type": "add_tag", "tag": "important"},
        priority=100
    ))
    
    # Add rule: Mark all metadata as processed
    processor.add_rule(Rule(
        name="mark_metadata",
        condition={"type": "metadata"},
        action={"type": "set_field", "field": "processed_by", "value": "rule_engine"},
        priority=90
    ))
    
    tokens = [
        {"type": "metadata", "speaker": "DM", "timestamp": "2025-10-24"},
        {"type": "dialogue", "content": "这是重要的线索"},
        {"type": "dialogue", "content": "普通对话"},
        {"type": "dice_roll", "result": 20},
    ]

    print(f"Processing {len(tokens)} tokens...")
    results = processor.process_tokens(tokens)
    
    for i, result in enumerate(results):
        print(f"  [{i+1}] {result.get('type')}: "
              f"Tags={result.get('tags', [])} "
              f"Processed by={result.get('processed_by', 'N/A')}")
    print()


def example_5_custom_processor():
    processor = Processor()

    # Custom processing function: Count characters
    def add_char_count(data):
        if "content" in data:
            data["char_count"] = len(data["content"])
        return data

    # Custom processing function: Ensure timestamp exists
    def ensure_timestamp(data):
        if "timestamp" not in data:
            from datetime import datetime
            data["timestamp"] = datetime.now().isoformat()
        return data
    
    processor.add_processor(add_char_count)
    processor.add_processor(ensure_timestamp)
    
    test_data = [
        {"type": "dialogue", "content": "你好世界"},
        {"type": "text", "content": "这是一段很长的文本内容"},
    ]
    
    results = processor.process_tokens(test_data)
    
    for result in results:
        print(f"  {result.get('type')}: "
              f"Character count={result.get('char_count')} "
              f"Timestamp={result.get('timestamp', 'N/A')[:19]}")
    print()


def example_6_priority_and_order():
    engine = RuleEngine()

    engine.add_rule_dict(
        name="low_priority",
        condition={"type": "test"},
        action={"type": "set_field", "field": "processed_by", "value": "low"},
        priority=10
    )
    
    engine.add_rule_dict(
        name="high_priority",
        condition={"type": "test"},
        action={"type": "set_field", "field": "processed_by", "value": "high"},
        priority=100
    )
    
    engine.add_rule_dict(
        name="medium_priority",
        condition={"type": "test"},
        action={"type": "set_field", "field": "processed_by", "value": "medium"},
        priority=50
    )
    
    data = {"type": "test"}
    
    result1 = engine.process(data, apply_all=False)
    print(f"Only apply the highest priority matching rule: {result1}")

    result2 = engine.process(data, apply_all=True)
    print(f"Apply all matching rules: {result2}")
    print()


def main():
    example_1_simple_rules()
    example_2_conditional_rules()
    example_3_field_transformation()
    example_4_processor_with_rules()
    example_5_custom_processor()
    example_6_priority_and_order()


if __name__ == "__main__":
    main()
