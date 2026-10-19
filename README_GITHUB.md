# UncleKK Self-Referential Design

> English first, Chinese after (GitHub convention). | 英文在前，中文在后（GitHub 规范）。
> Version | 版本: **1.1.1**

Diagnose which **self-referential maturity** level your Agent sits at, and turn it into a system that can improve *how it improves itself*.
诊断你的 Agent 处在**自指自改进**的哪一级，并把它改造成「能改进自己改法」的系统。

---

## One-liner | 一句话

Your Agent iterates slowly not because the model is dumb, but because **how to improve it is hard-coded**.
你的 Agent 迭代慢，**根因通常不是模型笨，而是"怎么改进它"这件事被写死了**。

The sufficient condition for self-reference is not "can edit itself" but "**mistakes get caught and rolled back**".
自指的充分条件不是"能改自己"，而是"**改错了能被拦住并回滚**"。

---

## Four maturity levels | 四级成熟度

| Level | Trait | Symptom |
|---|---|---|
| **L0** Manual | No meta-layer file | Degrades on every new task; nothing is retained |
| **L1** Fixed meta-layer | "How to improve" rules exist but are hard-coded in code | Stuck inside a fixed frame |
| **L2** Half-open ⚠️ | Editable meta-layer, but no fixed point or human-approval gate | **Looks stronger short-term, evolves its own safety rules away long-term** |
| **L3** Controlled | Editable meta-layer + fixed points + human gate + rollback | The improvement mechanism itself compounds across tasks |

| 级别 | 特征 | 症状 |
|---|---|---|
| **L0** 人肉迭代 | 没有元层文件 | 换个任务就拉胯，经验留不下来 |
| **L1** 固定元层 | 有"怎么改"的规则，但写死在代码里 | 只能在固定框架内打转 |
| **L2** 半开自指 ⚠️ | 元层可编辑，但缺不动点或人类确认闸 | **短期变强，长期把安全约束自己演化掉** |
| **L3** 可控自指 | 元层可编辑 + 不动点 + 人类确认闸 + 可回滚 | 改进机制本身能跨任务累积 |

**L2 is more dangerous than L0.** L0 is merely slow; L2 masquerades as progress.
**L2 比 L0 更危险。** L0 只是慢；L2 会伪装成"变强了"直到出事。

---

## Quick start | 快速开始

```bash
# 1) Audit: see your level | 审计：看自己在哪一级
python scripts/selfref_audit.py your-agent-dir

# 2) Minimal example: three levels in one command | 跑最小示例：一条命令看三级对照
python example/run_demo.py

# 3) Use as a CI hard gate | 当 CI 硬闸用
python scripts/selfref_audit.py your-agent-dir --strict
```

Zero dependencies, Python 3.8+, **read-only**.
零第三方依赖，Python 3.8+，**只读不写**。

---

## Remediation | 改造流程（hard cap: 4 steps, order matters）

> **Four steps, no fifth.** Need more? The attribution is wrong — go back to step 2.
> **最多 4 步，没有第 5 步。** 超过说明归因错了，回到第 2 步重判。

1. **Extract the meta-layer**: move hard-coded improvement logic out of `.py` into an editable text file such as `meta/evolve-policy.md`.
   **抽出元层**：把硬编码在 `.py` 里的改进逻辑写成 `meta/evolve-policy.md` 这类文本文件。
2. **Declare fixed points** (BEFORE opening the meta-layer): lock three files — the contract, the engine body, and the red-line list.
   **声明不动点**（必须在放开元层之前）：锁 3 个文件——契约、引擎本体、红线清单。
3. **Add a human-approval gate**: reject meta-layer edits without approval. **Warn ≠ block.**
   **加人类确认闸**：元层改动缺确认即拒绝应用。**不要用"提醒"代替"拦截"。**
4. **Wire scoring and rollback**: a 0~1 utility score plus violation counts; git commit points or `trial→verdict→revert`; archive negative samples.
   **接评分与回滚**：0~1 效用分 + 违规计数；git 提交点或 `trial→verdict→revert`；变体库存负样本。

