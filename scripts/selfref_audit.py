#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selfref_audit.py —— 自指自改进成熟度审计器（零依赖，仅用标准库）
selfref_audit.py -- Self-Referential Maturity Auditor (zero-dependency, stdlib only)

用途 | Purpose
  给一个 Agent / Skill 的配置目录，判定它处在自指自改进的哪一级 (L0~L3)，
  并列出还差什么才能安全地把"改进方法本身"也开放给 Agent 去改。
  Given an Agent/Skill directory, grade it L0~L3 on self-referential maturity and
  list what is missing before you safely let the Agent edit "how it improves itself".

判定模型 | Grading model
  L0 人肉迭代   Manual iteration      没有元层。改什么、怎么改，全靠人决定。
  L1 固定元层   Fixed meta-layer      有"怎么改"的规则，但它写死在代码/人手里。
  L2 半开自指   Half-open (DANGER)    元层可编辑，但缺不动点或人类确认闸。
  L3 可控自指   Controlled self-ref   元层可编辑 + 不动点 + 人类确认闸 + 可回滚。

用法 | Usage
  python selfref_audit.py <目录>                # 人读报告 | human report
  python selfref_audit.py <目录> --json         # 机器读 | machine readable
  python selfref_audit.py <目录> --strict       # CI 硬闸：有致命/高缺口就非零退出
  python selfref_audit.py <目录> --assert-level 3   # 硬闸：达不到 L3 就非零退出
  python selfref_audit.py <目录> --max-files 500 --max-depth 5

退出码 | Exit codes
  0  审计完成（默认） | audit finished
  1  目录不存在 | directory missing
  2  目录下无可读文本文件 | no readable text files
  3  --strict：存在致命/高缺口 | critical/high gaps found
  4  --assert-level：未达指定级别 | level below required
  5  内部异常（兜底，报告降级但仍给结论） | internal error (degraded)
