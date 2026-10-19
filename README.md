# UncleKK 自指自改进设计器 | UncleKK Self-Referential Design

> 中文在前，英文在后（SkillHub 规范）。| Chinese first, English after.
> 版本 Version: **1.1.1**

诊断你的 Agent 处在**自指自改进**的哪一级，并给出把它改造成「能改进自己改法」的闭环方案。
Diagnose which **self-referential maturity** level your Agent sits at, and turn it into a system that can improve *how it improves itself*.

---

## 一句话 | One-liner

你的 Agent 迭代慢，**根因通常不是模型笨，而是"怎么改进它"这件事被写死了**。
Your Agent iterates slowly not because the model is dumb, but because **how to improve it is hard-coded**.

**自指的充分条件不是"能改自己"，而是"改错了能被拦住并回滚"。**
The sufficient condition for self-reference is not "can edit itself" but "**mistakes get caught and rolled back**".

---

## 四级成熟度 | Four maturity levels

| 级别 | 特征 | 症状 |
|---|---|---|
| **L0** 人肉迭代 Manual | 没有元层文件 | 换个任务就拉胯，经验留不下来 |
| **L1** 固定元层 Fixed | 有"怎么改"的规则，但写死在代码里 | 只能在固定框架内打转 |
| **L2** 半开自指 Half-open ⚠️ | 元层可编辑，但缺不动点或人类确认闸 | **短期变强，长期把安全约束自己演化掉** |
| **L3** 可控自指 Controlled | 元层可编辑 + 不动点 + 人类确认闸 + 可回滚 | 改进机制本身能跨任务累积 |

**L2 比 L0 更危险。** L0 只是慢；L2 会伪装成"变强了"直到出事。
**L2 is more dangerous than L0.** L0 is merely slow; L2 masquerades as progress.

---

## 快速开始 | Quick start

```bash
# 1) 审计：看自己在哪一级 | See your level
python scripts/selfref_audit.py 你的Agent目录

# 2) 跑最小示例：一条命令看三级对照 | One command, three levels
python example/run_demo.py

# 3) 当 CI 硬闸用 | Use as a CI hard gate
python scripts/selfref_audit.py 你的Agent目录 --strict
```

零第三方依赖，Python 3.8+，**只读不写**。
Zero dependencies, Python 3.8+, **read-only**.

---

## 改造流程 | Remediation（硬上限 4 步，顺序不可颠倒）

> **最多 4 步，没有第 5 步。** 超过说明归因错了，回到第 2 步重判。
> **Four steps, no fifth.** Need more? The attribution is wrong — go back to step 2.

1. **抽出元层**：把硬编码在 `.py` 里的改进逻辑写成 `meta/evolve-policy.md` 这类文本文件。
   Extract hard-coded improvement logic into an editable text file.
2. **声明不动点**（**必须在放开元层之前**）：锁 3 个文件——契约、引擎本体、红线清单。
   Declare 3 fixed points BEFORE opening the meta-layer: contract, engine, red-line list.
3. **加人类确认闸**：元层改动缺确认即**拒绝**应用。**不要用"提醒"代替"拦截"。**
   Add a human-approval gate. **Warn ≠ block.**
4. **接评分与回滚**：0~1 效用分 + 违规计数；git 提交点或 `trial→verdict→revert`；变体库存负样本。
   Wire scoring, rollback, and a negative-sample archive.

---

## 硬代码保障 | Hard enforcement

不是纯声明式——`scripts/selfref_audit.py` 是真实可执行代码，能给 CI 当闸门。
Not declarative-only: the auditor is real executable code and works as a CI gate.

| 退出码 | 含义 | Meaning |
|---|---|---|
| 0 | 审计完成 / 通过 | passed |
| 1 | 目录不存在 | directory missing |
| 2 | 无可读文本文件 | no readable text files |
| 3 | `--strict`：存在致命/高缺口 | critical/high gaps |
| 4 | `--assert-level N`：未达指定级别 | below required level |
| 5 | 内部异常（**明确报"结果不可信"**） | internal error (reported loudly) |

扫描上限（不会无限跑）：文件数 500、深度 5、单文件 400 KB，超限即截断并**显式标注**。
Bounded scan: 500 files, depth 5, 400 KB per file — truncation is always labeled.

---

## 适用受众 | Audience

**所有 Agent 用户，从新手到专业用户。**
For every Agent user, from beginner to professional.

- **新手**：只有一个提示词文件也能用。先跑审计看自己在 L0，再按四步补，示例目录可直接抄。
  **Beginner**: works with a single prompt file. Audit → see L0 → follow four steps → copy the fixtures.
- **进阶**：已有分层，正打算加自改进循环——用审计确认别掉进 L2 危险区。
  **Intermediate**: already layered? Use the audit to avoid the L2 danger zone.
- **专业**：把 `--strict` / `--assert-level` 接进 CI 当结构门禁。
  **Professional**: wire the hard gates into CI as a structural check.

---

## 资源 | Resources

| 文件 | 用途 | Purpose |
|---|---|---|
| `SKILL.md` | 完整使用说明 | full instructions |
| `scripts/selfref_audit.py` | 审计器（硬代码） | the auditor |
| `example/README.md` | **最小运行示例** | minimal runnable example |
| `example/run_demo.py` | 一条命令跑三级对照 | three-level comparison |
| `references/audit-report-sample.md` | **真实审计报告样例** | real report samples |
| `references/faq.md` | FAQ · 坑点 · 对照效果 | FAQ, pitfalls, before/after |
| `references/paper-notes.md` | 论文映射 | paper mapping |

---

## 论文依据 | Paper basis

| 论文机制 | 本 skill 落地 |
|---|---|
| HyperAgents（arXiv:2603.19461）：元层可编辑 = 元认知自修改 | L2 / L3 判据 |
| HyperAgents：archive + 软奖励 + git diff 回滚 | 第 4 步的三件套 |
| Practice Makes Unsafe（arXiv:2608.12851）：21/21 全军覆没 | 不动点与人类闸强制前置 |
| Self-Evolving Survey：四组件闭环 | 任务层（系统）→ 元层（优化器）分离审计 |

设计思路参考上述论文；审计脚本为独立原创实现。
Design ideas reference the papers above; the auditor is an independent original implementation.

**许可证 License**：设计思路参考 HyperAgents（CC BY-NC-SA 4.0 非商用）；实现仅限个人非商用。
