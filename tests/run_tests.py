#!/usr/bin/env python3
"""
测试套件运行器
运行所有单元测试
"""

import sys
import unittest
from pathlib import Path

# 添加 src 目录到路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def run_all_tests():
    """运行所有测试"""
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 从当前目录加载所有测试
    suite = loader.discover(
        start_dir=Path(__file__).parent,
        pattern='test_*.py'
    )
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
