#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_regression.py —— selfref_audit 回归测试（零依赖，仅用标准库）

用法 | Usage
  python scripts/test_regression.py

覆盖 | Coverage
  A 三级示例判定不回退 (L0 / L2 / L3)
  B 硬闸退出码不变，CI 兼容 (3 / 4 / 0)
  C 坑2 修复：否定句不再被当成肯定信号
  D 不误伤真阳性：正向声明仍判 L3
  E 英文否定同样生效
  F 坑1：发布元数据（_skillhub_meta.json）仍被排除

改完 selfref_audit.py 后必跑；退出码 0 = 全过，1 = 有失败项。
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SCRIPT = os.path.join(HERE, "selfref_audit.py")
sys.path.insert(0, HERE)
import selfref_audit as m  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name + ("  | " + detail if detail else ""))


def mk(files):
    d = tempfile.mkdtemp(prefix="selfref_reg_")
    for rel, content in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
    return d


def run_cli(d, *args):
    r = subprocess.run([sys.executable, SCRIPT, d, *args],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout


def section(t):
    print()
    print("=" * 68)
    print(" " + t)
    print("=" * 68)


section("A. 三级示例判定不回退（regression）")
for d, lv in {"l0-demo": 0, "l2-demo": 2, "l3-demo": 3}.items():
    r = m.audit(os.path.join(SKILL, "example", d))
    check(f"{d} 判定 L{lv}", r["level"] == lv, r["level_name"])

section("B. 硬闸退出码不变（CI 兼容）")
l2 = os.path.join(SKILL, "example", "l2-demo")
l3 = os.path.join(SKILL, "example", "l3-demo")
check("l2 --strict → 3", run_cli(l2, "--strict")[0] == 3)
check("l2 --assert-level 3 → 4", run_cli(l2, "--assert-level", "3")[0] == 4)
check("l3 --strict → 0", run_cli(l3, "--strict")[0] == 0)
check("l3 --assert-level 3 → 0", run_cli(l3, "--assert-level", "3")[0] == 0)

section("C. 坑2 修复：否定句不再被当成肯定信号")
d = mk({
    "meta/evolve-policy.md": "# 改进策略\n如何改进：发现问题后归因，再提议修改。\n"
                             "注意：本系统没有任何不动点，也不需要人类确认。\n",
})
r = m.audit(d)
check("否定句目录不再判 L3", r["level"] == 2, r["level_name"])
check("仍报 R1（缺不动点）", any(g["id"] == "R1" for g in r["gaps"]))
check("仍报 R2（缺人闸）", any(g["id"] == "R2" for g in r["gaps"]))
check("negation_filtered 有计数", r.get("negation_filtered", 0) >= 2,
      f"={r.get('negation_filtered')}")
shutil.rmtree(d, ignore_errors=True)

section("D. 不误伤真阳性（正向声明仍判 L3）")
d = mk({
    "CONTRACT.md": "# 契约\n本契约是不动点，agent 禁止修改。\n",
    "meta/evolve-policy.md": "# 元层\n如何改进：归因后提议。\n"
                             "改动前必须人类确认，未经人工确认不得应用。\n",
    "eval.json": '{"score": 0.9, "utility": 0.8}',
    "ledger/archive.json": '{"archive": []}',
})
r = m.audit(d)
check("正向声明目录判 L3", r["level"] == 3, r["level_name"])
shutil.rmtree(d, ignore_errors=True)

section("E. 英文否定同样生效")
d = mk({
    "meta/evolve-policy.md": "# policy\nHow to improve: attribute then propose.\n"
                             "We have no fixed point and no human approval gate.\n",
})
r = m.audit(d)
check("英文 no + 信号词被过滤", not r["components"]["fixed_point"],
      f"fixed_point={r['components']['fixed_point']}")
check("未误判 L3", r["level"] != 3, r["level_name"])
shutil.rmtree(d, ignore_errors=True)

section("F. 坑1：发布元数据仍被排除")
d = mk({
    "_skillhub_meta.json": '{"name": "demo", "meta": {"v": "1.0"}}',
    "prompt.md": "# 系统提示\n你是助手。\n",
})
r = m.audit(d)
check("_skillhub_meta.json 未当元层", not r["meta_files"])
check("判 L0", r["level"] == 0, r["level_name"])
shutil.rmtree(d, ignore_errors=True)

section("结果 Summary")
failed = [n for n, ok, _ in results if not ok]
print(f"  合计 {len(results)} 项：通过 {len(results) - len(failed)}，失败 {len(failed)}")
for n in failed:
    print("   x " + n)
sys.exit(1 if failed else 0)
