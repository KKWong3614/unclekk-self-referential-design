---
name: unclekk-self-referential-design
slug: unclekk-self-referential-design
displayName: UncleKK Self-Referential Design
version: 1.1.1
summary: 自指自改进设计器——诊断你的 Agent 处于 L0~L3 哪一级，并给出把它改造成「能改进自己改法」的闭环方案。含零依赖审计脚本（可当 CI 硬闸）、最小运行示例与真实审计报告样例。
  Self-Referential Design — diagnose whether your Agent sits at L0~L3 and turn it into a system that can improve *how it improves itself*. Ships a zero-dependency auditor (usable as a CI hard gate), a minimal runnable example, and real audit report samples.
description: 诊断并改造 Agent 的自指自改进结构：判定 L0 人肉迭代 / L1 固定元层 / L2 半开自指（危险区）/ L3 可控自指，指出缺的不动点、人类确认闸、评分信号、变体库与回滚机制，并给四步改造路径。当用户提到「Agent 换个任务就拉胯」「只能人肉改提示词迭代」「元层可编辑」「元认知自修改」「自指自改进」「自进化系统设计」「担心安全约束被演化掉」，或需要评审某个 Agent/Skill 的自进化结构是否安全时使用。也适用于搭建自进化系统前的方案设计与 CI 结构门禁。
  Diagnose and redesign an Agent's self-referential structure: grade it L0 manual / L1 fixed meta-layer / L2 half-open (danger) / L3 controlled, surface missing fixed points, human-approval gates, scoring signals, variant archives and rollback, then give a four-step remediation path. Use when the user says the Agent "degrades on a new task", "only improves by hand-editing prompts", or asks about letting an Agent modify itself, editable meta-layers, metacognitive self-modification, self-referential self-improvement, designing self-evolving systems, Agents that get smarter with use, or worries that safety constraints will be evolved away. Also for pre-build design review and CI structural gating.
license: 设计思路参考 HyperAgents（arXiv:2603.19461，CC BY-NC-SA 4.0 非商用）；审计脚本为独立原创实现，仅限个人非商用。
  Design ideas reference HyperAgents (arXiv:2603.19461, CC BY-NC-SA 4.0 non-commercial); the auditor is an independent original implementation, personal non-commercial use only.
agent_created: true
---

# UncleKK 自指自改进设计器 | Self-Referential Design

你的 Agent 迭代慢，**根因通常不是模型笨，而是"怎么改进它"这件事被写死了**。
Your Agent iterates slowly not because the model is dumb, but because **how to improve it is hard-coded**.

改 Agent 时你在动两样东西：它手里的东西（提示词、规则、工具、记忆），以及"你怎么决定改哪里"。绝大多数人只开放了第一样。HyperAgents 的主张是——**第二样也要变成可编辑文件**：改规则的能力，本身也得能被改。
You improve two things: what the Agent holds, and how you decide *what to change*. Most people only open the first. HyperAgents says **open the second too**.

但要同时记住反例：Practice Makes Unsafe 实测 21 个自演化配置**全部**写出了不安全产物。所以本 skill 的另一半是——**自指必须有截断**。
But remember the counter-example: Practice Makes Unsafe found **all 21** self-evolving configs produced unsafe artifacts. So the other half of this skill is: **self-reference must have a cut-off**.

> **一句话总结 One-liner**：自指的充分条件不是"能改自己"，而是"**改错了能被拦住并回滚**"。
> The sufficient condition for self-reference is not "can edit itself" but "**mistakes get caught and rolled back**".

---

## 触发条件 | When this triggers（自动触发）

出现以下任一情形即可自动加载本 skill（无需显式点名）：
This skill auto-loads on any of the following:

| 你说的话 / 遇到的情况 | 例子 |
|---|---|
| Agent 换个任务就拉胯、泛化差 | "换个场景又要重调一遍" |
| 只能人肉迭代提示词 | "每次都得我自己改 prompt" |
| 想评估是否该让 Agent 自改 | "该不该开放让它自己改" |
| 讨论元层 / 元认知自修改 | "元层可编辑""改改法" |
| 设计自进化系统 | "想搭个会自我进化的 Agent" |
| 担心安全约束被演化掉 | "它会不会把安全规则自己改没了" |
| 评审某个 Skill 的自进化结构 | "帮我看看这个结构安全吗" |
| CI 里要卡结构退化 | "结构上不能倒退" |

---

## 适用受众 | Audience

