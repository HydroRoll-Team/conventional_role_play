# Usage Instructions for TRPG Log Processor

## Overview

The TRPG Log Processor is a Python SDK designed for structured processing of tabletop role-playing game (TRPG) logs. It provides functionalities for parsing logs, extracting rules, and rendering outputs in multiple formats.

## Installation

To install the TRPG Log Processor, you can use pip:

```bash
pip install conventionalrp
```

## Basic Usage

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

## Features

- **Rule Extraction**: Easily extract rules from JSON configuration files using the `RuleExtractor`.
- **Multi-format Rendering**: Render outputs in various formats such as HTML, Markdown, and JSON using the respective renderer classes.
- **Extensibility**: Create custom plugins to extend the functionality of the SDK.

## Custom Plugins

To create a custom plugin, you can follow the example provided in `examples/custom_plugin.py`. This allows you to add additional processing or rendering capabilities tailored to your needs.

## Documentation

For more detailed information on the API and available classes, please refer to the [API documentation](api.md).
