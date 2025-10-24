#!/usr/bin/env python3
"""
Parser 模块单元测试
"""

import unittest
import tempfile
from pathlib import Path
from conventionalrp.core.parser import Parser


class TestParser(unittest.TestCase):
    """Parser 类的单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.parser = Parser()
        
        # 创建临时规则文件
        self.temp_rules = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json5', 
            delete=False,
            encoding='utf-8'
        )
        self.temp_rules.write('''{
            metadata: [{
                type: "metadata",
                patterns: ["^\\\\[(.+?)\\\\]\\\\s*<(.+?)>\\\\s*(.*)$"],
                groups: ["timestamp", "speaker", "content"],
                priority: 100
            }],
            content: [
                {
                    type: "dice_roll",
                    match_type: "enclosed",
                    patterns: ["\\\\[d(\\\\d+)\\\\s*=\\\\s*(\\\\d+)\\\\]"],
                    groups: ["dice_type", "result"],
                    priority: 90
                },
                {
                    type: "dialogue",
                    match_type: "enclosed",
                    patterns: ["「(.+?)」"],
                    groups: ["dialogue_text"],
                    priority: 60
                },
                {
                    type: "text",
                    match_type: "prefix",
                    patterns: ["^(.+)$"],
                    groups: ["text_content"],
                    priority: 1
                }
            ]
        }''')
        self.temp_rules.close()
        
        # 创建临时日志文件
        self.temp_log = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        )
        self.temp_log.write('''[2025-10-24 14:30:01] <艾莉娅> 「我要检查这扇门」
[2025-10-24 14:30:05] <DiceBot> 检定结果: [d20 = 18]
[2025-10-24 14:30:10] <DM> 你发现了陷阱
''')
        self.temp_log.close()
    
    def tearDown(self):
        """清理测试环境"""
        Path(self.temp_rules.name).unlink(missing_ok=True)
        Path(self.temp_log.name).unlink(missing_ok=True)
    
    def test_load_rules_success(self):
        """测试成功加载规则文件"""
        self.parser.load_rules(self.temp_rules.name)
        self.assertIn("metadata", self.parser.rules)
        self.assertIn("content", self.parser.rules)
    
    def test_load_rules_file_not_found(self):
        """测试加载不存在的规则文件"""
        with self.assertRaises(FileNotFoundError):
            self.parser.load_rules("nonexistent_file.json5")
    
    def test_parse_log_success(self):
        """测试成功解析日志"""
        self.parser.load_rules(self.temp_rules.name)
        result = self.parser.parse_log(self.temp_log.name)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # 检查第一条记录
        first_entry = result[0]
        self.assertIn("timestamp", first_entry)
        self.assertIn("speaker", first_entry)
        self.assertIn("content", first_entry)
        self.assertEqual(first_entry["speaker"], "艾莉娅")
    
    def test_parse_log_file_not_found(self):
        """测试解析不存在的日志文件"""
        self.parser.load_rules(self.temp_rules.name)
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_log("nonexistent_log.txt")
    
    def test_match_metadata(self):
        """测试元数据匹配"""
        self.parser.load_rules(self.temp_rules.name)
        line = "[2025-10-24 14:30:01] <艾莉娅> 测试内容"
        result = self.parser._match_metadata(line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "metadata")
        self.assertEqual(result["timestamp"], "2025-10-24 14:30:01")
        self.assertEqual(result["speaker"], "艾莉娅")
    
    def test_parse_line_content_dialogue(self):
        """测试解析对话内容"""
        self.parser.load_rules(self.temp_rules.name)
        line = "「这是一段对话」"
        result = self.parser._parse_line_content(line)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result[0]["type"], "dialogue")
    
    def test_parse_line_content_dice_roll(self):
        """测试解析骰子投掷"""
        self.parser.load_rules(self.temp_rules.name)
        line = "检定结果: [d20 = 18]"
        result = self.parser._parse_line_content(line)
        
        # 应该包含文本和骰子投掷
        dice_tokens = [t for t in result if t["type"] == "dice_roll"]
        self.assertGreater(len(dice_tokens), 0)


if __name__ == "__main__":
    unittest.main()
