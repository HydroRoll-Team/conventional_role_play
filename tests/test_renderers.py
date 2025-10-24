#!/usr/bin/env python3
"""
Renderers 模块单元测试
"""

import unittest
import json
from conventionalrp.renderers.html_renderer import HTMLRenderer
from conventionalrp.renderers.json_renderer import JSONRenderer
from conventionalrp.renderers.markdown_renderer import MarkdownRenderer


class TestRenderers(unittest.TestCase):
    """测试所有渲染器"""
    
    def setUp(self):
        """设置测试数据"""
        self.sample_data = [
            {
                "type": "metadata",
                "timestamp": "2025-10-24 14:30:01",
                "speaker": "艾莉娅",
                "content": [
                    {"type": "dialogue", "content": "「测试对话」"}
                ]
            },
            {
                "type": "metadata",
                "timestamp": "2025-10-24 14:30:05",
                "speaker": "DM",
                "content": [
                    {"type": "text", "content": "测试文本"}
                ]
            }
        ]
        
        self.dict_data = {
            "title": "测试标题",
            "content": "测试内容"
        }
    
    def test_html_renderer_basic(self):
        """测试 HTML 渲染器基本功能"""
        renderer = HTMLRenderer()
        output = renderer.render(self.sample_data)
        
        self.assertIsInstance(output, str)
        self.assertIn("<html>", output)
        self.assertIn("</html>", output)
        self.assertIn("<title>", output)
    
    def test_html_renderer_set_style(self):
        """测试 HTML 渲染器设置样式"""
        renderer = HTMLRenderer()
        renderer.set_style("custom_style")
        # 当前实现为占位符，仅测试不抛出异常
        self.assertIsNotNone(renderer)
    
    def test_json_renderer_basic(self):
        """测试 JSON 渲染器基本功能"""
        renderer = JSONRenderer()
        output = renderer.render(self.sample_data)
        
        self.assertIsInstance(output, str)
        
        # 验证输出是有效的 JSON
        parsed = json.loads(output)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), len(self.sample_data))
    
    def test_json_renderer_unicode(self):
        """测试 JSON 渲染器处理 Unicode"""
        renderer = JSONRenderer()
        output = renderer.render(self.sample_data)
        
        # 应该保留中文字符
        self.assertIn("艾莉娅", output)
        self.assertIn("测试", output)
    
    def test_markdown_renderer_basic(self):
        """测试 Markdown 渲染器基本功能"""
        renderer = MarkdownRenderer()
        output = renderer.render(self.dict_data)
        
        self.assertIsInstance(output, str)
        self.assertIn("##", output)  # 应该有标题标记
        self.assertIn("测试标题", output)
    
    def test_markdown_renderer_set_style(self):
        """测试 Markdown 渲染器设置样式"""
        renderer = MarkdownRenderer()
        style = {"heading_level": 2}
        renderer.set_style(style)
        self.assertEqual(renderer.style, style)
    
    def test_all_renderers_empty_data(self):
        """测试所有渲染器处理空数据"""
        empty_data = []
        
        html_renderer = HTMLRenderer()
        html_output = html_renderer.render(empty_data)
        self.assertIsInstance(html_output, str)
        
        json_renderer = JSONRenderer()
        json_output = json_renderer.render(empty_data)
        self.assertEqual(json_output, "[]")
        
        md_renderer = MarkdownRenderer()
        md_output = md_renderer.render({})
        self.assertEqual(md_output, "")


if __name__ == "__main__":
    unittest.main()
