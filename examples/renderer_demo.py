import sys
import os
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from conventionalrp.renderers.html_renderer import HTMLRenderer
from conventionalrp.renderers.markdown_renderer import MarkdownRenderer
from conventionalrp.renderers.json_renderer import JSONRenderer


TEST_DATA = [
    {
        "type": "dialogue",
        "speaker": "战士",
        "content": "我们需要更小心地前进，前面可能有陷阱。",
        "timestamp": "2024-01-15 20:30:15",
        "tags": ["对话", "警告"],
    },
    {
        "type": "dice",
        "speaker": "战士",
        "content": "d20+5",
        "result": 18,
        "timestamp": "2024-01-15 20:30:30",
    },
    {
        "type": "success",
        "content": "战士成功发现了隐藏的陷阱！",
        "timestamp": "2024-01-15 20:30:35",
    },
    {
        "type": "narration",
        "content": "昏暗的走廊中，石板地面上隐约可见一些不寻常的纹路。",
        "timestamp": "2024-01-15 20:31:00",
        "tags": ["环境描述"],
    },
    {
        "type": "dialogue",
        "speaker": "法师",
        "content": "让我施放侦测魔法，看看这里是否有魔法陷阱。",
        "timestamp": "2024-01-15 20:31:15",
    },
    {
        "type": "dice",
        "speaker": "法师",
        "content": "d20+8",
        "result": 23,
        "timestamp": "2024-01-15 20:31:20",
        "combat_data": {"type": "damage", "amount": 12, "total_damage": 12},
    },
    {
        "type": "system",
        "content": "法师侦测到前方10英尺处有一个魔法陷阱（火球术触发）。",
        "timestamp": "2024-01-15 20:31:25",
    },
]


def demo_html_themes():
    themes = ["light", "dark", "fantasy"]
    
    for theme in themes:
        print(f"\nGenerate {theme} theme...")
        renderer = HTMLRenderer(theme=theme)
        html_output = renderer.render(TEST_DATA)
        
        output_file = f"output_html_{theme}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_output)
        
def demo_html_custom_css():
    custom_css = """
    body {
        background-image: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
    }
    
    .token {
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    """
    
    renderer = HTMLRenderer(theme="light", custom_css=custom_css)
    html_output = renderer.render(TEST_DATA)
    
    output_file = "output_html_custom.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_output)
    

def demo_markdown_styles():
    renderer_full = MarkdownRenderer(enable_syntax_hints=True, enable_emoji=True)
    md_output_full = renderer_full.render(TEST_DATA)
    
    with open("output_markdown_full.md", "w", encoding="utf-8") as f:
        f.write(md_output_full)

    renderer_simple = MarkdownRenderer(enable_syntax_hints=False, enable_emoji=False)
    md_output_simple = renderer_simple.render(TEST_DATA)
    
    with open("output_markdown_simple.md", "w", encoding="utf-8") as f:
        f.write(md_output_simple)

    print(md_output_full[:100] + "...")


def demo_json_formats():
    renderer_pretty = JSONRenderer(pretty=True, indent=2)
    json_output_pretty = renderer_pretty.render(TEST_DATA)
    
    with open("output_json_pretty.json", "w", encoding="utf-8") as f:
        f.write(json_output_pretty)

    renderer_compact = JSONRenderer(pretty=False)
    json_output_compact = renderer_compact.render(TEST_DATA)
    
    with open("output_json_compact.json", "w", encoding="utf-8") as f:
        f.write(json_output_compact)
        
    renderer_sorted = JSONRenderer(pretty=True, indent=4, sort_keys=True)
    json_output_sorted = renderer_sorted.render(TEST_DATA)
    
    with open("output_json_sorted.json", "w", encoding="utf-8") as f:
        f.write(json_output_sorted)

def main():

    try:
        demo_html_themes()
        demo_html_custom_css()
        demo_markdown_styles()
        demo_json_formats()
        
    except Exception as e:
        print(f"\n{e!r}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
