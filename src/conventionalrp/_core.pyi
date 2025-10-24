"""
提供高性能的文本解析和匹配功能
"""

from typing import Dict, List, Optional, Tuple

class Base:
    """基础类（向后兼容）"""
    ...

class Token:
    """
    解析后的 Token
    
    表示文本中的一个语义单元，包含类型、内容和元数据
    """
    
    token_type: str
    content: str
    metadata: Dict[str, str]
    
    def __init__(self, token_type: str, content: str) -> None:
        """
        创建新的 Token
        
        Args:
            token_type: Token 类型
            content: Token 内容
        """
        ...
    
    def add_metadata(self, key: str, value: str) -> None:
        """
        添加元数据
        
        Args:
            key: 元数据键
            value: 元数据值
        """
        ...
    
    def get_metadata(self, key: str) -> Optional[str]:
        """
        获取元数据
        
        Args:
            key: 元数据键
        
        Returns:
            元数据值，如果不存在返回 None
        """
        ...
    
    def to_dict(self) -> Dict[str, any]:
        """
        转换为 Python 字典
        
        Returns:
            包含 Token 所有信息的字典
        """
        ...
    
    def __repr__(self) -> str: ...

class RegexRule:
    """
    正则表达式规则
    
    用于文本匹配和提取
    """
    
    rule_type: str
    priority: int
    
    def __init__(self, pattern: str, rule_type: str, priority: int) -> None:
        """
        创建正则规则
        
        Args:
            pattern: 正则表达式模式
            rule_type: 规则类型
            priority: 优先级（数字越大优先级越高）
        
        Raises:
            ValueError: 如果正则表达式无效
        """
        ...
    
    def matches(self, text: str) -> bool:
        """
        测试文本是否匹配
        
        Args:
            text: 待测试的文本
        
        Returns:
            是否匹配
        """
        ...
    
    def extract(self, text: str) -> Optional[List[str]]:
        """
        提取匹配的捕获组
        
        Args:
            text: 待提取的文本
        
        Returns:
            捕获组列表，如果不匹配返回 None
        """
        ...
    
    def find_all(self, text: str) -> List[Tuple[int, int, str]]:
        """
        查找所有匹配
        
        Args:
            text: 待搜索的文本
        
        Returns:
            列表，每个元素为 (start, end, matched_text)
        """
        ...

class TextParser:
    """
    高性能文本解析器
    
    支持多规则、优先级排序的文本解析
    """
    
    def __init__(self) -> None:
        """创建新的解析器"""
        ...
    
    def add_rule(self, pattern: str, rule_type: str, priority: int) -> None:
        """
        添加解析规则
        
        Args:
            pattern: 正则表达式模式
            rule_type: 规则类型
            priority: 优先级
        
        Raises:
            ValueError: 如果正则表达式无效
        """
        ...
    
    def parse_line(self, text: str) -> List[Tuple[str, str, int, int]]:
        """
        解析单行文本
        
        Args:
            text: 待解析的文本
        
        Returns:
            列表，每个元素为 (type, content, start, end)
        """
        ...
    
    def parse_lines(self, lines: List[str]) -> List[List[Dict[str, any]]]:
        """
        批量解析多行文本
        
        Args:
            lines: 文本行列表
        
        Returns:
            每行的解析结果列表
        """
        ...
    
    def clear_rules(self) -> None:
        """清除所有规则"""
        ...
    
    def rule_count(self) -> int:
        """
        获取规则数量
        
        Returns:
            当前规则数量
        """
        ...

class FastMatcher:
    """
    快速字符串匹配器
    
    用于高效的多模式字符串匹配
    """
    
    def __init__(self, patterns: List[str]) -> None:
        """
        创建匹配器
        
        Args:
            patterns: 模式列表
        """
        ...
    
    def contains_any(self, text: str) -> bool:
        """
        检查文本是否包含任意模式
        
        Args:
            text: 待检查的文本
        
        Returns:
            是否包含任意模式
        """
        ...
    
    def find_matches(self, text: str) -> List[str]:
        """
        查找所有匹配的模式
        
        Args:
            text: 待搜索的文本
        
        Returns:
            匹配的模式列表
        """
        ...
    
    def count_matches(self, text: str) -> Dict[str, int]:
        """
        统计每个模式的出现次数
        
        Args:
            text: 待统计的文本
        
        Returns:
            字典，键为模式，值为出现次数
        """
        ...
