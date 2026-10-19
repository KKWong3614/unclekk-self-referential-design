# 审计报告样例参考 | Audit Report Samples

> 以下三份输出均为**实跑捕获**，非手写示例。
> All three outputs below were **captured from real runs**, not hand-written.
> 捕获时间 Captured: 2026-09-03（样例一/二）· 2026-09-11（样例四）｜ 审计器版本 Auditor: v1.1.1

完整样例见 `example/` 目录，可自行复现：
Reproduce them yourself from the `example/` directory:

```bash
python example/run_demo.py                          # 一次跑完三个示例 | all three at once
python scripts/selfref_audit.py example/l2-demo     # 单个示例 | single fixture
```

---

## 样例一：L2 半开自指（危险区）| Sample 1: L2 Half-open (DANGER ZONE)

**输入 Input**：`example/l2-demo` —— 元层是可编辑的 Markdown，但没有不动点、没有人类确认闸。
An editable Markdown meta-layer, but no fixed point and no human-approval gate.

**看什么 What to look at**：两条 `致命 CRIT` 缺口（R1 / R2）。这是本 skill 最想拦住的情形。
Two CRITICAL gaps (R1/R2) — exactly what this skill exists to catch.

```
==============================================================
  自指自改进成熟度审计  |  Self-Referential Maturity Audit
  v1.1.1
==============================================================
  目录     Directory : <skill>/example/l2-demo
  扫描文件 Files     : 2
  判定     Verdict   : L2 半开自指（危险区）

  [结构组件 Components]
    元层存在    meta layer      : 有 yes
    元层可编辑  meta editable   : 有 yes
    不动点声明  fixed point     : —  no
    人类确认闸  human gate      : —  no
    变体库      archive         : —  no
    评分信号    eval signal     : —  no
    回滚机制    rollback        : 有 yes

  [识别为元层的文件 Meta-layer files]
    - meta\evolve-policy.md

  [识别为任务层的文件 Task-layer files]
    - prompt.md

  [缺口与风险 Gaps & Risks]
    [致命 CRIT] R1 元层可编辑，但没有声明任何不动点
        为什么 why  : 没有不可动的文件，安全约束会在若干代之后被 Agent 自己演化掉。这是自指结构最典型的失效方式。
        怎么做 fix  : 明确列出 2-3 个 Agent 禁止修改的文件（契约、红线、引擎本体），并在 SKILL.md 里写死。
    [致命 CRIT] R2 元层可编辑，但没有人类确认闸
        为什么 why  : 改「怎么改」是最高权限操作。缺了人类确认，一次误判会污染之后所有的改进。
        怎么做 fix  : 给元层改动加一道强制人类确认（如 --human-ok 参数或显式审批），缺确认则拒绝应用。
    [中  MED ] G3 没有可量化的评分信号
        为什么 why  : 没有分数就没有软奖励，进化循环无法择优，只能随机游走。
        怎么做 fix  : 定义一个 0~1 的效用分（任务达成度）与违规计数，每轮记录。
    [中  MED ] G4 没有变体库（archive）
        为什么 why  : 被否决的坏改动不留存，就会反复被重新提出来；也失去了跨任务累积改进的载体。
        怎么做 fix  : 建一个 archive.json / ledger，把被拒与回滚的改动连同原因存为负样本。

==============================================================
  下一步：先别急着放开元层。补齐不动点与人类确认闸，否则安全约束会被自己演化掉。
==============================================================
```

**解读 Reading**：七项组件里只中了三项，却已经"看起来能自我改进了"。
这正是 L2 的迷惑性——**它会伪装成变强，直到出事**。
Only 3 of 7 components present, yet it already "looks" self-improving. That is the trap.

---

## 样例二：L3 可控自指 | Sample 2: L3 Controlled self-reference

**输入 Input**：与 `example/l3-demo` 同构的真实 skill（元层可编辑 + 不动点 + 人类闸 + 评分 + 变体库 + 回滚）。
A real skill structurally identical to `example/l3-demo`.

**看什么 What to look at**：七项组件全中，缺口为空。
All seven components present, zero gaps.

```
==============================================================
  自指自改进成熟度审计  |  Self-Referential Maturity Audit
  v1.1.1
==============================================================
  目录     Directory : <skill>/example/l3-demo   # 与 L3 示例同构
  扫描文件 Files     : 3
  判定     Verdict   : L3 可控自指

  [结构组件 Components]
    元层存在    meta layer      : 有 yes
    元层可编辑  meta editable   : 有 yes
    不动点声明  fixed point     : 有 yes
    人类确认闸  human gate      : 有 yes
    变体库      archive         : 有 yes
    评分信号    eval signal     : 有 yes
    回滚机制    rollback        : 有 yes

  [识别为元层的文件 Meta-layer files]
    - SKILL.md
    - metacog.py
    - references\paper-notes.md

  [缺口与风险 Gaps & Risks] 未发现结构性缺口。No structural gaps found.

==============================================================
  结构已完整。重心从「建结构」转向「喂信号」—— 评分注水的棘轮比没有棘轮更糟。
==============================================================
```

**解读 Reading**：注意结尾提示——到了 L3，重心从"建结构"转向"喂信号"。
**评分注水的棘轮比没有棘轮更糟**，因为它会给你"变强了"的错觉。
Note the closing hint: at L3 the focus shifts from structure to signal quality.

