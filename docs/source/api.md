# API Documentation for TRPG Log Processor

## Overview

The TRPG Log Processor SDK provides a structured way to parse, extract, and render logs from tabletop role-playing games (TRPGs). This document outlines the key components of the SDK, including classes, methods, and their functionalities.

## Core Components

### Parser

- **Class**: `Parser`
- **Module**: `src/conventionalrp/core/parser.py`
- **Methods**:
  - `parse_log(log: str) -> List[Token]`: Parses a TRPG log string and returns a list of tokens.
  - `load_rules(rules_file: str) -> None`: Loads parsing rules from a specified file.

### Processor

- **Class**: `Processor`
- **Module**: `src/conventionalrp/core/processor.py`
- **Methods**:
  - `process_tokens(tokens: List[Token]) -> None`: Processes a list of tokens.
  - `generate_output(format: str) -> str`: Generates output in the specified format (e.g., HTML, Markdown, JSON).

## Extractors

### BaseExtractor

- **Class**: `BaseExtractor`
- **Module**: `src/conventionalrp/extractors/base.py`
- **Methods**:
  - `extract(data: Any) -> Any`: Extracts relevant data based on defined rules.
  - `load_rules(rules_file: str) -> None`: Loads extraction rules from a specified file.

### RuleExtractor

- **Class**: `RuleExtractor`
- **Module**: `src/conventionalrp/extractors/rule_extractor.py`
- **Methods**:
  - `extract(data: Any) -> List[Rule]`: Extracts rules from JSON configuration files.

## Renderers

### BaseRenderer

- **Class**: `BaseRenderer`
- **Module**: `src/conventionalrp/renderers/base.py`
- **Methods**:
  - `render(data: Any) -> str`: Renders data into a specific format.
  - `set_style(style: str) -> None`: Sets the rendering style.

### HTMLRenderer

- **Class**: `HTMLRenderer`
- **Module**: `src/conventionalrp/renderers/html_renderer.py`
- **Methods**:
  - `render(data: Any) -> str`: Renders data into HTML format.

### MarkdownRenderer

- **Class**: `MarkdownRenderer`
- **Module**: `src/conventionalrp/renderers/markdown_renderer.py`
- **Methods**:
  - `render(data: Any) -> str`: Renders data into Markdown format.

### JSONRenderer

- **Class**: `JSONRenderer`
- **Module**: `src/conventionalrp/renderers/json_renderer.py`
- **Methods**:
  - `render(data: Any) -> str`: Renders data into JSON format.

## Plugins

### PluginManager

- **Class**: `PluginManager`
- **Module**: `src/conventionalrp/plugins/plugin_manager.py`
- **Methods**:
  - `load_plugins() -> None`: Loads available plugins.
  - `execute_plugin(name: str, data: Any) -> Any`: Executes a specified plugin with the provided data.

## Utilities

### Text Processing

- **Module**: `src/conventionalrp/utils/text_processing.py`
- **Functions**:
  - `tokenize(text: str) -> List[str]`: Tokenizes input text into a list of tokens.
  - `match_regex(pattern: str, text: str) -> List[str]`: Matches a regex pattern against the input text.

## Conclusion

This API documentation provides a comprehensive overview of the TRPG Log Processor SDK. For detailed usage instructions and examples, please refer to the `usage.md` file in the `docs` directory.
