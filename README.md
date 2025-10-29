# Conventional Role Play

## Overview

Conventional Role Play (CVRP) is a Python SDK designed for structured processing of tabletop role-playing game (TRPG) logs. It provides functionalities for parsing logs, extracting rules, and rendering outputs in multiple formats. This SDK aims to streamline the analysis and presentation of TRPG session data.

> **Note**  
> This documentation is still under construction. Contributions are welcome! See contributing for more information.

## Key Features

* **Rule Extraction**: Easily extract rules from JSON configuration files using the `RuleExtractor` class.
* **Multi-format Rendering**: Render outputs in various formats such as HTML, Markdown, and JSON using the respective renderer classes (e.g., `HTMLRenderer`).
* **THULAC Smart Parser**: 🆕 Intelligent parsing using Tsinghua THULAC (THU Lexical Analyzer for Chinese) for automatic content recognition with minimal configuration. See [THULAC Parser Documentation](docs/THULAC_PARSER.md).
* **Extensibility**: Create custom plugins to extend the functionality of the SDK. See custom-plugins for details.
* **Comprehensive API**: Full API documentation available for all modules and classes. See api-documentation.

## Installation

To install Conventional Role Play, you can use pip:

```bash
pip install conventionalrp
```

## Basic Usage

### Traditional Parser (Regex-based)

Here is a simple example of how to use the TRPG Log Processor:

```python
from conventionalrp.core.parser import Parser
from conventionalrp.core.processor import Processor
from conventionalrp.extractors.rule_extractor import RuleExtractor
from conventionalrp.renderers.html_renderer import HTMLRenderer

# Step 1: Load rules
rule_extractor = RuleExtractor()
rules = rule_extractor.load_rules('path/to/rules.json')

# Step 2: Parse the log
parser = Parser(rules)
parsed_log = parser.parse_log('path/to/log.txt')

# Step 3: Process the parsed tokens
processor = Processor()
output = processor.process_tokens(parsed_log)

# Step 4: Render the output
renderer = HTMLRenderer()
html_output = renderer.render(output)

# Save or display the output
with open('output.html', 'w') as f:
    f.write(html_output)
```

### THULAC Smart Parser

Simplified parsing with automatic content recognition:

```python
from conventionalrp.core.thulac_parser import THULACParser

# Step 1: Create parser
parser = THULACParser(seg_only=False)

# Step 2: Load simplified rules (just delimiters!)
parser.load_rules('examples/rules/thulac_rules.json5')

# Step 3: Parse a line
text = '[15:30] <Alice> "Hello!"（waves）'
result = parser.parse_line(text)

# Result:
# {
#   "metadata": {"timestamp": "15:30", "speaker": "Alice"},
#   "content": [
#     {"type": "dialogue", "content": "Hello!", "confidence": 1.0},
#     {"type": "action", "content": "waves", "confidence": 1.0}
#   ]
# }

# Step 4: Parse entire log file
results = parser.parse_log('path/to/log.txt')
stats = parser.get_statistics()
print(f"Parsed {stats['total_parsed']} lines")
```

## Custom Plugins

To create a custom plugin, you can follow the example provided in 

custom_plugin.py

. This allows you to add additional processing or rendering capabilities tailored to your needs.

## API Documentation

For more detailed information on the API and available classes, please refer to the [API documentation](https://crp.hydroroll.team/api.html).

## License

This project is licensed under the AGPLv3.0 License - see the 

LICENSE

 file for details.

## Project Links

* [Homepage](https://hydroroll.team/)
* [Documentation](https://crp.hydroroll.team/)
* [GitHub Repository](https://github.com/HydroRoll-Team/conventional_role_play)