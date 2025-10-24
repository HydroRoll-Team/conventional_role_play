import unittest
import json
from conventionalrp.renderers.html_renderer import HTMLRenderer
from conventionalrp.renderers.json_renderer import JSONRenderer
from conventionalrp.renderers.markdown_renderer import MarkdownRenderer


class TestRenderers(unittest.TestCase):
    def setUp(self):
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
        renderer = HTMLRenderer()
        output = renderer.render(self.sample_data)
        
        self.assertIsInstance(output, str)
        self.assertIn("<html>", output)
        self.assertIn("</html>", output)
        self.assertIn("<title>", output)
    
    def test_html_renderer_set_style(self):
        renderer = HTMLRenderer()
        renderer.set_style("custom_style")
        # now style is set, just ensure no exceptions
        self.assertIsNotNone(renderer)
    
    def test_json_renderer_basic(self):
        renderer = JSONRenderer()
        output = renderer.render(self.sample_data)
        
        self.assertIsInstance(output, str)
        
        # Output should be valid JSON
        parsed = json.loads(output)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), len(self.sample_data))
    
    def test_json_renderer_unicode(self):
        renderer = JSONRenderer()
        output = renderer.render(self.sample_data)
        
        # should preserve Chinese characters
        self.assertIn("艾莉娅", output)
        self.assertIn("测试", output)
    
    def test_markdown_renderer_basic(self):
        renderer = MarkdownRenderer()
        output = renderer.render(self.dict_data)
        
        self.assertIsInstance(output, str)
        self.assertIn("##", output)
        self.assertIn("test content", output)
    
    def test_markdown_renderer_set_style(self):
        renderer = MarkdownRenderer()
        style = {"heading_level": 2}
        renderer.set_style(style)
        self.assertEqual(renderer.style, style)
    
    def test_all_renderers_empty_data(self):
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
