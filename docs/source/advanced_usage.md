# 高级使用指南

## 目录

1. [插件系统](#插件系统)
2. [规则引擎](#规则引擎)
3. [自定义渲染器](#自定义渲染器)
4. [性能优化](#性能优化)
5. [错误处理](#错误处理)

---

## 插件系统

ConventionalRP 提供了强大的插件系统，允许您扩展和定制框架的功能。

### 插件类型

#### 1. 解析器插件 (ParserPlugin)

用于扩展文本解析功能：

```python
from conventionalrp.plugins import ParserPlugin

class CustomParserPlugin(ParserPlugin):
    def __init__(self):
        super().__init__("CustomParser", "1.0.0")
        self.priority = 60  # 优先级
    
    def initialize(self, config=None):
        self.config = config or {}
    
    def can_parse(self, text: str) -> bool:
        # 判断是否可以解析
        return text.startswith("custom:")
    
    def parse(self, text: str) -> List[Dict[str, Any]]:
        # 解析文本
        return [{"type": "custom", "content": text}]
```

#### 2. 处理器插件 (ProcessorPlugin)

用于数据处理和转换：

```python
from conventionalrp.plugins import ProcessorPlugin

class CombatTrackerPlugin(ProcessorPlugin):
    def __init__(self):
        super().__init__("CombatTracker", "1.0.0")
        self.total_damage = 0
    
    def initialize(self, config=None):
        self.config = config or {}
    
    def process_token(self, token: Dict[str, Any]) -> Dict[str, Any]:
        # 处理单个 token
        content = token.get("content", "")
        
        # 检测伤害
        import re
        damage_match = re.search(r'(\d+)\s*点?伤害', content)
        if damage_match:
            damage = int(damage_match.group(1))
            self.total_damage += damage
            token["combat_data"] = {
                "type": "damage",
                "amount": damage,
                "total": self.total_damage
            }
        
        return token
```

#### 3. 渲染器插件 (RendererPlugin)

用于自定义输出格式：

```python
from conventionalrp.plugins import RendererPlugin

class PlainTextRenderer(RendererPlugin):
    def __init__(self):
        super().__init__("PlainText", "1.0.0")
    
    def initialize(self, config=None):
        self.config = config or {}
    
    def render(self, data: Any) -> str:
        # 渲染为纯文本
        lines = []
        for item in data:
            speaker = item.get("speaker", "")
            content = item.get("content", "")
            if speaker:
                lines.append(f"{speaker}: {content}")
            else:
                lines.append(content)
        return "\n".join(lines)
```

#### 4. 分析器插件 (AnalyzerPlugin)

用于数据分析和统计：

```python
from conventionalrp.plugins import AnalyzerPlugin

class SessionAnalyzerPlugin(AnalyzerPlugin):
    def __init__(self):
        super().__init__("SessionAnalyzer", "1.0.0")
    
    def initialize(self, config=None):
        self.config = config or {}
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        # 分析游戏数据
        stats = {
            "total_dialogues": 0,
            "total_dice_rolls": 0,
            "active_characters": set(),
        }
        
        for token in data:
            token_type = token.get("type", "")
            if token_type == "dialogue":
                stats["total_dialogues"] += 1
            elif token_type == "dice":
                stats["total_dice_rolls"] += 1
            
            speaker = token.get("speaker", "")
            if speaker:
                stats["active_characters"].add(speaker)
        
        stats["active_characters"] = list(stats["active_characters"])
        return stats
```

### 使用插件管理器

```python
from conventionalrp.plugins import PluginManager

# 创建管理器
manager = PluginManager(plugin_dirs=["./my_plugins"])

# 发现插件
discovered = manager.discover_plugins()
print(f"发现 {len(discovered)} 个插件")

# 注册插件
my_plugin = MyCustomPlugin()
my_plugin.initialize()
manager.register_plugin(my_plugin)

# 执行插件
result = manager.execute_plugins(data, plugin_type=ProcessorPlugin)

# 启用/禁用插件
manager.disable_plugin("MyPlugin")
manager.enable_plugin("MyPlugin")

# 获取统计信息
stats = manager.get_statistics()
print(stats)
```

---

## 规则引擎

规则引擎允许您定义灵活的数据处理规则。

### 规则定义

```python
from conventionalrp.core.rules import Rule, RuleEngine

# 创建规则
rule = Rule(
    name="detect_critical_hit",
    conditions={
        "type": {"equals": "dice"},
        "content": {"matches": r"d20=20"}
    },
    actions=[
        {"action": "add_tag", "tag": "critical_hit"},
        {"action": "set_field", "field": "is_critical", "value": True}
    ],
    priority=100
)
```

### 条件运算符

- `equals`: 精确匹配
- `not_equals`: 不等于
- `contains`: 包含子字符串
- `not_contains`: 不包含
- `matches`: 正则表达式匹配
- `in`: 值在列表中
- `not_in`: 值不在列表中
- `greater_than`: 大于
- `less_than`: 小于

### 动作类型

- `set_field`: 设置字段值
- `add_tag`: 添加标签
- `remove_field`: 删除字段
- `transform`: 自定义转换函数

### 使用规则引擎

```python
# 创建引擎
engine = RuleEngine()

# 添加规则
engine.add_rule(rule)

# 应用规则
tokens = [
    {"type": "dice", "content": "d20=20"},
    {"type": "dialogue", "content": "我投了大成功！"}
]

processed_tokens = engine.apply_rules(tokens)

# 移除规则
engine.remove_rule("detect_critical_hit")
```

### 高级示例：动态规则

```python
def create_damage_rule(min_damage: int):
    """创建伤害检测规则"""
    return Rule(
        name=f"detect_damage_{min_damage}",
        conditions={
            "content": {"matches": rf"(\d+)点伤害"},
            # 可以添加自定义验证
        },
        actions=[
            {"action": "set_field", "field": "damage_detected", "value": True},
            {"action": "transform", "function": lambda token: {
                **token,
                "damage_level": "high" if int(re.search(r'(\d+)', token["content"]).group(1)) > min_damage else "normal"
            }}
        ]
    )

# 使用
engine.add_rule(create_damage_rule(20))
```

---

## 自定义渲染器

### 继承 BaseRenderer

```python
from conventionalrp.renderers.base import BaseRenderer

class LaTeXRenderer(BaseRenderer):
    def __init__(self):
        super().__init__()
    
    def render(self, data: List[Dict[str, Any]]) -> str:
        latex = r"\documentclass{article}" + "\n"
        latex += r"\begin{document}" + "\n"
        
        for item in data:
            token_type = item.get("type", "")
            content = item.get("content", "")
            
            if token_type == "dialogue":
                speaker = item.get("speaker", "")
                latex += rf"\textbf{{{speaker}:}} {content}\\" + "\n"
            else:
                latex += f"{content}\\\\\n"
        
        latex += r"\end{document}" + "\n"
        return latex
```

### 使用主题系统

```python
from conventionalrp.renderers.html_renderer import HTMLRenderer

# 使用内置主题
renderer = HTMLRenderer(theme="dark")

# 使用自定义 CSS
custom_css = """
body {
    background: linear-gradient(to bottom, #2c3e50, #3498db);
}
.token {
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
"""

renderer = HTMLRenderer(theme="light", custom_css=custom_css)
output = renderer.render(data)
```

---

## 性能优化

### 1. 使用 Rust 核心

编译 Rust 模块获得更好的性能：

```bash
maturin develop --uv --release
```

### 2. 批量处理

```python
# 不推荐：逐个处理
for token in tokens:
    processor.process(token)

# 推荐：批量处理
processed_tokens = processor.process_batch(tokens)
```

### 3. 规则优化

```python
# 设置合适的优先级
Rule(name="fast_rule", priority=100, ...)  # 先执行
Rule(name="slow_rule", priority=10, ...)   # 后执行

# 预编译正则表达式
import re
pattern = re.compile(r'd\d+')  # 编译一次
rule = Rule(
    conditions={"content": {"matches": pattern}},
    ...
)
```

### 4. 缓存结果

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(data: str) -> str:
    # 昂贵的计算
    return result
```

### 性能基准测试

```bash
# 运行基准测试
python benchmarks/benchmark_parser.py
python benchmarks/benchmark_rules.py
```

---

## 错误处理

### 自定义异常

```python
from conventionalrp.utils.exceptions import (
    ParsingError,
    RuleError,
    PluginError
)

try:
    parser.parse_log("invalid.txt")
except ParsingError as e:
    print(f"解析错误: {e}")
except FileNotFoundError as e:
    print(f"文件未找到: {e}")
```

### 日志配置

```python
from conventionalrp.utils.logging_config import setup_logging
import logging

# 设置日志级别
setup_logging(level=logging.DEBUG)

# 在您的代码中使用
logger = logging.getLogger(__name__)
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告")
logger.error("错误")
```

### 最佳实践

1. **始终验证输入**
   ```python
   def process_token(token: Dict[str, Any]) -> Dict[str, Any]:
       if not isinstance(token, dict):
           raise TypeError("Token must be a dictionary")
       
       if "type" not in token:
           raise ValueError("Token must have a 'type' field")
       
       return processed_token
   ```

2. **使用类型提示**
   ```python
   from typing import List, Dict, Any, Optional
   
   def parse_data(text: str) -> List[Dict[str, Any]]:
       ...
   ```

3. **提供清晰的错误消息**
   ```python
   if not file_path.exists():
       raise FileNotFoundError(
           f"Log file not found: {file_path}\n"
           f"Please check the file path and try again."
       )
   ```

---

## 完整示例

查看 `examples/` 目录获取更多示例：

- `basic_usage.py` - 基本使用
- `rule_system_demo.py` - 规则系统演示
- `plugin_system_demo.py` - 插件系统演示
- `renderer_demo.py` - 渲染器演示

---

## 下一步

- 阅读 [API 文档](api.md)
- 查看 [插件开发指南](plugin_guide.md)
- 参与 [GitHub 讨论](https://github.com/HydroRoll-Team/conventional_role_play/discussions)
