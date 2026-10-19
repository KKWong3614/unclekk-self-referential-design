# 论文依据与映射 | Paper Basis & Mapping

> **中文在前，英文在后（SkillHub 规范）。** | Chinese first, English after.
>
> **EN abstract**: This reference maps the skill's design back to three papers —
> HyperAgents (arXiv:2603.19461, editable meta-layer / metacognitive self-modification),
> Practice Makes Unsafe (arXiv:2608.12851, why fixed points and human gates are mandatory),
> and the Self-Evolving Agents Survey (four-component loop). It also records one
> **deliberate design divergence** from HyperAgents: we keep the meta-layer editable but
> bound it with fixed points and a human gate, trading self-acceleration speed for
> constraints that survive evolution. That trade-off is an engineering choice, not a
> paper conclusion.

所有依据取自本地知识库 `D:/图书馆/wiki/`，非凭印象。核验时间 2026-09-03。
All sources come from the local knowledge base `D:/图书馆/wiki/`, verified 2026-09-03.

## 1. HyperAgents —— 本 skill 的主干论文

- arXiv: 2603.19461 ｜ GitHub: facebookresearch/HyperAgents（2695⭐）｜ 协议 CC BY-NC-SA 4.0（非商用）
- 知识库页：`wiki/papers/paper-hyperagents.md`、`wiki/concepts/concept-self-referential-agent.md`

### 论文在解决什么问题

自改进 AI 想减少对人类工程的依赖，学会改进自身的"学习与解题流程"。但既有自改进方法依赖**固定、手工设计的元层机制**——这本身就构成了系统能变多快的上限。

Darwin Gödel Machine（DGM）在编程域展示了开放式自改进，但依赖一个隐含假设：**任务性能 ↔ 自修改能力同域对齐**。因为评估与自修改都是编程任务，编程能力提升能转化为自修改能力提升。该假设在编程之外一般不成立。

### 核心方法

- **双层同程序**：`task_agent.py`（解题）与 `meta_agent.py`（修改自己与 task agent）共处**同一个可编辑代码库**。meta agent 读自己与 task agent 的源码、生成修改、以 git diff 形式落地。
- **元认知自修改**：meta 的"如何修改"逻辑也是可编辑代码 → 系统能改进自己的改进方式。这是与一般自进化 agent 的分水岭。
- **达尔文进化循环**：archive（变体库）+ parent selection（选父代），以 eval 评分 + git diff 作软奖励驱动迭代。
- **DGM-H**：扩展 DGM，去掉同域对齐假设，支持**任意可计算任务**的自加速。

### 关键结果

- 多样域上性能随时间提升，优于无自改进 / 无开放式探索的基线，也优于既有自改进系统。
- **元层改进跨域迁移、跨运行累积**：如"持久记忆""性能追踪"这类改进机制本身被改进后，能在不同任务、不同运行间复用。
- 不只在搜更好解，更持续改进"如何改进"的搜索。

### 论文自身的安全警示

执行模型生成的不可信代码有破坏性风险；协议为 CC BY-NC-SA 4.0（非商用）。

### 映射到本 skill

| 论文概念 | 本 skill 落地 | 说明 |
|---|---|---|
| task + meta agent 同程序 | 元层与任务层文件共处同一可编辑目录 | 审计器负责把二者区分开 |
| 元层可编辑 = 元认知自修改 | L2 / L3 的判据 | 判据是"元层是否为可编辑文本文件" |
| archive + parent selection | 第 4 步的变体库 | 负样本留存 |
| eval 评分作软奖励 | 第 4 步的效用分 | |
| git diff 作回滚点 | 第 4 步的回滚机制 | |

## 2. Practice Makes Unsafe —— 本 skill 的约束来源

- arXiv: 2608.12851 ｜ 知识库页：`wiki/papers/paper-practice-makes-unsafe.md`

### 为什么它决定了本 skill 的"不动点"设计

- 实测 25 个 agent-method 配置（各 25 轮，共 525 任务）：**全部 21 个演化配置都写出了不安全产物**，其中 **15 个导致新会话伤害**；3 个恶意任务把遗留 ASR 从 16.0% 抬到 35.3%。
- 机理：演化优化的是任务结果**而非流程安全** → 受污染的经验导致**技能误演化**。一次不安全的成功，会变成可复用策略。
- 生命周期三段：**编写 → 检索 → 后续执行**。只测单点行为无法归因。
- SafeEvolve（写前修复 + 复用管控）：不安全检索 −26.7pp、新会话伤害 −17.3pp，良性效用仅变动 0.4 点。

### 映射

| 论文要素 | 本 skill 中的体现 |
|---|---|
| "一次不安全的成功会沉淀" | 不动点必须在放开元层**之前**声明（第 2 步先于第 1 步生效） |
| 编写段风险 | 不动点声明 + 引擎硬拦截 |
| 检索段风险 | 变体库存负样本，防止坏改动被重新捞回 |
| 后续执行段风险 | 人类确认闸 |
| "良性效用仅变动 0.4 点" | 评分注水风险提示：分数必须是客观、难刷的 |

## 3. Self-Evolving Agents Survey —— 结构骨架

- 知识库页：`wiki/papers/paper-self-evolving-survey.md`、`wiki/concepts/concept-self-evolving-agent.md`
- GitHub: EvoAgentX/Awesome-Self-Evolving-Agents（2343⭐）

多数 Agent 系统部署后**保持静态**。自进化的统一框架是四组件反馈闭环：**系统输入 → Agent 系统 → 环境 → 优化器**。

映射到本 skill 的审计视角：**任务层文件 = Agent 系统，元层文件 = 优化器**。审计器做的第一件事就是把这两层分开——分不开，就无法归因"到底是规则错了，还是找规则的方式错了"。

## 4. 一处主动的设计分歧（如实记录）

> HyperAgents 主张元层完全可编辑以获得开放式自加速；
> Practice Makes Unsafe 证明 21/21 的演化配置都会产出不安全产物。

**本 skill 的取舍**：承认元层可编辑是"自指"成立的必要条件（否则只是固定框架内的参数搜索），但强制要求**不动点 + 人类确认闸**两个前置。代价是牺牲一部分自加速速度，换取安全约束不会在若干代后被自己演化掉。

这属于工程取舍，**不是论文结论**。使用者若在隔离沙箱中追求最大自演化速度，可自行放宽——但请先读一遍 Practice Makes Unsafe 的 21/21。

## 5. 与 metacog-self-evolve 的关系

`metacog-self-evolve` 是运行时落地，本 skill 是设计期方法。分工：

| 阶段 | 谁负责 |
|---|---|
| 诊断现在在哪一级 | 本 skill（审计器） |
| 决定不动点、设计分层 | 本 skill（改造流程） |
| 记账、闸门、棘轮、回滚 | `metacog-self-evolve` |

本 skill 的 L3 判据（元层可编辑 + 不动点 + 人类闸 + 可回滚）正是从 metacog 的结构中归纳出来的——它是一个已被跑通的 L3 实例，可作为设计参照。
