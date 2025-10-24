#!/usr/bin/env python3
"""
RuleExtractor 模块单元测试
"""

import unittest
import tempfile
import json5
from pathlib import Path
from conventionalrp.extractors.rule_extractor import RuleExtractor


class TestRuleExtractor(unittest.TestCase):
    """RuleExtractor 类的单元测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时规则文件
        self.temp_rules = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json5',
            delete=False,
            encoding='utf-8'
        )
        self.temp_rules.write('''{
            test_rule: "test_value",
            metadata: [{type: "test"}],
            content: [{type: "test_content"}]
        }''')
        self.temp_rules.close()
    
    def tearDown(self):
        """清理测试环境"""
        Path(self.temp_rules.name).unlink(missing_ok=True)
    
    def test_init_without_file(self):
        """测试不带配置文件的初始化"""
        extractor = RuleExtractor()
        self.assertEqual(extractor.rules, {})
        self.assertIsNone(extractor.config_file)
    
    def test_init_with_file(self):
        """测试带配置文件的初始化"""
        extractor = RuleExtractor(self.temp_rules.name)
        self.assertIsNotNone(extractor.rules)
        self.assertIn("test_rule", extractor.rules)
    
    def test_load_rules_from_file_success(self):
        """测试成功加载规则文件"""
        extractor = RuleExtractor()
        rules = extractor.load_rules_from_file(self.temp_rules.name)
        
        self.assertIsInstance(rules, dict)
        self.assertIn("test_rule", rules)
        self.assertEqual(rules["test_rule"], "test_value")
    
    def test_load_rules_from_file_not_found(self):
        """测试加载不存在的文件"""
        extractor = RuleExtractor()
        with self.assertRaises(FileNotFoundError):
            extractor.load_rules_from_file("nonexistent.json5")
    
    def test_load_rules_empty_file(self):
        """测试加载空文件"""
        empty_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json5',
            delete=False,
            encoding='utf-8'
        )
        empty_file.write('')
        empty_file.close()
        
        try:
            extractor = RuleExtractor()
            with self.assertRaises(ValueError):
                extractor.load_rules_from_file(empty_file.name)
        finally:
            Path(empty_file.name).unlink(missing_ok=True)
    
    def test_load_rules_method(self):
        """测试 load_rules 方法"""
        extractor = RuleExtractor()
        rules = extractor.load_rules(self.temp_rules.name)
        
        self.assertIsInstance(rules, dict)
        self.assertEqual(extractor.rules, rules)
    
    def test_extract_method(self):
        """测试 extract 方法"""
        extractor = RuleExtractor(self.temp_rules.name)
        extracted = extractor.extract()
        
        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, extractor.rules)


if __name__ == "__main__":
    unittest.main()
