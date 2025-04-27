import json5
import re
from pathlib import Path
from typing import List, Dict, Optional

class Parser:
    def __init__(self):
        self.rules = []

    def load_rules(self, rules_path: str):
        """Load parsing rules."""
        if not Path(rules_path).exists():
            raise FileNotFoundError(f"No such file or directory: {rules_path} ")

        with open(rules_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        rules = json5.loads(file_content)

        # validation rule format
        if rules is None:
            raise ValueError(f"Rule file cannot be empty.")
        # to be continue...

        self.rules = rules
        print(f"Rules loaded: {rules}\n")

    def parse_log(self, log_path: str) -> List[Dict]:
        """Parse the TRPG log based on loaded rules."""
        if not Path(log_path).exists():
            raise FileNotFoundError(f"No such file or directory: {log_path}")

        with open(log_path, "r", encoding="utf-8") as f:
            log_content = f.read().splitlines()

        parsed_data = []
        current_metadata = None
        current_content = []

        # Iterate each line of the log
        for line in log_content:
            line = line.strip()
            # pass blank line
            if not line:
                continue

            # Check for metadata
            metadata_match = self._match_metadata(line)
            if metadata_match:
                if current_metadata:
                    parsed_data.append({
                        **current_metadata,
                        "content": current_content
                    })
                    current_content = []
                current_metadata = metadata_match
                continue

            # Parse content
            if current_metadata:
                parsed_segments = self._parse_line_content(line)
                current_content.extend(parsed_segments)

        # Add the last entry
        if current_metadata:
            parsed_data.append({
                **current_metadata,
                "content": current_content
            })

        return parsed_data

    def _match_metadata(self, line: str) -> Optional[Dict]:
        """Match metadata line."""
        metadata_rule = self.rules.get("metadata")
        if not metadata_rule:
            return None

        for pattern in metadata_rule.get("patterns", []):
            match = re.match(pattern, line)
            if match:
                metadata = {"type": "metadata"}
                for i, key in enumerate(metadata_rule.get("groups", [])):
                    if i + 1 <= len(match.groups()):
                        metadata[key] = match.group(i + 1).strip()
                return metadata
        return None

    def _parse_line_content(self, line: str) -> List[Dict]:
        """Parse a single line of content recursively."""
        if not line:
            return []

        # Sort rules by priority (highest first)
        content_rules = sorted(
            self.rules.get("content", []),
            key=lambda x: x.get("priority", 0),
            reverse=True
        )

        for rule in content_rules:
            for pattern in rule["patterns"]:
                match = re.search(pattern, line)
                if match:
                    # Handle different match types
                    if rule["match_type"] == "enclosed":
                        return self._handle_enclosed_match(line, match, rule)
                    elif rule["match_type"] == "prefix":
                        return self._handle_prefix_match(line, match, rule)
                    elif rule["match_type"] == "suffix":
                        return self._handle_suffix_match(line, match, rule)

        # If no matches found, return as unknown
        return [{"type": "unknown", "content": line}]

    def _handle_enclosed_match(self, line: str, match: re.Match, rule: Dict) -> List[Dict]:
        """Handle enclosed matches (highest priority)."""
        before = line[:match.start()].strip()
        matched = match.group(0).strip()
        after = line[match.end():].strip()

        result = []
        if before:
            result.extend(self._parse_line_content(before))
        
        entry = {"type": rule["type"], "content": matched}
        for i, group in enumerate(rule.get("groups", [])):
            if i + 1 <= len(match.groups()):
                entry[group] = match.group(i + 1).strip() if match.group(i + 1) else ""
        result.append(entry)
        
        if after:
            result.extend(self._parse_line_content(after))
        
        return result

    def _handle_prefix_match(self, line: str, match: re.Match, rule: Dict) -> List[Dict]:
        """Handle prefix matches."""
        matched = line[match.start():].strip()
        before = line[:match.start()].strip()

        result = []
        if before:
            result.extend(self._parse_line_content(before))
        
        entry = {"type": rule["type"], "content": matched}
        for i, group in enumerate(rule.get("groups", [])):
            if i + 1 <= len(match.groups()):
                entry[group] = match.group(i + 1).strip() if match.group(i + 1) else ""
        result.append(entry)
        
        return result

    def _handle_suffix_match(self, line: str, match: re.Match, rule: Dict) -> List[Dict]:
        """Handle suffix matches."""
        matched = line[:match.end()].strip()
        after = line[match.end():].strip()

        entry = {"type": rule["type"], "content": matched}
        for i, group in enumerate(rule.get("groups", [])):
            if i + 1 <= len(match.groups()):
                entry[group] = match.group(i + 1).strip() if match.group(i + 1) else ""
        
        result = [entry]
        if after:
            result.extend(self._parse_line_content(after))
        
        return result