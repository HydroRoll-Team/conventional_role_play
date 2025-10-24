import json5
from pathlib import Path
from typing import Dict, Any, Optional


class BaseExtractor:
    def extract(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def load_rules(self, rules):
        raise NotImplementedError("This method should be overridden by subclasses.")


class RuleExtractor(BaseExtractor):
    """规则提取器，用于从配置文件加载解析规则"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.rules: Dict[str, Any] = {}
        if config_file:
            self.rules = self.load_rules_from_file(config_file)

    def load_rules_from_file(self, config_file: str) -> Dict[str, Any]:
        """
        从文件加载规则
        """
        if not Path(config_file).exists():
            raise FileNotFoundError(f"Rule file not found: {config_file}")
            
        with open(config_file, "r", encoding="utf-8") as file:
            content = file.read()
            
        rules = json5.loads(content)
        
        if not rules:
            raise ValueError("Rule file cannot be empty")
            
        return rules

    def load_rules(self, config_file: str) -> Dict[str, Any]:
        """
        加载规则（兼容旧接口）
        """
        self.rules = self.load_rules_from_file(config_file)
        return self.rules

    def extract(self) -> Dict[str, Any]:
        """
        提取规则
        """
        return self.rules
