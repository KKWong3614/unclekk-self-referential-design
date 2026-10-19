#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_demo.py —— 最小运行示例 / Minimal runnable example

一条命令跑完三个示例目录，直观看到 L0 / L2 / L3 三级的判定差异。
Runs the auditor against the three bundled fixtures and shows the L0/L2/L3
difference side by side.

用法 | Usage:
    python example/run_demo.py

无需任何第三方依赖 | No third-party dependencies.
"""

import os
import subprocess
import sys

# Windows 控制台中文输出保护 | Windows console UTF-8 guard
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT = os.path.join(os.path.dirname(HERE), "scripts", "selfref_audit.py")

CASES = [
    ("l0-demo", "只有提示词，没有元层 / prompt only, no meta layer"),
    ("l2-demo", "元层可编辑，但无不动点 / editable meta, no fixed point"),
    ("l3-demo", "元层可编辑 + 不动点 + 人类闸 / full L3 structure"),
]

BAR = "=" * 74


def run_case(name):
    d = os.path.join(HERE, name)
    p = subprocess.run(
        [sys.executable, AUDIT, d, "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if p.returncode != 0:
        return None, None, p.stderr.strip()
    import json
    r = json.loads(p.stdout)
    return r["level"], [g["id"] for g in r["gaps"]], None


def main():
    print(BAR)
    print("  自指自改进成熟度 —— 最小运行示例")
    print("  Self-Referential Maturity — minimal runnable example")
    print(BAR)

    if not os.path.isfile(AUDIT):
        print(f"找不到审计脚本 auditor not found: {AUDIT}", file=sys.stderr)
        return 1

    results = []
    for name, desc in CASES:
        level, gaps, err = run_case(name)
        if err:
            print(f"  [ERR] {name}: {err}")
            continue
        results.append((name, desc, level, gaps))
        print(f"\n  目录 {name}  ->  L{level}   缺口 gaps: {gaps or '无 none'}")
        print(f"       {desc}")

    print()
    print(BAR)
    print("  对照结论 | Takeaway")
    print(BAR)
    print("  L0 -> 慢，但安全      slow but safe")
    print("  L2 -> 看似变强，实则最危险  looks stronger, actually the most dangerous")
    print("  L3 -> 才应该追求的目标      the level you actually want")
    print()
    print("  亲手改一改试试 | Try it yourself:")
    print("    删掉 l3-demo/CONTRACT.md 再跑一次，L3 会立刻掉到 L2 并报 R1 致命缺口。")
    print("    Delete l3-demo/CONTRACT.md and re-run; L3 drops to L2 with a critical R1 gap.")
    print(BAR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
