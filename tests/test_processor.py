import unittest
from conventionalrp.core.processor import Processor


class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = Processor()
        self.sample_tokens = [
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
    
    def test_init_without_rules(self):
        processor = Processor()
        self.assertEqual(processor.rules, {})
    
    def test_init_with_rules(self):
        rules = {"test_rule": "value"}
        processor = Processor(rules)
        self.assertEqual(processor.rules, rules)
    
    def test_process_tokens(self):
        result = self.processor.process_tokens(self.sample_tokens)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(self.sample_tokens))
        
        # Check processing marks
        for token in result:
            if "timestamp" in token:
                self.assertTrue(token.get("processed"))
    
    def test_apply_rules(self):
        token = self.sample_tokens[0]
        result = self.processor.apply_rules(token)
        
        self.assertIsInstance(result, dict)
        self.assertIn("timestamp", result)
        self.assertTrue(result.get("processed"))
    
    def test_generate_json_output(self):
        output = self.processor.generate_json_output(self.sample_tokens)
        
        self.assertIsInstance(output, str)
        self.assertIn("timestamp", output)
        self.assertIn("speaker", output)
    
    def test_generate_html_output(self):
        output = self.processor.generate_html_output(self.sample_tokens)
        
        self.assertIsInstance(output, str)
        self.assertIn("<html>", output)
        self.assertIn("</html>", output)
    
    def test_generate_markdown_output(self):
        output = self.processor.generate_markdown_output(self.sample_tokens)
        
        self.assertIsInstance(output, str)
        self.assertIn("-", output)
    
    def test_generate_output_json(self):
        output = self.processor.generate_output(self.sample_tokens, "json")
        self.assertIsInstance(output, str)
    
    def test_generate_output_html(self):
        output = self.processor.generate_output(self.sample_tokens, "html")
        output = self.processor.generate_output(self.sample_tokens, "html")
        self.assertIsInstance(output, str)
    
    def test_generate_output_markdown(self):
        output = self.processor.generate_output(self.sample_tokens, "markdown")
        self.assertIsInstance(output, str)
    
    def test_generate_output_unsupported_format(self):
        with self.assertRaises(ValueError) as context:
            self.processor.generate_output(self.sample_tokens, "pdf")
        
        self.assertIn("Unsupported format type", str(context.exception))


if __name__ == "__main__":
    unittest.main()