**所有 Agent 用户，从新手到专业用户全覆盖。**
For every Agent user, from absolute beginner to professional.

- **新手 Beginner**：只有一个提示词文件也能用。先跑审计看自己在 L0，再按四步补。示例目录可直接抄。
  Works with a single prompt file. Run the audit, see L0, follow four steps. Copy the fixtures.
- **进阶 Intermediate**：已有提示词/规则/记忆分层，正打算加自改进循环——用审计确认别掉进 L2 危险区。
  Already layered prompts/rules/memory? Use the audit to avoid the L2 danger zone.
- **专业 Professional**：把 `--strict` / `--assert-level` 接进 CI 当结构门禁；参照 `references/paper-notes.md` 做方案取舍。
  Wire `--strict` / `--assert-level` into CI as a structural gate; use the paper notes for design trade-offs.

---

## 快速开始 | Quick start（3 步）

```bash
# 1) 审计：看自己在哪一级
python scripts/selfref_audit.py 你的Agent目录

# 2) 看最小示例：直观感受三级差异（一条命令）
python example/run_demo.py

# 3) 当硬闸用：结构不达标就失败
python scripts/selfref_audit.py 你的Agent目录 --strict
```

零第三方依赖，Python 3.8+，**只读不写**。
Zero dependencies, Python 3.8+, **read-only**.

---

## 四级成熟度 | Four maturity levels

| 级别 | 特征 | 症状 |
|---|---|---|
| **L0 人肉迭代** Manual | 没有元层文件 | 换个任务就拉胯，经验留不下来 |
| **L1 固定元层** Fixed | 有"怎么改"的规则，但写死在代码或人手里 | 只能在固定框架内打转 |
| **L2 半开自指** Half-open ⚠️ | 元层可编辑，但缺不动点或人类确认闸 | **短期变强，长期把安全约束自己演化掉** |
| **L3 可控自指** Controlled | 元层可编辑 + 不动点 + 人类确认闸 + 可回滚 | 改进机制本身能跨任务累积 |

**L2 是最危险的级别，不是 L0。** L0 只是慢，L2 会伪装成"变强了"直到出事。
**L2 is more dangerous than L0.** L0 is merely slow; L2 masquerades as progress.

---

## 改造流程 | Remediation（**硬上限 4 步**，顺序不可颠倒）

> 步数限制：**最多 4 步，没有第 5 步**。超过说明归因错了，回到第 2 步重判。
> Hard cap: **four steps, no fifth**. If you need more, the attribution is wrong — go back to step 2.

1. **抽出元层**：把硬编码在 `.py` 里的改进逻辑（propose / 归因 / 打分 / 回滚分支）写成 `meta/evolve-policy.md` 这类文本文件。→ 元层可编辑。
   Extract the hard-coded improvement logic into an editable text file.
2. **声明不动点**（**必须在放开元层之前**）：锁 3 类不可动文件——`CONTRACT.md`（统一不动点契约，SHE(L3) 与 metacog(L2) 共享的**单一真相源**）、引擎本体、红线清单，并在引擎里硬拦截。统一契约的权威定义见 `metacog-self-evolve/CONTRACT.md`，四工件 1:1 映射：`system_prompt / rule_bank / safety_memory / tool_policy` ≡ `A1 / A2 / A3 / A4`；闸门集为 SHE 三硬闸（备份/安全-效用/拒收池去重）与 metacog 三闸（G1 写入/G2 检索/G3 人类确认）的并集，任一不得削弱。
   Declare 3 classes of immutable files BEFORE opening the meta-layer: the unified CONTRACT.md (SSOT shared by SHE & metacog), the engine, the red-line list — and hard-block in the engine.
3. **加人类确认闸**：元层改动缺确认即拒绝应用。**不要用"提醒"代替"拦截"**——提醒会被看完继续干。
   Add a human-approval gate. **Warn ≠ block.**
4. **接评分与回滚**：0~1 效用分 + 违规计数；git 提交点或 `trial→verdict→revert`；变体库存负样本。
   Wire scoring, rollback, and a negative-sample archive.

> **这是本 skill 对论文的主动收窄**：HyperAgents 追求元层完全可编辑的开放式自加速；本 skill 认为个人 Agent 场景更需要可控性。代价是自加速变慢，收益是安全约束不会在若干代后被自己演化掉。
> **A deliberate narrowing of the paper**: we trade some self-acceleration speed for constraints that survive evolution.

