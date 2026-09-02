<div align="center">

# Development Planning

**Persistent planning and development state for Coding Agents.**

轻量、可恢复、可验证的软件开发规划 Skill。  
面向 Codex、Claude Code、Cursor 等 Coding Agent，以 Markdown 持久化开发上下文，并使用少量 Python 提供确定性校验。

![Markdown First](https://img.shields.io/badge/Markdown-First-111111?style=flat-square)
![Local First](https://img.shields.io/badge/Local-First-111111?style=flat-square)
![Agent Friendly](https://img.shields.io/badge/Coding_Agent-Friendly-111111?style=flat-square)

</div>

---

## Why Development Planning

Coding Agent 很擅长完成当前任务，但长周期开发还需要解决另一类问题：**如何让正确的项目状态跨会话持续存在。**

`development-planning` 将项目选择、当前开发位置、全局规划、模块实现方案、完成状态和关键计划变化保存为本地 Markdown 文件，使新的会话不必依赖聊天记忆重新猜测上下文。

它重点解决：

| 场景 | 能力 |
| --- | --- |
| 多项目并行 | 使用唯一 `[✅]` 明确当前项目 |
| 新会话恢复 | 通过 `current.md` 找回真实开发位置 |
| 长周期规划 | 全局计划 + 模块级实现计划 |
| 中途需求变化 | 允许调整当前有效计划并维护版本 |
| 文件意外丢失 | `manifest.md` 区分未创建与创建后缺失 |
| Agent 越界风险 | 校验项目根目录，防止跨项目操作 |
| 时间一致性 | 统一通过 Python 获取北京时间 |

核心工作流：

```text
选择项目
→ 校验边界
→ 检查开发资料完整性
→ 恢复当前开发位置
→ 读取当前有效计划
→ 实现与验证
→ 必要时调整计划
→ 更新状态
```

完整、纯净的 Skill 功能说明见 **[SKILL-INTRODUCTION.md](./SKILL-INTRODUCTION.md)**。

## Repository Layout

```text
.
├── README.md
├── SKILL-INTRODUCTION.md
└── skills/
    └── development-planning/
        ├── SKILL.md
        └── references/
            ├── projects-template.md
            ├── manifest-template.md
            ├── current-template.md
            ├── global-plan-template.md
            ├── module-plan-template.md
            ├── module-development-log-template.md
            ├── agent-instruction-block.md
            ├── get_beijing_time.py
            ├── validate_project_scope.py
            └── validate_project_manifest.py
```

- `README.md`：仓库入口、Skill 概览和仓库迭代规则。
- `SKILL-INTRODUCTION.md`：纯净的 Skill 介绍，不包含仓库维护或发布规则。
- `skills/development-planning/`：真正的 Skill 本体。

仓库说明文档与 Skill 本体保持目录隔离。

## Skill Location

真正需要安装、加载或交给 Coding Agent 使用的内容位于：

```text
skills/development-planning/
```

不同 Coding Agent 的 Skill 安装方式和项目级指令机制不同，应以对应宿主的正式支持方式为准。

---

# Agent / Codex 仓库迭代规则

以下规则适用于任何维护本仓库的 Coding Agent，包括 Codex、Claude Code、Cursor Agent 等。

## 1. `main` 只保存稳定版本

`main` 是稳定分支。

Agent **不得直接在 `main` 分支进行开发、试验、测试或临时修改**。

包括但不限于：

- 不得直接修改 `skills/development-planning/SKILL.md`；
- 不得直接修改 `skills/development-planning/references/`；
- 不得直接修改公开说明文档后立即发布；
- 不得为了试验而向 `main` 提交临时内容；
- 不得未经用户同意把其他分支内容提升到 `main`。

## 2. 所有修改必须先在 `test` 分支完成

开始维护前，Agent 必须确认当前分支。

如果当前在 `main`：

1. 不得直接修改；
2. 切换到 `test` 分支；
3. 如果 `test` 不存在，应基于最新 `main` 创建 `test`；
4. 后续修改、试验、文档同步和验证全部在 `test` 完成。

如果无法确认或安全切换分支，应停止修改并告知用户。

## 3. `test` 通过后也不能自行提升到 `main`

完成修改后，Agent 必须先在 `test`：

1. 检查所有变更；
2. 执行与本次修改相关的测试或验证；
3. 检查是否产生缓存、临时文件或非预期产物；
4. 向用户汇报：
   - 修改了什么；
   - 测试/验证结果；
   - 是否存在已知风险或未验证内容；
5. 明确询问用户是否同意将**本次 `test` 版本**提升到 `main`。

只有用户针对当前这一次修改明确同意后，Agent 才可以执行 `test → main`。

不得把以下情况当作本次授权：

- 用户过去允许过发布；
- 用户说过以后可以代为维护；
- 用户只同意修改方案，但没有同意提升到 `main`；
- Agent 自己判断修改很安全。

## 4. 不得破坏 `main` 历史

除非用户对具体操作明确授权，否则 Agent 不得：

- force push `main`；
- 重写 `main` 历史；
- 删除 `main`；
- 绕过 `test → 验证 → 用户确认 → main` 流程。

## 5. Skill 修改必须同步维护说明

如果修改 `skills/development-planning/SKILL.md` 或其 `references/`，并且影响以下任一内容：

- Skill 功能或行为；
- 项目、模块、功能工作流；
- 文件结构或文件职责；
- 状态、版本、时间或校验规则；
- Agent 安全约束；
- 用户操作方式；
- 模板或脚本的新增、删除、重命名；

则必须在同一个 `test` 分支中同步检查：

- `README.md`：Skill 简介、仓库结构、使用方式、维护规则是否仍准确；
- `SKILL-INTRODUCTION.md`：纯净 Skill 介绍是否与实际行为一致。

如果实际 Skill 已改变而文档仍描述旧行为，视为维护未完成。

反过来，修改介绍文档时，也必须检查是否与当前 Skill 本体一致。

## 6. 目录隔离规则

仓库文档与 Skill 本体必须保持分离：

```text
README.md
SKILL-INTRODUCTION.md
```

保留在仓库根目录；真正的 Skill 本体只放在：

```text
skills/development-planning/
```

维护时不得把仓库级 README、发布规则或纯介绍文档混入 Skill 本体目录。

## 7. 请求发布到 `main` 前的最低检查

- [ ] 当前修改发生在 `test`，不是 `main`。
- [ ] `SKILL.md` 与相关 `references/` 一致。
- [ ] Python 脚本语法检查通过（如本次涉及 Python 或进行整体发布验证）。
- [ ] 没有 `__pycache__`、`*.pyc` 或临时测试文件。
- [ ] `SKILL-INTRODUCTION.md` 已与当前 Skill 行为同步。
- [ ] `README.md` 已检查并按需同步。
- [ ] 仓库根文档没有被混入 `skills/development-planning/`。
- [ ] 已向用户汇报本次变更和验证结果。
- [ ] 已取得用户针对本次 `test → main` 的明确同意。

## 迭代流程

```text
main（稳定）
  ↓
基于 main 创建 / 更新 test
  ↓
test 中修改 Skill / 文档
  ↓
测试与一致性检查
  ↓
向用户汇报
  ↓
用户明确同意
  ↓
test → main
```

核心原则：**Agent 可以协助修改和验证，但稳定版本是否进入 `main` 始终由用户决定。**
