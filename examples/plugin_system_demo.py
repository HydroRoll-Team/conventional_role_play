import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from conventionalrp.plugins import PluginManager
from conventionalrp.core.parser import Parser

sys.path.insert(0, str(Path(__file__).parent / "plugins"))
from dice_analyzer_plugin import DiceAnalyzerPlugin
from combat_tracker_plugin import CombatTrackerPlugin


def demo_basic_plugin_usage():
    manager = PluginManager()
    
    dice_analyzer = DiceAnalyzerPlugin()
    dice_analyzer.initialize()
    manager.register_plugin(dice_analyzer)
    
    combat_tracker = CombatTrackerPlugin()
    combat_tracker.initialize()
    manager.register_plugin(combat_tracker)

    print("\nRegistered Plugins:")
    for plugin_info in manager.list_plugins():
        print(f"  - {plugin_info['name']} v{plugin_info['version']} (type: {plugin_info['type']})")
    
    stats = manager.get_statistics()
    print(f"\nPlugin Statistics: {stats}")


def demo_processor_plugin():
    manager = PluginManager()
    
    combat_tracker = CombatTrackerPlugin()
    combat_tracker.initialize()
    manager.register_plugin(combat_tracker)
    
    combat_log = [
        {"type": "dialogue", "speaker": "战士", "content": "我攻击兽人，造成12点伤害！"},
        {"type": "dialogue", "speaker": "法师", "content": "火球术！造成28点火焰伤害"},
        {"type": "dialogue", "speaker": "牧师", "content": "治疗之光，恢复15点生命值"},
        {"type": "dialogue", "speaker": "战士", "content": "重击！造成18点伤害"},
        {"type": "dialogue", "speaker": "牧师", "content": "群体治疗，恢复10点生命值"},
    ]

    print("\nProcessing Combat Log:")
    from conventionalrp.plugins.base import ProcessorPlugin
    processed_log = manager.execute_plugins(combat_log, plugin_type=ProcessorPlugin)
    
    for token in processed_log:
        if "combat_data" in token:
            print(f"  {token['speaker']}: {token['content']}")
            print(f"    -> {token['combat_data']}")
    
    print("\nCombat Summary:")
    summary = combat_tracker.get_combat_summary()
    print(f"  总伤害: {summary['total_damage']}")
    print(f"  总治疗: {summary['total_healing']}")
    print(f"  净伤害: {summary['net_damage']}")
    print("\n  角色统计:")
    for character, stats in summary['character_stats'].items():
        print(f"    {character}: 造成伤害={stats['damage_dealt']}, 治疗={stats['healing_done']}")


def demo_analyzer_plugin():
    manager = PluginManager()
    
    dice_analyzer = DiceAnalyzerPlugin()
    dice_analyzer.initialize()
    manager.register_plugin(dice_analyzer)
    
    dice_rolls = [
        {"type": "dice", "content": "d20=15", "result": 15},
        {"type": "success", "content": "检定成功"},
        {"type": "dice", "content": "d6=4", "result": 4},
        {"type": "dice", "content": "d20=20", "result": 20},
        {"type": "success", "content": "大成功！Critical hit!"},
        {"type": "dice", "content": "d20=1", "result": 1},
        {"type": "failure", "content": "大失败..."},
        {"type": "dice", "content": "d20=12", "result": 12},
        {"type": "dice", "content": "d6=3", "result": 3},
        {"type": "success", "content": "检定成功"},
    ]

    print("\nDice Roll Data:")
    for roll in dice_rolls:
        if roll["type"] == "dice":
            print(f"  {roll['content']}")
    
    from conventionalrp.plugins.base import AnalyzerPlugin
    analysis = manager.execute_plugins(dice_rolls, plugin_type=AnalyzerPlugin)
    
    print("\nAnalyze result:")
    print(f"  总投掷次数: {analysis['total_rolls']}")
    print(f"  骰子类型分布: {analysis['dice_types']}")
    print(f"  成功次数: {analysis['success_count']}")
    print(f"  失败次数: {analysis['failure_count']}")
    print(f"  大成功次数: {analysis['critical_hits']}")
    print(f"  大失败次数: {analysis['critical_fails']}")
    print(f"  成功率: {analysis['success_rate']:.1%}")
    print(f"  出现极值比率: {analysis['critical_rate']:.1%}")


def demo_plugin_enable_disable():
    manager = PluginManager()
    dice_analyzer = DiceAnalyzerPlugin()
    dice_analyzer.initialize()
    manager.register_plugin(dice_analyzer)
    
    combat_tracker = CombatTrackerPlugin()
    combat_tracker.initialize()
    manager.register_plugin(combat_tracker)

    print("\nInitial State:")
    for plugin_info in manager.list_plugins():
        print(f"  {plugin_info['name']}: {'Enabled' if plugin_info['enabled'] else 'Disabled'}")

    # Disable DiceAnalyzer
    print("\nDisabling DiceAnalyzer...")
    manager.disable_plugin("DiceAnalyzer")
    
    print("\nCurrent State:")
    for plugin_info in manager.list_plugins():
        print(f"  {plugin_info['name']}: {'Enabled' if plugin_info['enabled'] else 'Disabled'}")

    print("\nRe-enabling DiceAnalyzer...")
    manager.enable_plugin("DiceAnalyzer")

    print("\nFinal State:")
    for plugin_info in manager.list_plugins():
        print(f"  {plugin_info['name']}: {'Enabled' if plugin_info['enabled'] else 'Disabled'}")


def demo_plugin_discovery():
    plugin_dir = Path(__file__).parent / "plugins"
    manager = PluginManager(plugin_dirs=[str(plugin_dir)])

    print(f"\nSearching for plugins in directory: {plugin_dir}")
    discovered = manager.discover_plugins()

    print(f"\nFound {len(discovered)} plugin modules:")
    for module in discovered:
        print(f"  - {module}")

    print("\nLoading plugins...")
    for py_file in plugin_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        
        plugin_class = manager.load_plugin_from_file(str(py_file))
        if plugin_class:
            print(f"  ✓ Successfully loaded: {py_file.name}")


def main():
    try:
        demo_basic_plugin_usage()
        demo_processor_plugin()
        demo_analyzer_plugin()
        demo_plugin_enable_disable()
        demo_plugin_discovery()
        
    except Exception as e:
        print(f"\n{e!r}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
