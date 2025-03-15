import json
import re
from pathlib import Path


class Parser:
    def __init__(self):
        self.rules = []

    def load_rules(self, rules_path: str):
        """Load parsing rules."""
        if not Path(rules_path).exists():
            raise FileNotFoundError(f"No such file or directory: {rules_path} ")

        with open(rules_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        rules = json.loads(file_content)

        # validation rule format
        if rules is None:
            raise ValueError(f"Rule file cannot be empty.")
        # to be continue...

        self.rules = rules

    def parse_log(self, log_path: str):
        """Parse the TRPG log based on loaded rules."""
        parsed_data = []

        if not Path(log_path).exists():
            raise FileNotFoundError(f"No such file or directory: {log_path} ")

        with open(log_path, "r", encoding="utf-8") as f:
            log_content = f.read().splitlines()

        # Iterate each line of the log
        for line in log_content:
            # pass blank line
            if not line.strip():
                continue

            # try to match the current line by rules
            for rule in self.rules:
                pattern = rule.get("pattern")
                rule_type = rule.get("type")
                match = re.search(pattern, line)
                if match:
                    # matched
                    content = match.group(1).strip()
                    parsed_data.append({"content": content, "type": rule_type})
                    break
            # no matched, marked as an unknown type
            else:
                parsed_data.append({"content": line.strip(), "type": "unknown"})

        return parsed_data
