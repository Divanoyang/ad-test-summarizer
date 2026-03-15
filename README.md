# Cursor Skills Collection

一组为 [Cursor IDE](https://cursor.sh) 打造的内置 Agent Skills，帮助 AI 代理更高效地完成编辑器相关任务。

## Skills 列表

| Skill | 说明 |
|-------|------|
| [create-rule](create-rule/SKILL.md) | 创建 `.cursor/rules/` 下的持久化 AI 规则（`.mdc` 文件），用于设定编码标准和项目约定 |
| [create-skill](create-skill/SKILL.md) | 引导创建新的 Agent Skill，包含目录结构、SKILL.md 编写规范和最佳实践 |
| [create-subagent](create-subagent/SKILL.md) | 创建自定义子代理（Subagent），如代码审查员、调试器、数据分析师等专用 AI 助手 |
| [migrate-to-skills](migrate-to-skills/SKILL.md) | 将旧版 Cursor Rules 和 Slash Commands 迁移为 Agent Skills 格式 |
| [shell](shell/SKILL.md) | 通过 `/shell` 命令直接在终端中执行 shell 命令 |
| [update-cursor-settings](update-cursor-settings/SKILL.md) | 修改 Cursor/VSCode 的 `settings.json` 配置，如主题、字号、自动保存等 |

## 安装使用

将本仓库克隆到 Cursor 的 skills 目录：

```bash
# 个人级别（所有项目可用）
git clone https://github.com/Divanoyang/cursor-skills.git ~/.cursor/skills-cursor

# 项目级别（仅当前项目可用）
git clone https://github.com/Divanoyang/cursor-skills.git .cursor/skills
```

## 目录结构

```
cursor-skills/
├── create-rule/          # 创建 Cursor 规则
│   └── SKILL.md
├── create-skill/         # 创建 Agent Skill
│   └── SKILL.md
├── create-subagent/      # 创建自定义子代理
│   └── SKILL.md
├── migrate-to-skills/    # 迁移规则和命令到 Skills
│   └── SKILL.md
├── shell/                # Shell 命令执行
│   └── SKILL.md
├── update-cursor-settings/  # 修改编辑器设置
│   └── SKILL.md
└── README.md
```

## Skill 编写规范

每个 Skill 是一个目录，包含一个 `SKILL.md` 文件，格式如下：

```markdown
---
name: skill-name
description: 简要描述 Skill 的功能和触发场景
---

# Skill 标题

具体指令内容...
```

关键要点：

- **name**：小写字母 + 连字符，最长 64 字符
- **description**：用第三人称描述功能和使用场景，最长 1024 字符
- **正文**：建议不超过 500 行，保持简洁
- 详细参考资料放在独立文件中，由 SKILL.md 引用

## License

MIT
