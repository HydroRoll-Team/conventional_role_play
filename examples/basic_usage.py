from trpg_log_processor.core.parser import Parser
from trpg_log_processor.core.processor import Processor
from trpg_log_processor.extractors.rule_extractor import RuleExtractor
from trpg_log_processor.renderers.html_renderer import HTMLRenderer

def main():
    # Initialize the parser and load rules
    parser = Parser()
    parser.load_rules('path/to/rules.json')

    # Parse the TRPG log
    log_data = "Your TRPG log data here"
    parsed_tokens = parser.parse_log(log_data)

    # Initialize the rule extractor
    extractor = RuleExtractor()
    rules = extractor.extract('path/to/rules.json')

    # Process the parsed tokens
    processor = Processor()
    processed_data = processor.process_tokens(parsed_tokens, rules)

    # Render the output in HTML format
    renderer = HTMLRenderer()
    output = renderer.render(processed_data)

    # Print or save the output
    print(output)

if __name__ == "__main__":
    main()