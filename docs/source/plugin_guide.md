# 插件开发指南

本指南将帮助您创建自己的 ConventionalRP 插件。

## 目录

1. [插件基础](#插件基础)
2. [插件类型](#插件类型)
3. [开发流程](#开发流程)
4. [最佳实践](#最佳实践)
5. [发布插件](#发布插件)

---

## 插件基础

### 什么是插件？

插件是扩展 ConventionalRP 功能的独立模块。每个插件继承自基础 `Plugin` 类，并实现特定的接口。

### 插件生命周期

1. **发现** - PluginManager 扫描插件目录
2. **加载** - 导入插件模块
3. **初始化** - 调用 `initialize()` 方法
4. **启用** - 调用 `on_enable()` 钩子
5. **执行** - 调用 `process()` 方法处理数据
6. **禁用** - 调用 `on_disable()` 钩子

### 基本结构

```python
from conventionalrp.plugins import Plugin
from typing import Any, Dict, Optional

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__(name="MyPlugin", version="1.0.0")
        # 初始化插件状态
        self.data = {}
    
    def initialize(self, config: Optional[Dict[str, Any]] = None):
        """初始化插件，加载配置"""
        self.config = config or {}
        self.logger.info(f"{self.name} initialized with config: {self.config}")
    
    def process(self, data: Any) -> Any:
        """处理数据"""
        self.logger.debug(f"Processing data: {data}")
        # 实现您的处理逻辑
        return data
    
    def on_enable(self):
        """插件启用时调用"""
        super().on_enable()
        # 执行启用逻辑（如打开文件、建立连接等）
    
    def on_disable(self):
        """插件禁用时调用"""
        # 执行清理逻辑（如关闭文件、断开连接等）
        super().on_disable()
```

---

## 插件类型

### 1. 解析器插件 (ParserPlugin)

解析器插件用于识别和解析特定格式的文本。

#### 接口

```python
from conventionalrp.plugins import ParserPlugin

class MyParserPlugin(ParserPlugin):
    def can_parse(self, text: str) -> bool:
        """判断是否可以解析给定文本"""
        raise NotImplementedError
    
    def parse(self, text: str) -> List[Dict[str, Any]]:
        """解析文本并返回结果"""
        raise NotImplementedError
```

#### 示例：CoC 规则解析器

```python
import re
from conventionalrp.plugins import ParserPlugin

class CoCParserPlugin(ParserPlugin):
    """Call of Cthulhu 规则解析器"""
    
    def __init__(self):
        super().__init__("CoCParser", "1.0.0")
        self.priority = 60
        
        # CoC 特有的模式
        self.skill_check_pattern = re.compile(
            r'\.(?:rc|san|sc)\s+(.+)',
            re.IGNORECASE
        )
        self.sanity_pattern = re.compile(
            r'(\d+)/(\d+d\d+)',
            re.IGNORECASE
        )
    
    def initialize(self, config=None):
        self.config = config or {}
    
    def can_parse(self, text: str) -> bool:
        """检查是否是 CoC 指令"""
        return bool(self.skill_check_pattern.match(text))
    
    def parse(self, text: str) -> List[Dict[str, Any]]:
        """解析 CoC 指令"""
        results = []
        
        match = self.skill_check_pattern.match(text)
        if match:
            command_text = match.group(1)
            
            # 解析 SAN 检定
            san_match = self.sanity_pattern.search(command_text)
            if san_match:
                results.append({
                    "type": "sanity_check",
                    "success_loss": san_match.group(1),
                    "failure_loss": san_match.group(2),
                    "content": text,
                })
            else:
                # 普通技能检定
                results.append({
                    "type": "skill_check",
                    "skill": command_text.strip(),
                    "content": text,
                })
        
        return results
```

### 2. 处理器插件 (ProcessorPlugin)

处理器插件用于转换和增强数据。

#### 示例：经验值追踪器

```python
from conventionalrp.plugins import ProcessorPlugin
import re

class ExperienceTrackerPlugin(ProcessorPlugin):
    """经验值追踪插件"""
    
    def __init__(self):
        super().__init__("ExperienceTracker", "1.0.0")
        self.character_exp = {}
        self.exp_pattern = re.compile(r'获得\s*(\d+)\s*点?经验', re.IGNORECASE)
    
    def initialize(self, config=None):
        self.config = config or {}
        # 加载初始经验值
        if "initial_exp" in self.config:
            self.character_exp = self.config["initial_exp"].copy()
    
    def process_token(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """处理 token 并追踪经验值"""
        content = token.get("content", "")
        speaker = token.get("speaker", "")
        
        # 检测经验值获取
        match = self.exp_pattern.search(content)
        if match and speaker:
            exp_gained = int(match.group(1))
            
            if speaker not in self.character_exp:
                self.character_exp[speaker] = 0
            
            self.character_exp[speaker] += exp_gained
            
            # 添加经验值信息到 token
            token["exp_data"] = {
                "gained": exp_gained,
                "total": self.character_exp[speaker],
                "character": speaker,
            }
            
            self.logger.info(f"{speaker} 获得 {exp_gained} 经验，总计 {self.character_exp[speaker]}")
        
        return token
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """获取经验值排行榜"""
        sorted_chars = sorted(
            self.character_exp.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {"character": char, "exp": exp}
            for char, exp in sorted_chars
        ]
```

### 3. 渲染器插件 (RendererPlugin)

渲染器插件用于生成特定格式的输出。

#### 示例：Discord Markdown 渲染器

```python
from conventionalrp.plugins import RendererPlugin

class DiscordRenderer(RendererPlugin):
    """Discord Markdown 渲染器"""
    
    def __init__(self):
        super().__init__("DiscordRenderer", "1.0.0")
    
    def initialize(self, config=None):
        self.config = config or {}
        self.use_embeds = self.config.get("use_embeds", False)
    
    def render(self, data: Any) -> str:
        """渲染为 Discord 格式"""
        output = []
        
        for token in data:
            token_type = token.get("type", "unknown")
            speaker = token.get("speaker", "")
            content = token.get("content", "")
            
            if token_type == "dialogue":
                # 使用 Discord 的粗体和引用
                output.append(f"**{speaker}:** {content}")
            
            elif token_type == "dice":
                # 使用代码块高亮骰子结果
                result = token.get("result", "?")
                output.append(f"`{content}` → **{result}**")
            
            elif token_type == "narration":
                # 使用斜体表示旁白
                output.append(f"*{content}*")
            
            elif token_type == "system":
                # 使用代码块表示系统消息
                output.append(f"```\n{content}\n```")
            
            else:
                output.append(content)
        
        return "\n\n".join(output)
```

### 4. 分析器插件 (AnalyzerPlugin)

分析器插件用于统计和分析数据。

#### 示例：对话分析器

```python
from conventionalrp.plugins import AnalyzerPlugin
from collections import Counter

class DialogueAnalyzerPlugin(AnalyzerPlugin):
    """对话分析插件"""
    
    def __init__(self):
        super().__init__("DialogueAnalyzer", "1.0.0")
    
    def initialize(self, config=None):
        self.config = config or {}
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        """分析对话数据"""
        dialogue_count = Counter()
        word_count = Counter()
        total_words = 0
        
        for token in data:
            if token.get("type") == "dialogue":
                speaker = token.get("speaker", "Unknown")
                content = token.get("content", "")
                
                # 统计对话次数
                dialogue_count[speaker] += 1
                
                # 统计词数
                words = len(content.split())
                word_count[speaker] += words
                total_words += words
        
        # 计算参与度
        most_active = dialogue_count.most_common(1)
        most_talkative = word_count.most_common(1)
        
        return {
            "total_dialogues": sum(dialogue_count.values()),
            "total_words": total_words,
            "dialogue_count": dict(dialogue_count),
            "word_count": dict(word_count),
            "most_active_character": most_active[0][0] if most_active else None,
            "most_talkative_character": most_talkative[0][0] if most_talkative else None,
            "average_words_per_dialogue": total_words / sum(dialogue_count.values()) if dialogue_count else 0,
        }
```

---

## 开发流程

### 1. 创建插件项目

```bash
mkdir my_plugin
cd my_plugin
touch my_plugin.py
touch config.json
touch README.md
```

### 2. 实现插件

```python
# my_plugin.py
from conventionalrp.plugins import ProcessorPlugin

class MyPlugin(ProcessorPlugin):
    # ... 实现代码
    pass
```

### 3. 添加配置

```json
{
  "name": "MyPlugin",
  "version": "1.0.0",
  "description": "My custom plugin",
  "author": "Your Name",
  "settings": {
    "enable_feature_x": true,
    "threshold": 10
  }
}
```

### 4. 测试插件

```python
# test_my_plugin.py
import unittest
from my_plugin import MyPlugin

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin()
        self.plugin.initialize()
    
    def test_process(self):
        test_data = [{"type": "test", "content": "test"}]
        result = self.plugin.process(test_data)
        self.assertIsNotNone(result)
    
    def test_enable_disable(self):
        self.assertTrue(self.plugin.enabled)
        self.plugin.on_disable()
        self.assertFalse(self.plugin.enabled)

if __name__ == "__main__":
    unittest.main()
```

### 5. 集成测试

```python
# integration_test.py
from conventionalrp.plugins import PluginManager
from my_plugin import MyPlugin

manager = PluginManager()
plugin = MyPlugin()
plugin.initialize({"test": True})
manager.register_plugin(plugin)

# 测试数据
test_data = [...]

# 执行插件
result = manager.execute_plugins(test_data)
print(result)
```

---

## 最佳实践

### 1. 命名约定

- 插件类名使用 PascalCase，如 `MyCustomPlugin`
- 文件名使用 snake_case，如 `my_custom_plugin.py`
- 配置键使用 snake_case

### 2. 日志记录

```python
def process_token(self, token):
    self.logger.debug(f"Processing token: {token['type']}")
    
    try:
        result = self._do_processing(token)
        self.logger.info("Processing successful")
        return result
    except Exception as e:
        self.logger.error(f"Processing failed: {e}")
        raise
```

### 3. 错误处理

```python
from conventionalrp.utils.exceptions import PluginError

def initialize(self, config=None):
    try:
        self.config = config or {}
        # 验证必需的配置
        if "required_key" not in self.config:
            raise PluginError(
                f"{self.name}: Missing required configuration 'required_key'"
            )
    except Exception as e:
        self.logger.error(f"Initialization failed: {e}")
        raise
```

### 4. 性能优化

```python
# 使用缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(self, key: str) -> Any:
    # 昂贵的计算
    return result

# 批量处理
def process(self, data: List[Dict]) -> List[Dict]:
    # 一次性处理所有数据，而不是逐个处理
    return [self.process_token(token) for token in data]
```

### 5. 文档注释

```python
class MyPlugin(Plugin):
    """
    我的自定义插件
    
    这个插件用于...
    
    Attributes:
        setting_x: 设置 X 的说明
        setting_y: 设置 Y 的说明
    
    Example:
        >>> plugin = MyPlugin()
        >>> plugin.initialize({"setting_x": True})
        >>> result = plugin.process(data)
    """
    
    def process_token(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个 token
        
        Args:
            token: 输入 token
        
        Returns:
            处理后的 token
        
        Raises:
            PluginError: 如果处理失败
        """
        pass
```

---

## 发布插件

### 1. 准备文件

创建以下文件：
- `README.md` - 插件说明
- `LICENSE` - 开源许可证
- `requirements.txt` - 依赖列表
- `setup.py` 或 `pyproject.toml` - 打包配置

### 2. 打包

```bash
# 使用 setuptools
python setup.py sdist bdist_wheel

# 或使用 poetry
poetry build
```

### 3. 发布

```bash
# 发布到 PyPI
twine upload dist/*

# 或发布到 GitHub
git tag v1.0.0
git push origin v1.0.0
```

### 4. 文档

在 README.md 中包含：
- 插件描述
- 安装方法
- 使用示例
- 配置选项
- API 文档
- 许可证信息

---

## 示例项目结构

```
my_plugin/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   └── utils.py
├── tests/
│   ├── test_plugin.py
│   └── test_utils.py
└── examples/
    └── example_usage.py
```

---

## 相关资源

- [插件系统演示](../../examples/plugin_system_demo.py)
- [示例插件](../../examples/plugins/)
- [API 文档](api.md)
- [高级使用指南](advanced_usage.md)
