# FAQ · 常见问题与坑点 | FAQ, Pitfalls & Before/After

> 中文在前，英文在后（SkillHub 规范）。| Chinese first, English after (SkillHub convention).
> 每条都配实例，不写空话。| Every answer carries a concrete example.

---

## Q1（新手）我的 Agent 只有几行提示词，用得上这个吗？

**用得上，而且你最该先看 L0 那一档。**
提示词少不代表不能自指——恰恰相反，**元层文件可以从零开始写，只有 4 个步骤**。
先跑一次审计看自己在哪一级，别急着上引擎。

跑法 | How:

```bash
python scripts/selfref_audit.py 你的Agent目录
```

**Yes — and L0 is exactly where you should start.** A short prompt is not a blocker.
Run the audit first to see your level before reaching for any engine.

---

## Q2（新手）L2 和 L3 到底差在哪？一句话说清

**差在"能不能被拦住"。**
L2 能改元层但没人拦，L3 能改元层且改元层必须先经过人。
**两者的外表几乎一样，区别只在有没有不动点和人类闸。**

**The difference is whether it can be stopped.** L2 can edit the meta-layer with no gate;
L3 can edit it, but only after human approval. They look nearly identical from outside.

---

## Q3 不动点该选哪几个文件？

选 **3 个**，少一个不够，多一个就僵化了：

| 角色 | 典型文件 | 为什么要锁 |
|---|---|---|
| 契约 | `CONTRACT.md` | 人类持有的目标与边界 |
| 引擎本体 | 实现闸门的脚本 | 防止闸门自己被拆 |
| 红线清单 | 禁止项列表 | 不可协商 |

完整可抄的模板见 `example/l3-demo/CONTRACT.md`。
A copy-ready template lives in `example/l3-demo/CONTRACT.md`.

---

## Q4（专业）能接进 CI 当硬闸吗？

能，两个闸门都带退出码：

```bash
python scripts/selfref_audit.py <dir> --strict          # 有致命/高缺口 → 退出码 3
python scripts/selfref_audit.py <dir> --assert-level 3  # 达不到 L3 → 退出码 4
```

已实跑验证：l2-demo 触发 **3** 和 **4**，l3-demo **全 0 通过**。
Verified by real runs: l2-demo exits 3 and 4; l3-demo exits 0.

---

## Q5 审计器会改我的文件吗？

**不会，全程只读。** 它只做三件事：读文件、数信号、打印结论。
唯一写操作是 `--json` 时的标准输出。
**Read-only.** It reads, counts signals, and prints. Nothing else.

---

## Q6 和 `metacog-self-evolve` 是什么关系？会重复吗？

**不重复，是设计期与运行期的分工。**
本 skill 只出诊断与改造方案（设计期）；`metacog-self-evolve` 负责记账、闸门、棘轮、回滚（运行期）。
审计到 L3 之后想真跑起来，去用它。
**Design-time vs run-time.** This skill diagnoses and plans; metacog executes.

---

## 坑点总结 | Pitfalls（都是实际踩出来的）

### 坑 1：文件名里的 "meta" 会骗过分类器

`_skillhub_meta.json` 这类**发布元数据**因文件名含 "meta"，
一度让一个普通 skill 被误报成 L2 危险区。

**已修**：现在必须**正文**里出现"如何改进/归因/提议"等信号才算元层，且排除 `_`、`.` 前缀与测试文件。
**Fixed**: body evidence is now mandatory; `_`-prefixed, dot-prefixed and test files are excluded.

### 坑 2：否定句也会被当成肯定信号（**v1.1.1 已修复**）

你在文件里写"本系统**没有**任何不动点"、"**不需要**人类确认"，
朴素关键词匹配会把它们当命中，**把危险的 L2 误判成 L3**——
这是安全审计器最糟的失效方向（假阴性）。开发示例时真实踩到过。

**修复（v1.1.1）**：信号词前 12 个字符内出现否定词
（没有 / 不存在 / 无需 / 不需要 / 缺少 / 尚未 / 未声明 / no / not / without …）
即作废该命中，报告里还会标注"已忽略 N 处否定语境命中"。中英文都生效。
回归测试 `scripts/test_regression.py` 第 C/E 两组专门守这个修复。

**残留边界 Residual**：否定词表是**有限清单**，
遇到绕着弯说"没有"的写法仍可能漏检；
所以说明性文字依旧建议放在被审计目录**之外**（如 `example/README.md`）。
**Fix (v1.1.1)**: negation cues within a 12-char window void the hit, and the
count is printed. The cue list is finite, so keep prose outside audited dirs anyway.

### 坑 3：效用分注水，棘轮反向固化垃圾

分数是唯一信任锚。若效用分能靠讨好评测刷上去，
棘轮会把垃圾固化成经验，还给你"变强了"的错觉。
**注水的棘轮比没有棘轮更糟。**
**A gamed ratchet is worse than no ratchet.**

### 坑 4：先放开元层、后补不动点 = 顺序反了

改造顺序**必须是**：抽元层 → 声明不动点 → 加人类闸 → 接评分回滚。
先放开再补闸，等于先出事再救火。
**Order matters**: extract → fix points → human gate → scoring/rollback.

### 坑 5：扫超大目录时结果可能不完整

审计器默认最多扫 500 个文件、5 层目录，超出即**截断**并在报告里标 `truncated`。
大仓库请显式加大上限：

```bash
python scripts/selfref_audit.py <dir> --max-files 3000 --max-depth 8
```

---

## 实际对照效果 | Before / After

以 `example/` 三个最小目录实跑对照（同一台机器、同一版本审计器）：

| 目录 | 结构差异 | 判定 | 缺口 |
|---|---|---|---|
| `l0-demo` | 只有 `prompt.md` | **L0** | G1 |
| `l2-demo` | 多了 `meta/evolve-policy.md` | **L2 危险区** | **R1 致命 + R2 致命** + G3, G4 |
| `l3-demo` | 再加 `CONTRACT.md` + `eval.json` + `ledger/archive.json` | **L3** | 无 |

**一行结论 One-liner**：
从 `l2-demo` 到 `l3-demo`，只多了 3 个文件，**两条致命缺口就消失了**。
From `l2-demo` to `l3-demo` — 3 extra files, and both CRITICAL gaps disappear.

**动手验证 Try it**：
删掉 `l3-demo/CONTRACT.md` 再跑一次，L3 立刻掉回 L2 并报 R1 致命缺口。
Delete `l3-demo/CONTRACT.md`, re-run, and L3 drops straight back to L2 with a critical R1 gap.