---

## 元层开放后的三大风险 | Three risks after opening the meta-layer

前两条是致命级，审计器直接标红。First two are CRITICAL — the auditor flags them red.

1. **约束自删 R1**：无不动点时，安全规则会被当成"拖累效用的东西"优化掉。→ 第 2 步。
   Without fixed points, safety rules get optimized away as "utility drag".
2. **元层漂移 R2**：无人类闸时，一次对"如何改进"的误判会污染之后**所有**改进——坏的不是一条规则，是造规则的模具。→ 第 3 步。
   One bad meta-edit poisons every later improvement — the mold is broken, not one rule.
3. **评分注水 Gamed scoring**：分数是唯一信任锚。能刷分的棘轮会把垃圾固化成经验，**注水的棘轮比没有棘轮更糟**。
   A gameable ratchet cements garbage and tells you it got better.

---

## 硬代码保障 · 兜底 · 严格闭环 | Hard enforcement, fallback, closed loop

**不是纯声明式**：`scripts/selfref_audit.py` 是真实可执行的代码，且能给 CI 当闸门。
**Not declarative-only**: the auditor is real executable code and works as a CI gate.

**步数限制 Bounded work**（不会无限跑）：

| 上限 | 默认值 | 超限时行为 |
|---|---|---|
| 扫描文件数 `--max-files` | 500（硬上限 5000） | 截断，报告标 `truncated` |
| 扫描深度 `--max-depth` | 5（硬上限 20） | 停止下钻 |
| 单文件体积 | 400 KB | 跳过内容 |

**严格闭环 Closed loop**——每次运行必有唯一结论（L0~L3）+ 唯一下一步，退出码可判定：

| 退出码 | 含义 |
|---|---|
| 0 | 审计完成 / 通过 |
| 1 | 目录不存在 |
| 2 | 无可读文本文件 |
| 3 | `--strict`：存在致命/高缺口 |
| 4 | `--assert-level N`：未达指定级别 |
| 5 | 内部异常（**明确报"结果不可信"，不静默失败**） |

**兜底保障 Fallback**：目录不存在、无文本文件、内部异常各有独立退出码并打印原因；结果被截断时显式标注，绝不用不完整数据冒充完整结论。
Every failure mode has its own exit code and printed reason; truncated results are labeled, never passed off as complete.

**否定句不算"已具备" Negation-aware**：文件里写"本系统**没有**任何不动点""**不需要**人类确认"时，关键词确实出现了，但语义是"缺失"。审计器会作废这类命中，并在报告里标出忽略了几处——**绝不把危险的 L2 结构误判成 L3**（安全审计器最怕的假阴性）。改动脚本后跑 `scripts/test_regression.py` 验证。
"We have **no** fixed point" must not count as having one: such hits are dropped and counted. Never grade a dangerous L2 as L3.

---

## 资源索引 | Bundled resources（无孤立文档，全部可点）

| 文件 | 用途 |
|---|---|
| `scripts/selfref_audit.py` | 审计器（硬代码，零依赖，可当 CI 闸） |
| `scripts/test_regression.py` | 回归测试（16 项：三级判定 + 硬闸退出码 + 否定句修复 + 不误伤真阳性） |
| `example/README.md` | **最小运行示例说明**（新手先看这个） |
| `example/run_demo.py` | 一条命令跑完 L0/L2/L3 对照 |
| `example/l0-demo/` `example/l2-demo/` `example/l3-demo/` | 三个可直接抄的最小骨架 |
| `references/audit-report-sample.md` | **真实审计报告样例** + 硬闸退出码对照 |
| `references/faq.md` | FAQ · 坑点总结 · 实际对照效果 |
| `references/paper-notes.md` | 论文映射与一处主动设计分歧 |
| `README.md` | SkillHub 展示文档（**中文在前英文在后**） |
| `README_GITHUB.md` | GitHub 展示文档（**英文在前中文在后**，发布到 GitHub 时用） |

> 双语排序规范：**SkillHub 通道中文在前，GitHub 通道英文在前**。两份 README 内容一致、语序不同，按发布渠道取用。
> Bilingual ordering: **Chinese-first for SkillHub, English-first for GitHub.** Same content, different order.

---

## 论文依据 | Paper basis

核心对应（完整映射见 `references/paper-notes.md`）：

