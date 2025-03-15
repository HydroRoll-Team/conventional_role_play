import json5
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

        rules = json5.loads(file_content)

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

        current_metadata = None
        current_content = []

        # Iterate each line of the log
        for line in log_content:
            # pass blank line
            if not line.strip():
                continue

            # metadata detect
            is_metadata = False
            for rule in self.rules:
                if rule.get("type") == "metadata":
                    patterns = rule.get("patterns", [])
                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            # If it's metadata, save the previous content
                            if current_metadata:
                                parsed_data.append({
                                    **current_metadata,
                                    "content": current_content
                                })
                                current_content = []

                            # Parsing new metadata
                            current_metadata = {}
                            groups = rule.get("groups", [])
                            for i, key in enumerate(groups):
                                if i + 1 <= len(match.groups()):  # Ensure effective
                                    current_metadata[key] = match.group(i + 1).strip()
                            is_metadata = True
                            break
                    if is_metadata:
                        break

            if is_metadata:
                continue  # The metadata line has been processed, skip subsequent content matching

            # content detect
            remaining_line = line
            while remaining_line:
                matched = False
                for rule in self.rules:
                    # pass metadata rule
                    if rule["type"] == "metadata":
                        continue

                    for pattern in rule["patterns"]:
                        match = re.match(pattern, remaining_line)
                        if match:
                            # If the matching content is not the beginning, it means that there is unknown content in front of it
                            if match.start() > 0:
                                current_content.append({
                                    "type": "unknown",
                                    "content": remaining_line[:match.start()]
                                })
                            
                            # Extract matched content
                            entry = {"type": rule["type"], "content": match.group(0)}
                            for i, group in enumerate(rule["groups"]):
                                entry[group] = match.group(i+1).strip() if match.group(i+1) else ""
                            
                            current_content.append(entry)
                            remaining_line = remaining_line[match.end():].lstrip()
                            matched = True
                            break
                    if matched:
                        break
                
                if not matched:
                    current_content.append({
                        "type": "unknown",
                        "content": remaining_line
                    })
                    remaining_line = ""

        # Process the last line
        if current_metadata:
            parsed_data.append({
                **current_metadata,
                "content": current_content
            })

        return parsed_data