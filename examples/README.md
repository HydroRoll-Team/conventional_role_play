# ConventionalRP 示例

本目录包含 ConventionalRP SDK 的使用示例。

## 目录结构

```
examples/
├── basic_usage.py          # 基础使用示例
├── custom_plugin.py        # 自定义插件示例
├── rules/                  # 规则文件
│   └── dnd5e_rules.json5  # D&D 5E 解析规则
├── logs/                   # 示例日志文件
│   ├── sample_session.txt # 完整会话日志
│   └── combat_log.txt     # 战斗日志
└── output/                 # 输出文件目录（自动生成）
```

## 快速开始

### 1. 基础使用示例

演示如何解析 TRPG 日志并以多种格式输出：

```bash
cd examples
python basic_usage.py
```

**输出：**
- `output/session_output.json` - JSON 格式
- `output/session_output.html` - HTML 格式
- `output/session_output.md` - Markdown 格式

### 2. 自定义插件示例

演示如何创建自定义插件进行数据分析：

```bash
python custom_plugin.py
```

**功能：**
- 骰子统计分析
- 对话提取
- 角色行为分析

## 规则文件格式

规则文件使用 JSON5 格式（支持注释和尾随逗号）：

```json5
{
  metadata: [{
    type: "metadata",
    patterns: ["正则表达式"],
    groups: ["字段名"],
    priority: 100
  }],
  
  content: [{
    type: "内容类型",
    match_type: "匹配模式",  // enclosed, prefix, suffix
    patterns: ["正则表达式"],
    groups: ["提取字段"],
    priority: 90
  }]
}
```

### 匹配模式说明

- **enclosed**: 封闭匹配（如 `**动作**`、`「对话」`）
- **prefix**: 前缀匹配（如 `[系统]消息`）
- **suffix**: 后缀匹配（文本结尾）

### 优先级

- 数字越大优先级越高
- 建议范围：1-100
- 元数据通常设置为最高优先级（100）

## 日志文件格式

标准 TRPG 日志格式：

```
[时间戳] <角色名> 内容
```

**示例：**

```
[2025-10-24 14:30:01] <艾莉娅> 「我要检查这扇门」
[2025-10-24 14:30:05] <DiceBot> 检定结果: [d20 = 18]
[2025-10-24 14:30:10] <DM> 你发现了陷阱
```

## 自定义规则

你可以为不同的游戏系统创建自定义规则：

### D&D 5E

已提供 `rules/dnd5e_rules.json5`

### 其他系统

创建新的规则文件，参考 D&D 5E 规则的结构：

```bash
cp rules/dnd5e_rules.json5 rules/my_system_rules.json5
# 然后编辑 my_system_rules.json5
```

## 创建自定义插件

插件是用于扩展功能的 Python 类：

```python
class MyPlugin:
    def __init__(self):
        self.name = "My Plugin"
    
    def process(self, parsed_data):
        # 你的处理逻辑
        return result
```

查看 `custom_plugin.py` 了解完整示例。

## 常见模式

### 1. 骰子投掷

- `[d20 = 18]` - 简单投掷结果
- `.r1d20+5` - 投掷命令
- `(1d20+5 = 18)` - 完整投掷信息

### 2. 角色动作

- `*动作描述*` - 单星号
- `**重要动作**` - 双星号

### 3. 对话

- `「对话内容」` - 中文引号
- `"对话内容"` - 英文引号
- `"对话内容"` - 弯引号

### 4. OOC（脱戏）

- `((OOC内容))` - 双括号
- `//OOC注释` - 双斜杠

### 5. 系统消息

- `[系统]消息内容`
- `[System]Message`

## 疑难解答

### 问题：规则文件加载失败

**解决方案：**
1. 确保文件是有效的 JSON5 格式
2. 检查正则表达式是否转义正确（使用 `\\` 而不是 `\`）
3. 验证文件编码为 UTF-8

### 问题：解析结果不正确

**解决方案：**
1. 调整规则的优先级
2. 测试正则表达式（使用 https://regex101.com/）
3. 检查 match_type 是否正确

### 问题：中文字符显示异常

**解决方案：**
- 确保所有文件使用 UTF-8 编码
- 在打开文件时指定 `encoding='utf-8'`

## 更多示例

访问项目文档查看更多示例：
https://crp.hydroroll.team/

## 贡献

欢迎提交新的示例和规则文件！请参考 CONTRIBUTING.md