| 论文机制 | 本 skill 落地 |
|---|---|
| HyperAgents：task + meta agent 同程序 | 元层与任务层文件共处同一可编辑目录 |
| HyperAgents：元层可编辑 = 元认知自修改 | L2 / L3 的判据 |
| HyperAgents：archive + 软奖励 + git diff 回滚 | 第 4 步的变体库、效用分、回滚 |
| Practice Makes Unsafe：21/21 全军覆没 | 不动点与人类闸强制前置 |
| Self-Evolving Survey：四组件闭环 | 任务层（系统）→ 元层（优化器）分离审计 |

---

## 版本历史 | Changelog

| 版本 | 变更 |
|---|---|
| **1.1.1** | 修复假阴性缺陷：否定语境下的关键词不再算作"已具备"（如"没有任何不动点"不再被当成有不动点），中英文否定均生效；报告新增 `negation_filtered` 计数与提示行；新增回归测试 `scripts/test_regression.py`（16 项，含修复生效与不误伤真阳性） |
| **1.1.0** | 新增 CI 硬闸 `--strict` / `--assert-level`；新增扫描上限与截断标记；新增内部异常兜底（退出码 5）；补最小运行示例 `example/`；补真实审计报告样例与 FAQ |
| 1.0.0 | 首次发布：四级成熟度模型 + 审计脚本 |

---

## 什么时候别用 | When NOT to use

- **一次性任务**：没有反复迭代，元层没有演化对象。
  One-off tasks: nothing to evolve.
- **想要"装上就自动变强"的引擎**：本 skill 只做设计期诊断，运行时请用 `metacog-self-evolve`。
  Want a runtime engine? Use `metacog-self-evolve`.
- **无法给出效用分的场景**：评分注水会让整套机制失效，此时停在 L1 更稳。
  No honest utility score? Stay at L1.

## 统一不动点契约（与 SHE / metacog 共享）| Unified Fixed-Point Contract

本 skill 的「锁 3 个不动点」与 `metacog-self-evolve`（L2）、`unclekk-safety-harness-evolution`（L3 SHE）**指向同一份契约**——`metacog-self-evolve/CONTRACT.md` 是单一真相源（SSOT）。三者关系：

- 本 skill = **设计期编译器**：只读审计（判 L0~L3）、四步改造产出直接指向 `.metacog/` 骨架，**不另起炉灶**。
- `metacog-self-evolve` = **运行期引擎**：按 `.metacog/` 骨架记账、过闸、棘轮、回滚。
- SHE = **安全特化引擎**：护栏四工件 ≡ metacog 的 A1~A4，三硬闸是统一闸门集的 L3 子集。

四步改造的产出目录（与 `.metacog/` 对齐，审计器可直接识别）：

```
<你的Agent目录>/.metacog/
├── CONTRACT.md                 ← 人类持有，Agent 禁止修改（自指不动点，SSOT）
├── artifacts/
│   ├── A1-system-prompt.md     ← 角色与行为基线
│   ├── A2-rule-bank.md         ← 具体做法条目（演化主战场）
│   ├── A3-safety-memory.md     ← 安全记忆，APPEND-ONLY
│   └── A4-tool-policy.md       ← 工具与权限边界
├── meta/
│   └── M1-evolve-policy.md     ← ★ 元层：如何提议修改（可被演化，改需人类确认）
└── ledger/                     ← 账本：episodes / ratchet / archive + L1 优化器回流
```

> 审计器已能识别该布局：含 `CONTRACT.md` 即按 `.metacog/` 处理，并**断言 `meta/M1-evolve-policy.md` 存在**（缺失报 R4 critical）。可用 `selfref_audit.py <目录> --assert-level 3` 当 CI 硬闸。

## 与相邻技能的分工 | Division of labour

| 技能 | 管什么 | 关系 |
|---|---|---|
| `metacog-self-evolve` | 运行期引擎：记账、闸门、棘轮、回滚 | 与本 skill **共享 `CONTRACT.md` 统一契约**：本 skill 是设计期（编译器），它是运行期（引擎），引擎各自独立 |
| `unclekk-safety-harness-evolution` | 安全护栏四工件演化 | 互补：护栏四工件 ≡ metacog 的 A1~A4，三硬闸是统一闸门集的 L3 子集 |
| `skill-evolver` / `darwin-skill` / `skill-optimizer` | 优化单个 SKILL.md（L1 层） | 层级不同：那优化文件，本 skill 设计"优化机制"；其棘轮裁决回流进 `.metacog/ledger/` 作为 M1/A2 证据 |
