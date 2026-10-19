# 最小运行示例 | Minimal Runnable Example

三个极简目录，覆盖 L0 / L2 / L3 三个级别。每个目录只有 1-4 个文件，能看懂也能改。
Three tiny directories covering L0 / L2 / L3. Each has 1-4 files — readable and editable.

> 中文在前，英文在后（SkillHub 规范）。| Chinese first, English after.

---

## 一条命令跑完 | One command

```bash
python example/run_demo.py
```

零第三方依赖，Python 3.8+ 即可。输出三级的判定对照。
No third-party dependencies; Python 3.8+. Prints the three-level comparison.

---

## 单跑某一个 | Run a single fixture

```bash
python scripts/selfref_audit.py example/l0-demo          # 人读报告
python scripts/selfref_audit.py example/l2-demo --json   # 机器读
python scripts/selfref_audit.py example/l3-demo --strict # 硬闸（退出码 3 = 有致命缺口）
```

---

## 三个目录分别是什么 | What the three fixtures are

### `l0-demo` —— L0 人肉迭代

```
l0-demo/
└── prompt.md        # 只有系统提示与工具清单
```

**没有任何元层文件**。改什么、怎么改，全靠人当场判断。审计报缺口 `G1`。
No meta-layer at all. Reported gap: `G1`.

---

### `l2-demo` —— L2 半开自指（危险区）

```
l2-demo/
├── prompt.md
└── meta/
    └── evolve-policy.md     # 可编辑元层，但没有不动点、没有人类确认闸
```

**元层是可编辑的 Markdown，但整套结构里没有任何"Agent 改不了"的落脚点，也没有需要人点头的环节。**
审计报 **两条致命缺口 `R1` + `R2`**，外加 `G3`、`G4`。

> ⚠️ **为什么说明文字写在 README 里、不写在示例文件里？**
> 因为审计器靠关键词识别"不动点""人类确认"等信号——
> 如果在示例文件里写"本系统**没有**不动点"，这句**否定句反而会被当成命中信号**，
> 把一个危险的 L2 结构误判成 L3。这是开发过程中真实踩到的坑。
> **结论：说明性文字要放在被审计目录之外。**
>
> Why is the explanation here and not in the fixture? Because the auditor matches keywords
> like "fixed point" / "human approval" — writing "this system has **no** fixed point" inside
> an audited file would **trigger the very signal it denies**, misgrading a dangerous L2 as L3.
> Keep explanatory prose outside the audited directory.

---

### `l3-demo` —— L3 可控自指（目标状态）

```
l3-demo/
├── CONTRACT.md              # 不动点契约 + 人类确认闸（Agent 禁止修改）
├── prompt.md                # 任务层：被改的对象
├── eval.json                # 评分信号：utility + violations
├── ledger/
│   └── archive.json         # 变体库：被拒/回滚的改动作负样本
└── meta/
    └── evolve-policy.md     # 元层：规定"如何改进"，本身也在可演化清单内
```

七项结构组件**全部命中，零缺口**。这就是可以直接抄的骨架。
All seven components present, **zero gaps**. This is the skeleton worth copying.

---

## 动手实验 | Try it yourself

```bash
# 删掉不动点契约，看 L3 怎么掉回 L2
# Remove the fixed-point contract and watch L3 fall back to L2
mv example/l3-demo/CONTRACT.md /tmp/
python scripts/selfref_audit.py example/l3-demo --strict
echo "exit=$?"     # 3 —— 出现致命缺口 R1
```

**这一删一跑，比读十页文档都直观。**
Nothing makes the point faster than deleting that one file and re-running.

更多样例输出见 `references/audit-report-sample.md`。
More sample output: `references/audit-report-sample.md`.
