import sys
import unittest
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def run_all_tests():
    loader = unittest.TestLoader()
    
    suite = loader.discover(
        start_dir=Path(__file__).parent,
        pattern='test_*.py'
    )
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
