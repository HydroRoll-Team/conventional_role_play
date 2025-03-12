class Processor:
    def __init__(self, rules):
        self.rules = rules

    def process_tokens(self, tokens):
        processed_data = []
        for token in tokens:
            processed_data.append(self.apply_rules(token))
        return processed_data

    def apply_rules(self, token):
        # Implement rule application logic here
        for rule in self.rules:
            if rule.matches(token):
                return rule.apply(token)
        return token

    def generate_output(self, processed_data, format_type):
        # Implement output generation logic based on format_type
        if format_type == 'json':
            return self.generate_json_output(processed_data)
        elif format_type == 'html':
            return self.generate_html_output(processed_data)
        elif format_type == 'markdown':
            return self.generate_markdown_output(processed_data)
        else:
            raise ValueError("Unsupported format type")

    def generate_json_output(self, processed_data):
        import json
        return json.dumps(processed_data)

    def generate_html_output(self, processed_data):
        # Implement HTML output generation
        return "<html><body>" + "".join(f"<p>{data}</p>" for data in processed_data) + "</body></html>"

    def generate_markdown_output(self, processed_data):
        # Implement Markdown output generation
        return "\n".join(f"- {data}" for data in processed_data)