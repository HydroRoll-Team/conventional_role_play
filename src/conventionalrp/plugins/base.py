from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """
    插件基类
    
    所有插件必须继承此类并实现必要的方法
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
        self.logger = logging.getLogger(f"conventionalrp.plugins.{name}")
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None):
        pass
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass
    
    def on_enable(self):
        """插件启用时调用"""
        self.logger.info(f"Plugin {self.name} enabled")
    
    def on_disable(self):
        """插件禁用时调用"""
        self.logger.info(f"Plugin {self.name} disabled")
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "type": self.__class__.__name__,
        }
    
    def __repr__(self) -> str:
        return f"Plugin(name={self.name}, version={self.version}, enabled={self.enabled})"


class ParserPlugin(Plugin):
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        self.priority = 50
    
    @abstractmethod
    def can_parse(self, text: str) -> bool:
        """
        判断是否可以解析给定文本
        """
        pass
    
    @abstractmethod
    def parse(self, text: str) -> List[Dict[str, Any]]:
        """
        解析文本
        """
        pass


class ProcessorPlugin(Plugin):
    @abstractmethod
    def process_token(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个 token
        """
        pass
    
    def process(self, data: Any) -> Any:
        """
        处理数据（实现基类方法）
        """
        if isinstance(data, dict):
            return self.process_token(data)
        elif isinstance(data, list):
            return [self.process_token(token) for token in data]
        return data


class RendererPlugin(Plugin):
    @abstractmethod
    def render(self, data: Any) -> str:
        pass
    
    def process(self, data: Any) -> Any:
        return self.render(data)


class AnalyzerPlugin(Plugin):
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        pass
    
    def process(self, data: Any) -> Any:
        return self.analyze(data)
