from typing import List, Dict, Any, Optional, Callable
import logging
from .rules import RuleEngine, Rule

logger = logging.getLogger(__name__)


class Processor:
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or {}
        self.rule_engine = RuleEngine()
        self.custom_processors: List[Callable] = []
        
        self._load_rules_to_engine()
        
        logger.info("Processor initialized with %d rules", 
                   self.rule_engine.rule_count())
    
    def _load_rules_to_engine(self):
        if not isinstance(self.rules, dict):
            return
        
        rules_list = self.rules.get("rules", [])
        for rule_dict in rules_list:
            if not isinstance(rule_dict, dict):
                continue
            
            try:
                self.rule_engine.add_rule_dict(
                    name=rule_dict.get("name", "unnamed"),
                    condition=rule_dict.get("condition", {}),
                    action=rule_dict.get("action", {}),
                    priority=rule_dict.get("priority", 50)
                )
            except Exception as e:
                logger.warning("Failed to load rule: %s", e)
    
    def add_rule(self, rule: Rule):
        self.rule_engine.add_rule(rule)
        logger.debug("Added rule: %s", rule.name)
    
    def add_processor(self, processor: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.custom_processors.append(processor)
        logger.debug("Added custom processor")
    
    def process_tokens(
        self,
        tokens: List[Dict[str, Any]],
        apply_all_rules: bool = False
    ) -> List[Dict[str, Any]]:
        if not tokens:
            logger.warning("Empty token list provided")
            return []
        
        logger.info("Processing %d tokens", len(tokens))
        processed_data = []
        
        for i, token in enumerate(tokens):
            try:
                processed_token = self.process_single_token(token, apply_all_rules)
                processed_data.append(processed_token)
            except Exception as e:
                logger.error("Error processing token %d: %s", i, e)
                # 发生错误时保留原始 token
                processed_data.append(token)
        
        logger.info("Successfully processed %d tokens", len(processed_data))
        return processed_data
    
    def process_single_token(
        self,
        token: Dict[str, Any],
        apply_all_rules: bool = False
    ) -> Dict[str, Any]:
        processed = token.copy()
        
        if self.rule_engine.rule_count() > 0:
            processed = self.rule_engine.process(processed, apply_all_rules)
        
        for processor in self.custom_processors:
            try:
                processed = processor(processed)
            except Exception as e:
                logger.error("Custom processor failed: %s", e)
        
        if "timestamp" in processed:
            processed["processed"] = True
            
        return processed
    
    def apply_rules(self, token: Dict[str, Any]) -> Dict[str, Any]:
        return self.process_single_token(token)
    
    def generate_output(
        self,
        processed_data: List[Dict[str, Any]],
        format_type: str
    ) -> str:
        logger.info("Generating %s output for %d items", 
                   format_type, len(processed_data))
        
        if format_type == "json":
            return self.generate_json_output(processed_data)
        elif format_type == "html":
            return self.generate_html_output(processed_data)
        elif format_type == "markdown":
            return self.generate_markdown_output(processed_data)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def generate_json_output(self, processed_data: List[Dict[str, Any]]) -> str:
        import json
        return json.dumps(processed_data, ensure_ascii=False, indent=2)
    
    def generate_html_output(self, processed_data: List[Dict[str, Any]]) -> str:
        return (
            "<html><body>"
            + "".join(f"<p>{data}</p>" for data in processed_data)
            + "</body></html>"
        )
    
    def generate_markdown_output(self, processed_data: List[Dict[str, Any]]) -> str:
        return "\n".join(f"- {data}" for data in processed_data)
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "rule_count": self.rule_engine.rule_count(),
            "custom_processor_count": len(self.custom_processors),
            "has_rules_config": bool(self.rules),
        }
