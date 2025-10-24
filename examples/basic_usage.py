#!/usr/bin/env python3
"""
基础使用示例
演示如何使用 ConventionalRP 解析和处理 TRPG 日志
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from conventionalrp.core.parser import Parser
from conventionalrp.core.processor import Processor
from conventionalrp.extractors.rule_extractor import RuleExtractor
from conventionalrp.renderers.html_renderer import HTMLRenderer
from conventionalrp.renderers.json_renderer import JSONRenderer
from conventionalrp.renderers.markdown_renderer import MarkdownRenderer


def main():
    # 获取示例文件路径
    example_dir = Path(__file__).parent
    rules_file = example_dir / "rules" / "dnd5e_rules.json5"
    log_file = example_dir / "logs" / "sample_session.txt"
    
    print("=" * 60)
    print("ConventionalRP 基础使用示例")
    print("=" * 60)
    
    # 步骤 1: 加载规则
    print("\n[步骤 1] 加载解析规则...")
    parser = Parser()
    parser.load_rules(str(rules_file))
    print(f"✓ 规则加载成功: {rules_file.name}")
    
    # 步骤 2: 解析日志
    print("\n[步骤 2] 解析 TRPG 日志...")
    parsed_data = parser.parse_log(str(log_file))
    print(f"✓ 日志解析完成，共 {len(parsed_data)} 条记录")
    
    # 步骤 3: 处理解析结果
    print("\n[步骤 3] 处理解析后的数据...")
    processor = Processor()
    processed_data = processor.process_tokens(parsed_data)
    print(f"✓ 数据处理完成")
    
    # 步骤 4: 渲染输出
    print("\n[步骤 4] 渲染输出...")
    
    # JSON 格式
    json_renderer = JSONRenderer()
    json_output = json_renderer.render(processed_data)
    json_file = example_dir / "output" / "session_output.json"
    json_file.parent.mkdir(exist_ok=True)
    with open(json_file, "w", encoding="utf-8") as f:
        f.write(json_output)
    print(f"✓ JSON 输出已保存: {json_file}")
    
    # HTML 格式
    html_renderer = HTMLRenderer()
    html_output = html_renderer.render(processed_data)
    html_file = example_dir / "output" / "session_output.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_output)
    print(f"✓ HTML 输出已保存: {html_file}")
    
    # Markdown 格式
    md_renderer = MarkdownRenderer()
    md_output = md_renderer.render(processed_data)
    md_file = example_dir / "output" / "session_output.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_output)
    print(f"✓ Markdown 输出已保存: {md_file}")
    
    # 预览前几条记录
    print("\n" + "=" * 60)
    print("解析结果预览（前3条）:")
    print("=" * 60)
    for i, entry in enumerate(parsed_data[:3], 1):
        print(f"\n[记录 {i}]")
        print(f"  时间: {entry.get('timestamp', 'N/A')}")
        print(f"  发言者: {entry.get('speaker', 'N/A')}")
        print(f"  内容类型数: {len(entry.get('content', []))}")
        for content in entry.get('content', [])[:2]:  # 只显示前2个内容
            print(f"    - {content.get('type', 'unknown')}: {content.get('content', '')[:50]}...")
    
    print("\n" + "=" * 60)
    print("✓ 所有步骤完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
