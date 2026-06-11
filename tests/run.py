"""Zero-dependency test runner (pytest-compatible tests, stdlib discovery).

The test files follow pytest conventions (test_* functions, plain asserts),
so `pytest tests/` works as-is once pytest is installed. Until then:

    .venv/bin/python -m tests.run            # run everything
    .venv/bin/python -m tests.run offline    # only files matching the pattern
"""

import importlib
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from tests import Skip  # noqa: E402  (shared class — avoids __main__ dual-import)


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else ""
    passed = failed = skipped = 0
    for fname in sorted(os.listdir(HERE)):
        if not (fname.startswith("test_") and fname.endswith(".py")):
            continue
        if pattern and pattern not in fname:
            continue
        mod = importlib.import_module(f"tests.{fname[:-3]}")
        for name in sorted(dir(mod)):
            if not name.startswith("test_"):
                continue
            try:
                getattr(mod, name)()
                print(f"PASS  {fname}::{name}")
                passed += 1
            except Skip as e:
                print(f"SKIP  {fname}::{name}  ({e})")
                skipped += 1
            except Exception:
                print(f"FAIL  {fname}::{name}")
                traceback.print_exc(limit=3)
                failed += 1
    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