"""

import argparse
import json
import os
import re
import sys
import traceback

AUDIT_VERSION = "1.1.1"

# Windows 控制台中文输出保护 | Windows console UTF-8 guard
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ---------------------------------------------------------------- 扫描上限（步数限制）
# Hard scan limits -- bounded work, never unbounded. Defaults are generous but finite.

DEFAULT_MAX_FILES = 500      # 最多读多少个文件
DEFAULT_MAX_DEPTH = 5        # 最多扫多少层目录
MAX_FILE_BYTES = 400_000     # 单文件超过则跳过内容（防巨型文件拖死）
HARD_MAX_FILES = 5_000       # 用户再怎么设也不许超过这个数

SKIP_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "__pycache__", ".venv", "venv",
    ".idea", ".vscode", "dist", "build", ".next", ".cache", "site-packages",
}

TEXT_EXT = {
    ".md", ".txt", ".py", ".sh", ".bash", ".ps1", ".yaml", ".yml",
    ".json", ".toml", ".cfg", ".ini", ".js", ".ts",
}

# ---------------------------------------------------------------- 信号词表 | Signal lexicon

# 「元层」= 规定"如何改进"的文件 | meta-layer = files that define HOW to improve
META_NAME = [
    "meta", "evolve", "evolution", "improve", "policy", "self-", "self_",
    "ratchet", "gate", "propose", "verdict",
    "元", "策略", "改进", "演化", "进化",
]
META_BODY = [
    "如何改进", "怎么改", "改进方式", "改进规则", "提议", "归因", "闸门",
    "棘轮", "回滚", "元层", "自指", "不动点", "自修改", "自演化",
    "evolve-policy", "meta agent", "meta-agent", "meta layer",
    "how to improve", "self-modif", "self-modifying", "attribut",
    "human-ok", "human_ok", "requires_human",
]

# 「任务层」= 被改的对象 | task-layer = the artifacts being improved
TASK_NAME = [
    "prompt", "rule", "memory", "tool", "skill", "agent", "spec",
    "提示", "规则", "记忆", "工具",
]
TASK_BODY = [
    "系统提示", "角色", "工具清单", "规则库", "安全记忆", "system prompt",
    "rule bank", "safety memory", "tool policy",
]

# 「不动点」= Agent 不可改的文件/约束 | fixed points = files the Agent must not edit
FIXPOINT_BODY = [
    "不动点", "不可修改", "禁止修改", "不可演化", "不可动", "人类持有",
    "immutable", "fixed point", "do not edit", "agent 禁止",
    "agent禁止", "红线",
]

# 「人类确认闸」| human-approval gate
HUMANGATE_BODY = [
    "人类确认", "人工确认", "需人类", "--human-ok", "human-ok",
    "requires_human", "human approval", "需用户确认", "向用户确认",
]

# 「变体库 / 累积」| archive of variants
ARCHIVE_NAME = ["archive", "ledger", "history", "variant", "归档", "账本", "档案"]
ARCHIVE_BODY = ["archive", "ledger", "变体", "负样本", "档案库", "episode"]

# 「评测打分」| evaluation signal
EVAL_NAME = ["eval", "score", "benchmark", "metric", "评测", "评分"]
EVAL_BODY = ["utility", "score", "评分", "效用", "打分", "sc:", "score:"]

# 「回滚机制」| rollback mechanism
ROLLBACK_BODY = ["回滚", "revert", "rollback", "git checkout", "git restore",
                 "撤销", "revoked", "trial"]


# ---------------------------------------------------------------- 工具函数 | Helpers

def walk_files(root, max_depth, max_files):
    """收集目录下的文本文件，受 max_depth / max_files 双重限制。
    Collect text files under root, bounded by max_depth AND max_files.

    返回 (files, truncated)。| Returns (files, truncated_flag).
    """
    out = []
    truncated = False
    root = os.path.abspath(root)
    base_depth = root.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        depth = dirpath.count(os.sep) - base_depth
        if depth >= max_depth:
            dirnames[:] = []
        for fn in filenames:
            if len(out) >= max_files:
                truncated = True
                return out, truncated
            ext = os.path.splitext(fn)[1].lower()
            if ext and ext not in TEXT_EXT:
                continue
            ap = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(ap) > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            out.append((os.path.relpath(ap, root), ap))
    return out, truncated


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


# 「否定语境」词表：信号词前面出现这些词 = 声明缺失，不是已具备
# Negation cues: if one appears right BEFORE a signal word, the hit means
# "this is missing", not "this exists".
NEGATION = [
    "没有", "不存在", "无", "无需", "不需要", "不必", "缺少", "缺乏",
    "尚未", "还没", "未声明", "未设置", "未提供", "未配置", "未启用", "未加",
    "no ", "not ", "never", "without", "lack", "none",
]
NEG_WINDOW = 12      # 往前看多少个字符 | how far back we look for a cue


def hits_negaware(text, words, window=NEG_WINDOW):
    """关键词命中，但**排除否定语境**下的命中。

    Keyword hits, minus hits that occur in a negated context.

    为什么需要：文件里写"本系统**没有**任何不动点""**不需要**人类确认"时，
    朴素的关键词匹配会把这些"声明缺失"当成"已经具备"，
    把危险的 L2 结构**误判成 L3**——对一个安全审计器来说，
    这是最糟糕的失效方向（假阴性）。因此否定窗口内的命中一律作废。

    Why: "we have NO fixed point" / "human approval NOT required" would
    otherwise count as positive evidence and grade a dangerous L2 as L3.
    A false negative is the worst failure mode for a safety auditor.
    """
    low = text.lower()
    valid, negated = set(), 0
    for w in words:
        wl = w.lower()
        start = 0
        while True:
            pos = low.find(wl, start)
            if pos < 0:
                break
            head = low[max(0, pos - window):pos]
            if any(n in head for n in NEGATION):
                negated += 1
                start = pos + 1
                continue
            valid.add(w)
            break
    return valid, negated


def hits(text, words):
    """返回命中的关键词集合（大小写不敏感）。| Case-insensitive keyword hits."""
    low = text.lower()
    return {w for w in words if w.lower() in low}


def is_noise(rel):
    """排除不该参与分层判定的文件：打包元数据、隐藏文件、测试文件。
    Exclude packaging metadata, hidden files and tests from layer classification.

    理由：_skillhub_meta.json 只是发布元数据，却被文件名里的 "meta" 命中，
    会让一个普通 skill 被误判成"有元层"。这是本项目实际修掉的一个缺陷。
    """
    base = os.path.basename(rel)
    if base.startswith("_") or base.startswith("."):
        return True
    if base.startswith("test_") or base.startswith("conftest"):
        return True
    parts = rel.replace("\\", "/").split("/")
    if any(p in ("tests", "test", "__tests__", "spec") for p in parts[:-1]):
        return True
    return False


def classify(rel, body):
    """判定单个文件属于元层 / 任务层 / 中性。| Classify a file into meta/task/neutral.

    关键规则：**必须有正文证据**。光文件名带 "meta" 不算元层。
    Key rule: BODY evidence is mandatory. A filename containing "meta" is not enough.
    """
    if is_noise(rel):
        return "skip", set()

    name = os.path.basename(rel).lower()
    head = body[:6000]          # 只看前 6000 字符，够用且快 | scan head only, fast
    b_meta = hits(head, META_BODY)
    b_task = hits(head, TASK_BODY)
    n_meta = hits(name, META_NAME)
    n_task = hits(name, TASK_NAME)

    is_meta = len(b_meta) >= 2 or (len(b_meta) >= 1 and len(n_meta) >= 1)
    is_task = len(b_task) >= 2 or (len(b_task) >= 1 and len(n_task) >= 1)

    if is_meta and is_task:
        return ("meta" if len(b_meta) >= len(b_task) else "task"), (b_meta | b_task)
    if is_meta:
        return "meta", b_meta
    if is_task:
        return "task", b_task
    return "neutral", set()


# ---------------------------------------------------------------- 审计主体 | Audit core

def audit(root, max_depth=DEFAULT_MAX_DEPTH, max_files=DEFAULT_MAX_FILES):
    """审计一个目录，返回结果字典。| Audit a directory, return result dict."""
    files, truncated = walk_files(root, max_depth, max_files)
    if not files:
        return None

    meta_files, task_files = [], []
    fixpoint_hits, humangate_hits = set(), set()
    archive_hits, eval_hits, rollback_hits = set(), set(), set()
    negated_total = 0
    has_git = os.path.isdir(os.path.join(root, ".git"))

    for rel, ap in files:
        body = read_text(ap)
        kind, _ev = classify(rel, body)
        if kind == "meta":
            meta_files.append(rel)
        elif kind == "task":
            task_files.append(rel)

        # 全局信号扫描（全库聚合，不只看元层文件）| scan whole tree for signals
        _fp, _n = hits_negaware(body, FIXPOINT_BODY)
        fixpoint_hits |= _fp
        negated_total += _n
        _hg, _n = hits_negaware(body, HUMANGATE_BODY)
        humangate_hits |= _hg
        negated_total += _n
        _rb, _n = hits_negaware(body, ROLLBACK_BODY)
        rollback_hits |= _rb
        negated_total += _n

        nm = os.path.basename(rel).lower()
        _a1, _n1 = hits_negaware(nm, ARCHIVE_NAME)
        _a2, _n2 = hits_negaware(body, ARCHIVE_BODY)
        archive_hits |= _a1 | _a2
        negated_total += _n1 + _n2
        _e1, _n1 = hits_negaware(nm, EVAL_NAME)
        _e2, _n2 = hits_negaware(body, EVAL_BODY)
        eval_hits |= _e1 | _e2
        negated_total += _n1 + _n2

    has_meta = len(meta_files) > 0

    # 元层是否"可编辑"：元层里存在文本型配置文件（而非只有 .py 代码常量）
    # Editable = the meta layer contains text config, not only hard-coded .py constants
    meta_editable = False
    for rel in meta_files:
        ext = os.path.splitext(rel)[1].lower()
        if ext in (".md", ".yaml", ".yml", ".json", ".txt", ".toml", ".ini", ".cfg"):
            meta_editable = True
            break

    has_fixpoint = len(fixpoint_hits) > 0
    has_humangate = len(humangate_hits) > 0
    has_archive = len(archive_hits) > 0
    has_eval = len(eval_hits) > 0
    has_rollback = len(rollback_hits) > 0 or has_git

    # ---- 定级 | grading
    if not has_meta:
        level, level_name, level_en = 0, "L0 人肉迭代", "L0 Manual iteration"
    elif not meta_editable:
        level, level_name, level_en = 1, "L1 固定元层", "L1 Fixed meta-layer"
    elif meta_editable and has_fixpoint and has_humangate:
        level, level_name, level_en = 3, "L3 可控自指", "L3 Controlled self-reference"
    else:
        level, level_name, level_en = 2, "L2 半开自指（危险区）", "L2 Half-open (DANGER ZONE)"

    # ---- 缺口与风险 | gaps and risks
    gaps = []
    if level == 0:
        gaps.append({
            "id": "G1", "severity": "high",
            "gap": "找不到任何元层文件",
            "gap_en": "No meta-layer file found",
            "why": "「改什么、怎么改」没有落成文件，全靠人当场判断，无法被改进，也无法被审计。",
            "action": "新建一份 meta/ 目录，写下「发现问题→归因到哪个文件→提议→验收」的规则，用 Markdown 而非代码常量。",
        })
    if level == 1:
        gaps.append({
            "id": "G2", "severity": "high",
            "gap": "元层不可编辑（写死在代码或人手里）",
            "gap_en": "Meta-layer is not editable (hard-coded)",
            "why": "这正是论文说的速度上限：改进方式本身永远不变，系统只能在固定框架内打转。",
            "action": "把「如何改进」从 .py 常量里抽出来，写成可被 Agent 读写的 .md 文件，进入可演化清单。",
        })
    if has_meta and meta_editable and not has_fixpoint:
        gaps.append({
            "id": "R1", "severity": "critical",
            "gap": "元层可编辑，但没有声明任何不动点",
            "gap_en": "Editable meta-layer without any fixed point",
            "why": "没有不可动的文件，安全约束会在若干代之后被 Agent 自己演化掉。这是自指结构最典型的失效方式。",
            "action": "明确列出 2-3 个 Agent 禁止修改的文件（契约、红线、引擎本体），并在 SKILL.md 里写死。",
        })
    if has_meta and meta_editable and not has_humangate:
        gaps.append({
            "id": "R2", "severity": "critical",
            "gap": "元层可编辑，但没有人类确认闸",
            "gap_en": "Editable meta-layer without a human-approval gate",
            "why": "改「怎么改」是最高权限操作。缺了人类确认，一次误判会污染之后所有的改进。",
            "action": "给元层改动加一道强制人类确认（如 --human-ok 参数或显式审批），缺确认则拒绝应用。",
        })
    if has_meta and meta_editable and not has_rollback:
        gaps.append({
            "id": "R3", "severity": "high",
            "gap": "没有回滚机制",
            "gap_en": "No rollback mechanism",
            "why": "改错了无法撤销，自改进就退化成赌博。回滚是自指能长期跑下去的前提。",
            "action": "用 git 托管配置目录，每次改动前留提交点；或实现 trial→verdict→revert 的状态机。",
        })
    if has_meta and meta_editable and not has_eval:
        gaps.append({
            "id": "G3", "severity": "medium",
            "gap": "没有可量化的评分信号",
            "gap_en": "No quantifiable scoring signal",
            "why": "没有分数就没有软奖励，进化循环无法择优，只能随机游走。",
            "action": "定义一个 0~1 的效用分（任务达成度）与违规计数，每轮记录。",
        })
    if has_meta and meta_editable and not has_archive:
        gaps.append({
            "id": "G4", "severity": "medium",
            "gap": "没有变体库（archive）",
            "gap_en": "No variant archive",
            "why": "被否决的坏改动不留存，就会反复被重新提出来；也失去了跨任务累积改进的载体。",
            "action": "建一个 archive.json / ledger，把被拒与回滚的改动连同原因存为负样本。",
        })

    # ---- 统一契约断言（A）：识别 .metacog/ 布局，断言 M1 元层策略存在
    # Unified-contract assertion: if this is a .metacog/ layout, M1 (the
    # meta-layer "how to improve" policy) MUST exist, or the self-referential
    # closure has no editable meta-layer to evolve.
    _is_metacog = (os.path.basename(root.rstrip(os.sep)) == ".metacog"
                   or os.path.isfile(os.path.join(root, "CONTRACT.md")))
    if _is_metacog:
        m1_names = {"m1-evolve-policy.md", "evolve-policy.md"}
        m1_exists = any(
            os.path.basename(rel).lower() in m1_names
            and "meta" in rel.replace("\\", "/").split("/")
            for rel, _ in files
        )
        if not m1_exists:
            gaps.append({
                "id": "R4", "severity": "critical",
                "gap": ".metacog/ 布局下缺失 M1 元层策略文件",
                "gap_en": "Missing M1 meta-layer policy under .metacog/",
                "why": "M1 规定「如何改进」，是元认知自修改的核心。缺 M1，自指闭包没有可演化的元层，退化成只能改行为、改不了改法。",
                "action": "新建 meta/M1-evolve-policy.md，写下「如何提议修改」的规则（归因优先级 + 提议标准 + 元层自省触发条件）。",
            })

    return {
        "audit_version": AUDIT_VERSION,
        "root": os.path.abspath(root),
        "files_scanned": len(files),
        "truncated": truncated,
        "negation_filtered": negated_total,
        "level": level,
        "level_name": level_name,
        "level_name_en": level_en,
        "components": {
            "meta_layer": has_meta,
            "meta_editable": meta_editable,
            "fixed_point": has_fixpoint,
            "human_gate": has_humangate,
            "archive": has_archive,
            "eval_signal": has_eval,
            "rollback": has_rollback,
        },
        "meta_files": sorted(meta_files)[:12],
        "task_files": sorted(task_files)[:12],
        "evidence": {
            "fixed_point": sorted(fixpoint_hits)[:8],
            "human_gate": sorted(humangate_hits)[:8],
            "archive": sorted(archive_hits)[:8],
            "eval": sorted(eval_hits)[:8],
            "rollback": sorted(rollback_hits)[:8],
        },
        "gaps": gaps,
    }


# ---------------------------------------------------------------- 报告输出 | Report

BAR = "=" * 62

TIPS = {
    0: "下一步：先造一个元层文件，把「怎么改」写下来。写不出来的部分，就是你人肉迭代的黑箱。",
    1: "下一步：把「怎么改」从代码里抽出来变成可编辑文件 —— 这一步做完，系统才谈得上自指。",
    2: "下一步：先别急着放开元层。补齐不动点与人类确认闸，否则安全约束会被自己演化掉。",
    3: "结构已完整。重心从「建结构」转向「喂信号」—— 评分注水的棘轮比没有棘轮更糟。",
}


def render(r):
    print(BAR)
    print("  自指自改进成熟度审计  |  Self-Referential Maturity Audit")
    print(f"  v{r['audit_version']}")
    print(BAR)
    print(f"  目录     Directory : {r['root']}")
    print(f"  扫描文件 Files     : {r['files_scanned']}"
          + ("  (已截断 truncated)" if r["truncated"] else ""))
    print(f"  判定     Verdict   : {r['level_name']}")
    print()

    c = r["components"]
    tick = lambda b: "有 yes" if b else "—  no"
    print("  [结构组件 Components]")
    print(f"    元层存在    meta layer      : {tick(c['meta_layer'])}")
    print(f"    元层可编辑  meta editable   : {tick(c['meta_editable'])}")
    print(f"    不动点声明  fixed point     : {tick(c['fixed_point'])}")
    print(f"    人类确认闸  human gate      : {tick(c['human_gate'])}")
    print(f"    变体库      archive         : {tick(c['archive'])}")
    print(f"    评分信号    eval signal     : {tick(c['eval_signal'])}")
    print(f"    回滚机制    rollback        : {tick(c['rollback'])}")

    if r["meta_files"]:
        print()
        print("  [识别为元层的文件 Meta-layer files]")
        for f in r["meta_files"]:
            print(f"    - {f}")
    if r["task_files"]:
        print()
        print("  [识别为任务层的文件 Task-layer files]")
        for f in r["task_files"]:
            print(f"    - {f}")

    if r.get("negation_filtered", 0):
        print()
        print(f"  注 note：已忽略 {r['negation_filtered']} 处否定语境下的关键词命中"
              f"（如「没有任何不动点」），不计为已具备。")
        print(f"          {r['negation_filtered']} negated hits ignored "
              f"(e.g. \"no fixed point\").")

    print()
    if r["gaps"]:
        print("  [缺口与风险 Gaps & Risks]")
        sev = {"critical": "致命 CRIT", "high": "高  HIGH",
               "medium": "中  MED ", "low": "低  LOW "}
        for g in r["gaps"]:
            print(f"    [{sev.get(g['severity'], g['severity'])}] {g['id']} {g['gap']}")
            print(f"        为什么 why  : {g['why']}")
            print(f"        怎么做 fix  : {g['action']}")
    else:
        print("  [缺口与风险 Gaps & Risks] 未发现结构性缺口。No structural gaps found.")

    print()
    print(BAR)
    print(f"  {TIPS[r['level']]}")
    print(BAR)


def main():
    ap = argparse.ArgumentParser(
        description="审计一个 Agent/Skill 目录的自指自改进成熟度（L0~L3）。")
    ap.add_argument("path", help="要审计的目录 | directory to audit")
    ap.add_argument("--json", action="store_true", help="输出 JSON | JSON output")
    ap.add_argument("--strict", action="store_true",
                    help="硬闸：存在致命/高缺口时退出码 3 | fail (3) on critical/high gaps")
    ap.add_argument("--assert-level", type=int, default=None, choices=[0, 1, 2, 3],
                    help="硬闸：低于该级别时退出码 4 | fail (4) below this level")
    ap.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH,
                    help=f"扫描深度，默认 {DEFAULT_MAX_DEPTH} | scan depth")
    ap.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES,
                    help=f"最多扫描文件数，默认 {DEFAULT_MAX_FILES} | max files")
    ap.add_argument("--version", action="version",
                    version=f"selfref_audit {AUDIT_VERSION}")
    a = ap.parse_args()

    # 兜底保障 | fallback guard: never crash silently, always emit a verdict
    try:
        max_files = min(max(1, a.max_files), HARD_MAX_FILES)
        max_depth = min(max(1, a.max_depth), 20)

        if not os.path.isdir(a.path):
            print(f"错误 Error：目录不存在 directory not found —— {a.path}", file=sys.stderr)
            return 1

        r = audit(a.path, max_depth, max_files)
        if r is None:
            print(f"错误 Error：目录下没有可读取的文本文件 no readable text files —— {a.path}",
                  file=sys.stderr)
            return 2

        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            render(r)

        # 严格闭环：硬闸判定 | closed loop: hard gates
        if a.strict and any(g["severity"] in ("critical", "high") for g in r["gaps"]):
            return 3
        if a.assert_level is not None and r["level"] < a.assert_level:
            return 4
        return 0

    except Exception:
        # 兜底：内部异常时明确报降级，而不是静默失败
        # Fallback: report degradation loudly instead of failing silently
        print("错误 Error：审计过程发生内部异常，结果不可信。", file=sys.stderr)
        print("Internal error during audit; result is NOT trustworthy.", file=sys.stderr)
        traceback.print_exc()
        return 5


if __name__ == "__main__":
    sys.exit(main())