---

## 样例三：四级对照速查 | Sample 3: Four-level cheat sheet

| 级别 | 元层 | 可编辑 | 不动点 | 人类闸 | 典型缺口 | 结论 |
|---|---|---|---|---|---|---|
| **L0** | 无 | — | — | — | G1 | 慢，但安全 |
| **L1** | 有 | 否 | — | — | G2 | 有天花板 |
| **L2** | 有 | 是 | 缺 或 缺 | 缺 | **R1 / R2 致命** | **最危险** |
| **L3** | 有 | 是 | 有 | 有 | 无 | 目标状态 |

**关键提醒 Key reminder**：**L2 比 L0 更危险**。L0 只是慢；L2 会伪装成变强，直到安全约束被自己演化掉。
**L2 is more dangerous than L0.** L0 is merely slow; L2 masquerades as progress.

---

## 样例四：否定句不算"已具备"（v1.1.1）| Sample 4: Negation is not evidence

**输入 Input**：元层文件里明写着"本系统**没有任何不动点**，也**不需要人类确认**"（中英文各一遍）。
A meta-layer file that literally says it has NO fixed point and needs NO human approval.

**看什么 What to look at**：`注 note` 那一行——审计器忽略了 4 处否定语境下的关键词命中，
**仍判 L2 危险区**并报 R1 / R2 致命。
**v1.1.1 之前，这个目录会被误判成 L3 可控**（假阴性，安全审计器最糟的失效方向）。
修复前后对照由 `scripts/test_regression.py` 的 C / E 两组守住。

```
==============================================================
  自指自改进成熟度审计  |  Self-Referential Maturity Audit
  v1.1.1
==============================================================
  目录     Directory : <否定句目录 negated-dir>
  扫描文件 Files     : 1
  判定     Verdict   : L2 半开自指（危险区）

  [结构组件 Components]
    元层存在    meta layer      : 有 yes
    元层可编辑  meta editable   : 有 yes
    不动点声明  fixed point     : —  no
    人类确认闸  human gate      : —  no
    变体库      archive         : —  no
    评分信号    eval signal     : —  no
    回滚机制    rollback        : —  no

  [识别为元层的文件 Meta-layer files]
    - meta\evolve-policy.md

  注 note：已忽略 4 处否定语境下的关键词命中（如「没有任何不动点」），不计为已具备。
          4 negated hits ignored (e.g. "no fixed point").

  [缺口与风险 Gaps & Risks]
    [致命 CRIT] R1 元层可编辑，但没有声明任何不动点
        为什么 why  : 没有不可动的文件，安全约束会在若干代之后被 Agent 自己演化掉。这是自指结构最典型的失效方式。
        怎么做 fix  : 明确列出 2-3 个 Agent 禁止修改的文件（契约、红线、引擎本体），并在 SKILL.md 里写死。
    [致命 CRIT] R2 元层可编辑，但没有人类确认闸
        为什么 why  : 改「怎么改」是最高权限操作。缺了人类确认，一次误判会污染之后所有的改进。
        怎么做 fix  : 给元层改动加一道强制人类确认（如 --human-ok 参数或显式审批），缺确认则拒绝应用。
    [高  HIGH] R3 没有回滚机制
        为什么 why  : 改错了无法撤销，自改进就退化成赌博。回滚是自指能长期跑下去的前提。
        怎么做 fix  : 用 git 托管配置目录，每次改动前留提交点；或实现 trial→verdict→revert 的状态机。
    [中  MED ] G3 没有可量化的评分信号
        为什么 why  : 没有分数就没有软奖励，进化循环无法择优，只能随机游走。
        怎么做 fix  : 定义一个 0~1 的效用分（任务达成度）与违规计数，每轮记录。
    [中  MED ] G4 没有变体库（archive）
        为什么 why  : 被否决的坏改动不留存，就会反复被重新提出来；也失去了跨任务累积改进的载体。
        怎么做 fix  : 建一个 archive.json / ledger，把被拒与回滚的改动连同原因存为负样本。

==============================================================
  下一步：先别急着放开元层。补齐不动点与人类确认闸，否则安全约束会被自己演化掉。
==============================================================
```

---

## 硬闸用法样例 | Hard-gate usage samples

把审计接进 CI，让结构退化无法合并 | Wire it into CI so structural regressions fail the build:

```bash
# 有致命/高缺口就失败（退出码 3）
# Fail on critical/high gaps (exit code 3)
python scripts/selfref_audit.py <dir> --strict

# 达不到 L3 就失败（退出码 4）
# Fail below L3 (exit code 4)
python scripts/selfref_audit.py <dir> --assert-level 3
```

实跑验证结果 | Verified by real runs:

| 命令 | 目录 | 退出码 | 含义 |
|---|---|---|---|
| `--strict` | l2-demo | **3** | 存在致命缺口，拦截 |
| `--assert-level 3` | l2-demo | **4** | 未达 L3，拦截 |
| `--strict` | l3-demo | **0** | 通过 |
| `--assert-level 3` | l3-demo | **0** | 通过 |
| `--assert-level 1` | l0-demo | **4** | 未达 L1，拦截 |
| （目录不存在） | NOPE | **1** | 参数错误 |
