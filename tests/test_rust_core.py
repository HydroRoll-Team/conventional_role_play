import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from conventionalrp import _core

def test_token():
    token = _core.Token("dialogue", "「你好世界」")
    token.add_metadata("speaker", "艾莉娅")
    token.add_metadata("timestamp", "2025-10-24 14:30:01")
    
    print(f"Token: {token}")
    print(f"Type: {token.token_type}")
    print(f"Content: {token.content}")
    print(f"Speaker: {token.get_metadata('speaker')}")
    print(f"Dict: {token.to_dict()}")


def test_regex_rule():
    rule = _core.RegexRule(r"\[d(\d+)\s*=\s*(\d+)\]", "dice_roll", 90)
    
    text = "检定结果: [d20 = 18]"
    print(f"Text: {text}")
    print(f"Matches: {rule.matches(text)}")
    print(f"Extracted: {rule.extract(text)}")
    print(f"Find all: {rule.find_all(text)}")


def test_text_parser():
    parser = _core.TextParser()
    
    parser.add_rule(r"\[d(\d+)\s*=\s*(\d+)\]", "dice_roll", 90)
    parser.add_rule(r"「(.+?)」", "dialogue", 80)
    parser.add_rule(r"\*\*(.+?)\*\*", "action", 70)
    
    print(f"规则数量: {parser.rule_count()}")
    
    line = "艾莉娅说「我要投掷」然后 **投掷骰子** 结果是 [d20 = 18]"
    print(f"\n解析文本: {line}")
    result = parser.parse_line(line)
    print(f"解析结果: {result}")
    
    lines = [
        "「你好」",
        "**挥剑** [d20 = 15]",
        "普通文本"
    ]
    results = parser.parse_lines(lines)
    for i, line_result in enumerate(results):
        print(f"  行 {i+1}: {line_result}")


def test_fast_matcher():
    patterns = ["骰子", "投掷", "检定"]
    matcher = _core.FastMatcher(patterns)
    
    text = "艾莉娅进行投掷骰子检定"
    print(f"Text: {text}")
    print(f"Contains any: {matcher.contains_any(text)}")
    print(f"Find matches: {matcher.find_matches(text)}")
    print(f"Count matches: {matcher.count_matches(text)}")


def benchmark_parser():
    import time
    
    parser = _core.TextParser()
    parser.add_rule(r"\[d(\d+)\s*=\s*(\d+)\]", "dice_roll", 90)
    parser.add_rule(r"「(.+?)」", "dialogue", 80)
    parser.add_rule(r"\*\*(.+?)\*\*", "action", 70)
    
    test_lines = [
        "「你好」**挥剑** [d20 = 15]" for _ in range(1000)
    ]
    
    start = time.time()
    results = parser.parse_lines(test_lines)
    elapsed = time.time() - start
    
    print(f"Process {len(test_lines)} lines")
    print(f"time: {elapsed:.4f} s")
    print(f"speed: {len(test_lines)/elapsed:.0f} lines/s")


if __name__ == "__main__":
    try:
        test_token()
        test_regex_rule()
        test_text_parser()
        test_fast_matcher()
        benchmark_parser()
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
