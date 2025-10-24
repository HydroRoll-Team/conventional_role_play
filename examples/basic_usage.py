import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from conventionalrp.core.parser import Parser
from conventionalrp.core.processor import Processor
from conventionalrp.extractors.rule_extractor import RuleExtractor
from conventionalrp.renderers.html_renderer import HTMLRenderer
from conventionalrp.renderers.json_renderer import JSONRenderer
from conventionalrp.renderers.markdown_renderer import MarkdownRenderer

def main(): 
    example_dir = Path(__file__).parent
    rules_file = example_dir / "rules" / "dnd5e_rules.json5"
    log_file = example_dir / "logs" / "sample_session.txt"

    parser = Parser()
    parser.load_rules(str(rules_file))
    print(f"Rule loaded: {rules_file.name}")
    
    parsed_data = parser.parse_log(str(log_file))
    print(f"Log parsed successfully, {len(parsed_data)} entries found.")
    
    processor = Processor()
    processed_data = processor.process_tokens(parsed_data)
    print(f"Done processing data")

    # JSON 格式
    json_renderer = JSONRenderer()
    json_output = json_renderer.render(processed_data)
    json_file = example_dir / "output" / "session_output.json"
    json_file.parent.mkdir(exist_ok=True)
    with open(json_file, "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"Json: {json_file}")
    
    # HTML 格式
    html_renderer = HTMLRenderer()
    html_output = html_renderer.render(processed_data)
    html_file = example_dir / "output" / "session_output.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"HTML: {html_file}")
    
    md_renderer = MarkdownRenderer()
    md_output = md_renderer.render(processed_data)
    md_file = example_dir / "output" / "session_output.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_output)
    print(f"Markdown: {md_file}")

if __name__ == "__main__":
    main()
