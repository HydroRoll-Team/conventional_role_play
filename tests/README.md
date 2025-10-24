# ConventionalRP 测试套件

本目录包含 ConventionalRP SDK 的所有单元测试。

## 测试文件

- `test_parser.py` - Parser 解析器测试
- `test_processor.py` - Processor 处理器测试
- `test_rule_extractor.py` - RuleExtractor 规则提取器测试
- `test_renderers.py` - 渲染器测试（HTML/JSON/Markdown）
- `test_pyo3.py` - PyO3 Rust 扩展测试

## 运行测试

### 运行所有测试

```bash
python tests/run_tests.py
```

### 运行单个测试文件

```bash
python -m unittest tests/test_parser.py
python -m unittest tests/test_processor.py
```

### 运行特定测试类

```bash
python -m unittest tests.test_parser.TestParser
```

### 运行特定测试方法

```bash
python -m unittest tests.test_parser.TestParser.test_load_rules_success
```

## 测试覆盖率

要查看测试覆盖率，请安装 `coverage` 并运行：

```bash
pip install coverage
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report
coverage html  # 生成 HTML 报告
```

## 测试数据

测试使用临时文件来模拟规则文件和日志文件，测试完成后会自动清理。

## 添加新测试

创建新的测试文件时，请遵循以下约定：

1. 文件名以 `test_` 开头
2. 测试类继承自 `unittest.TestCase`
3. 测试方法以 `test_` 开头
4. 使用 `setUp()` 和 `tearDown()` 方法管理测试状态
5. 添加清晰的文档字符串说明测试目的