---

## Hard enforcement | 硬代码保障

Not declarative-only: `scripts/selfref_audit.py` is real executable code and works as a CI gate.
不是纯声明式——审计脚本是真实可执行代码，能给 CI 当闸门。

| Exit code | Meaning | 含义 |
|---|---|---|
| 0 | Audit finished / passed | 审计完成 / 通过 |
| 1 | Directory missing | 目录不存在 |
| 2 | No readable text files | 无可读文本文件 |
| 3 | `--strict`: critical/high gaps | 存在致命/高缺口 |
| 4 | `--assert-level N`: below required level | 未达指定级别 |
| 5 | Internal error (**reported loudly**) | 内部异常（明确报"结果不可信"） |

Bounded scan (never runs forever): 500 files, depth 5, 400 KB per file. Truncation is always labeled.
扫描上限（不会无限跑）：文件数 500、深度 5、单文件 400 KB，超限即截断并显式标注。

---

## Audience | 适用受众

**Every Agent user, from beginner to professional.**
**所有 Agent 用户，从新手到专业用户。**

- **Beginner**: works with a single prompt file. Audit → see L0 → follow four steps → copy the fixtures.
  **新手**：只有一个提示词文件也能用。先跑审计看自己在 L0，再按四步补，示例目录可直接抄。
- **Intermediate**: already layered? Use the audit to avoid the L2 danger zone.
  **进阶**：已有分层，正打算加自改进循环——用审计确认别掉进 L2 危险区。
- **Professional**: wire `--strict` / `--assert-level` into CI as a structural gate.
  **专业**：把 `--strict` / `--assert-level` 接进 CI 当结构门禁。

---

## Resources | 资源

| File | Purpose | 用途 |
|---|---|---|
| `SKILL.md` | Full instructions | 完整使用说明 |
| `scripts/selfref_audit.py` | The auditor (hard code) | 审计器（硬代码） |
| `example/README.md` | **Minimal runnable example** | **最小运行示例** |
| `example/run_demo.py` | Three-level comparison in one command | 一条命令跑三级对照 |
| `example/l0-demo/` `example/l2-demo/` `example/l3-demo/` | Copy-ready skeletons | 可直接抄的骨架 |
| `references/audit-report-sample.md` | **Real audit report samples** | **真实审计报告样例** |
| `references/faq.md` | FAQ, pitfalls, before/after | FAQ · 坑点 · 对照效果 |
| `references/paper-notes.md` | Paper mapping | 论文映射 |

---

## Paper basis | 论文依据

| Paper mechanism | How it lands here |
|---|---|
| HyperAgents（arXiv:2603.19461）: editable meta-layer = metacognitive self-modification | The L2 / L3 criteria |
| HyperAgents: archive + soft reward + git-diff rollback | Step 4's three components |
| Practice Makes Unsafe（arXiv:2608.12851）: 21/21 all compromised | Why fixed points and the human gate come first |
| Self-Evolving Survey: four-component loop | Separating the task layer (system) from the meta layer (optimiser) |

| 论文机制 | 本 skill 落地 |
|---|---|
| HyperAgents：元层可编辑 = 元认知自修改 | L2 / L3 判据 |
| HyperAgents：archive + 软奖励 + git diff 回滚 | 第 4 步的三件套 |
| Practice Makes Unsafe：21/21 全军覆没 | 不动点与人类闸强制前置 |
| Self-Evolving Survey：四组件闭环 | 任务层（系统）→ 元层（优化器）分离审计 |

**License | 许可证**: design ideas reference HyperAgents (CC BY-NC-SA 4.0, non-commercial); the auditor is an independent original implementation, personal non-commercial use only.
设计思路参考 HyperAgents（CC BY-NC-SA 4.0 非商用）；审计脚本为独立原创实现，仅限个人非商用。
