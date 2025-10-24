from typing import Dict, Any, Callable, List, Optional
from enum import Enum
import re


class RuleCondition(Enum):
    """规则条件类型"""
    EQUALS = "equals"
    CONTAINS = "contains"
    MATCHES = "matches"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN_LIST = "in_list"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


class Rule:
    def __init__(
        self,
        name: str,
        condition: Dict[str, Any],
        action: Dict[str, Any],
        priority: int = 50
    ):
        self.name = name
        self.condition = condition
        self.action = action
        self.priority = priority
        self._compiled_patterns = {}
        
        self._precompile_patterns()
    
    def _precompile_patterns(self):
        """预编译正则表达式以提高性能"""
        if isinstance(self.condition, dict):
            for key, value in self.condition.items():
                if isinstance(value, dict) and value.get("type") == "matches":
                    pattern = value.get("pattern")
                    if pattern:
                        self._compiled_patterns[key] = re.compile(pattern)
    
    def matches(self, data: Dict[str, Any]) -> bool:
        """
        检查数据是否匹配规则条件
        """
        if not isinstance(self.condition, dict):
            return False
        
        for field, condition_spec in self.condition.items():
            if not self._check_field_condition(data, field, condition_spec):
                return False
        
        return True
    
    def _check_field_condition(
        self,
        data: Dict[str, Any],
        field: str,
        condition: Any
    ) -> bool:
        """检查单个字段的条件"""
        value = data.get(field)
        
        if not isinstance(condition, dict):
            return value == condition
        
        condition_type = condition.get("type")
        expected_value = condition.get("value")
        
        if condition_type == "equals":
            return value == expected_value
        elif condition_type == "contains":
            return expected_value in str(value) if value else False
        elif condition_type == "matches":
            if field in self._compiled_patterns:
                pattern = self._compiled_patterns[field]
                return bool(pattern.search(str(value))) if value else False
            return False
        elif condition_type == "starts_with":
            return str(value).startswith(expected_value) if value else False
        elif condition_type == "ends_with":
            return str(value).endswith(expected_value) if value else False
        elif condition_type == "in_list":
            return value in expected_value if isinstance(expected_value, list) else False
        elif condition_type == "greater_than":
            try:
                return float(value) > float(expected_value)
            except (ValueError, TypeError):
                return False
        elif condition_type == "less_than":
            try:
                return float(value) < float(expected_value)
            except (ValueError, TypeError):
                return False
        
        return False
    
    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        对匹配的数据应用规则动作
        """
        result = data.copy()
        
        if not isinstance(self.action, dict):
            return result
        
        action_type = self.action.get("type")
        
        if action_type == "set_field":
            field = self.action.get("field")
            value = self.action.get("value")
            if field:
                result[field] = value
        
        elif action_type == "add_field":
            field = self.action.get("field")
            value = self.action.get("value")
            if field and field not in result:
                result[field] = value
        
        elif action_type == "remove_field":
            field = self.action.get("field")
            if field and field in result:
                del result[field]
        
        elif action_type == "transform":
            field = self.action.get("field")
            func_name = self.action.get("function")
            if field and field in result and func_name:
                result[field] = self._apply_transform(result[field], func_name)
        
        elif action_type == "add_tag":
            tag = self.action.get("tag")
            if tag:
                if "tags" not in result:
                    result["tags"] = []
                if tag not in result["tags"]:
                    result["tags"].append(tag)
        
        elif action_type == "copy_field":
            source = self.action.get("source")
            target = self.action.get("target")
            if source and target and source in result:
                result[target] = result[source]
        
        return result
    
    def _apply_transform(self, value: Any, func_name: str) -> Any:
        transforms = {
            "upper": lambda x: str(x).upper(),
            "lower": lambda x: str(x).lower(),
            "strip": lambda x: str(x).strip(),
            "int": lambda x: int(x),
            "float": lambda x: float(x),
            "len": lambda x: len(x) if hasattr(x, '__len__') else 0,
        }
        
        func = transforms.get(func_name)
        if func:
            try:
                return func(value)
            except Exception:
                return value
        return value
    
    def __repr__(self) -> str:
        return f"Rule(name={self.name}, priority={self.priority})"


class RuleEngine:
    """
    规则引擎
    """
    
    def __init__(self):
        self.rules: List[Rule] = []
        self._sorted = False
    
    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        self._sorted = False
    
    def add_rule_dict(
        self,
        name: str,
        condition: Dict[str, Any],
        action: Dict[str, Any],
        priority: int = 50
    ):
        """
        从字典添加规则
        """
        rule = Rule(name, condition, action, priority)
        self.add_rule(rule)
    
    def _ensure_sorted(self):
        """确保规则按优先级排序"""
        if not self._sorted:
            self.rules.sort(key=lambda r: r.priority, reverse=True)
            self._sorted = True
    
    def process(
        self,
        data: Dict[str, Any],
        apply_all: bool = False
    ) -> Dict[str, Any]:
        self._ensure_sorted()
        result = data.copy()
        
        for rule in self.rules:
            if rule.matches(result):
                result = rule.apply(result)
                if not apply_all:
                    break
        
        return result
    
    def process_batch(
        self,
        data_list: List[Dict[str, Any]],
        apply_all: bool = False
    ) -> List[Dict[str, Any]]:
        return [self.process(data, apply_all) for data in data_list]
    
    def find_matching_rules(self, data: Dict[str, Any]) -> List[Rule]:
        self._ensure_sorted()
        return [rule for rule in self.rules if rule.matches(data)]
    
    def clear_rules(self):
        self.rules.clear()
        self._sorted = False
    
    def rule_count(self) -> int:
        return len(self.rules)
    
    def __repr__(self) -> str:
        return f"RuleEngine(rules={len(self.rules)})"
