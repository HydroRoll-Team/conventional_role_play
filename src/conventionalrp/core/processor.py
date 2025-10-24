from typing import List, Dict, Any, Optional


class Processor:
    """处理器，用于处理解析后的token"""
    
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        """
        初始化处理器
        
        Args:
            rules: 处理规则（可选）
        """
        self.rules = rules or {}

    def process_tokens(self, tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理token列表
        
        Args:
            tokens: 解析后的token列表
            
        Returns:
            处理后的数据列表
        """
        processed_data = []
        for token in tokens:
            processed_token = self.apply_rules(token)
            processed_data.append(processed_token)
        return processed_data

    def apply_rules(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """
        对单个token应用规则
        
        Args:
            token: 单个token
            
        Returns:
            处理后的token
        """
        # 基础实现：直接返回token
        # 可以在此添加更多处理逻辑
        processed = token.copy()
        
        # 添加处理时间戳
        if "timestamp" in processed:
            processed["processed"] = True
            
        return processed

    def generate_output(self, processed_data: List[Dict[str, Any]], format_type: str) -> str:
        """
        生成指定格式的输出
        
        Args:
            processed_data: 处理后的数据
            format_type: 输出格式 (json/html/markdown)
            
        Returns:
            格式化后的字符串
            
        Raises:
            ValueError: 不支持的格式类型
        """
        if format_type == "json":
            return self.generate_json_output(processed_data)
        elif format_type == "html":
            return self.generate_html_output(processed_data)
        elif format_type == "markdown":
            return self.generate_markdown_output(processed_data)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def generate_json_output(self, processed_data: List[Dict[str, Any]]) -> str:
        """生成JSON格式输出"""
        import json
        return json.dumps(processed_data, ensure_ascii=False, indent=2)

    def generate_html_output(self, processed_data: List[Dict[str, Any]]) -> str:
        """生成HTML格式输出"""
        return (
            "<html><body>"
            + "".join(f"<p>{data}</p>" for data in processed_data)
            + "</body></html>"
        )

    def generate_markdown_output(self, processed_data: List[Dict[str, Any]]) -> str:
        """生成Markdown格式输出"""
        return "\n".join(f"- {data}" for data in processed_data)
