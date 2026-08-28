# LLM Context

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/llm-context.svg)](https://pypi.org/project/llm-context/)
[![Downloads](https://static.pepy.tech/badge/llm-context/week)](https://pepy.tech/project/llm-context)

**LLM 开发工作流的智能上下文管理工具。** 通过智能选择和基于规则的过滤，即时共享相关项目文件。

## 问题所在

将正确的上下文传递到 LLM 对话中存在诸多摩擦：

- 手动查找和复制相关文件浪费时间
- 上下文过多会触及 token 限制，过少则遗漏重要细节
- AI 请求额外文件时需要手动获取
- 难以跟踪开发会话中的变更

## 解决方案

llm-context 通过可组合的规则，提供聚焦的、任务特定的项目上下文。

**适用于使用聊天界面的人类用户：**
```bash
lc-select   # 智能文件选择
lc-context  # 将格式化的上下文复制到剪贴板
# 粘贴并使用 - AI 可通过 MCP 访问额外文件
```

**适用于拥有 CLI 访问权限的 AI 代理：**
```bash
lc-preview tmp-prm-auth    # 验证规则是否选择了正确的文件
lc-context tmp-prm-auth    # 获取子代理的聚焦上下文
```

**适用于聊天环境中的 AI 代理（MCP 工具）：**
- `lc_outlines` - 从当前规则生成摘录上下文
- `lc_preview` - 使用前验证规则有效性
- `lc_missing` - 按需获取特定文件/实现

> **注意**：本项目是与多个 Claude Sonnet（3.5、3.6、3.7、4.0）和 Grok（3、4）协作开发的，开发过程中使用了 LLM Context 本身来共享代码。所有代码均由 @restlessronin 进行了大量人工审核。

## 安装

```bash
uv tool install "llm-context>=0.6.0"
```

### 代理配置（Claude Code 技能）

如果你是代理，需要设置 llm-context 来帮助管理任务上下文，请每个项目运行一次：

```bash
uv tool install "llm-context>=0.6.0"   # 全局安装 lc-* 命令
cd <project-root>
lc-init                                # 创建 .llm-context/，将 lc-curate-context 技能复制到 .claude/skills/
```

运行 `lc-init` 后，`lc-curate-context` 技能将加载到该项目的 Claude Code 会话中。它会教你如何编写最小化的任务规则，并在生成上下文之前使用 `lc-preview` 进行验证。

要获取更新版本的技能，运行 `uv tool upgrade llm-context` 并重新执行 `lc-init` — 它会原地刷新技能文件。

## 快速开始

### 人类工作流（剪贴板）

```bash
# 一次性设置
cd your-project
lc-init

# 日常使用
lc-select
lc-context
# 粘贴到你的 LLM 聊天中
```

### MCP 集成（推荐）

添加到 Claude Desktop 配置文件（`~/Library/Application Support/Claude/claude_desktop_config.json`）：

```jsonc
{
  "mcpServers": {
    "llm-context": {
      "command": "uvx",
      "args": ["--from", "llm-context", "lc-mcp"]
    }
  }
}
```

重启 Claude Desktop。现在 AI 可以在对话中访问额外文件，无需手动复制。

### 代理工作流（CLI）

拥有 shell 访问权限的 AI 代理使用 llm-context 创建聚焦的上下文：

```bash
# 代理探索代码库
lc-outlines

# 代理为特定任务创建聚焦规则
#（通过技能或 lc-rule-instructions）

# 代理验证规则
lc-preview tmp-prm-oauth-task

# 代理为子任务使用上下文
lc-context tmp-prm-oauth-task
```

### 代理工作流（MCP）

聊天环境中的 AI 代理使用 MCP 工具：

```bash
# 探索代码库结构
lc_outlines(root_path, rule_name)

# 验证规则有效性
lc_preview(root_path, rule_name)

# 获取特定文件/实现
lc_missing(root_path, param_type, data, timestamp)
```

## 核心概念

### 规则：任务特定的上下文描述符

规则是 YAML+Markdown 文件，描述为任务提供哪些上下文：

```yaml
---
description: "调试 API 认证"
compose:
  filters: [lc/flt-no-files]
  excerpters: [lc/exc-base]
also-include:
  full-files: ["/src/auth/**", "/tests/auth/**"]
---
聚焦于认证系统及相关测试。
```

### 五种规则类别

- **提示规则（`prm-`）**：生成项目上下文（如 `lc/prm-developer`）
- **过滤规则（`flt-`）**：控制文件包含（如 `lc/flt-base`、`lc/flt-no-files`）
- **指令规则（`ins-`）**：提供指导方针（如 `lc/ins-developer`）
- **风格规则（`sty-`）**：强制编码规范（如 `lc/sty-python`）
- **摘录规则（`exc-`）**：配置内容提取（如 `lc/exc-base`）

### 规则组合

从简单规则构建复杂规则：

```yaml
---
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [lc/flt-base, project-filters]
  excerpters: [lc/exc-base]
---
```

## 常用命令

| 命令                  | 用途                                     |
| -------------------- | ---------------------------------------- |
| `lc-init`            | 初始化项目配置                             |
| `lc-select`          | 根据当前规则选择文件                        |
| `lc-context`         | 生成并复制上下文                           |
| `lc-context -p`      | 包含提示指令                               |
| `lc-context -m`      | 格式化为独立消息                           |
| `lc-context -nt`     | 无工具（手动工作流）                        |
| `lc-set-rule <name>` | 切换活动规则                               |
| `lc-preview <rule>`  | 验证规则选择和大小                          |
| `lc-outlines`        | 获取代码结构摘录                           |
| `lc-missing`         | 获取文件/实现（手动 MCP）                   |

## AI 辅助规则创建

让 AI 帮助创建聚焦的、任务特定的规则。根据你的环境有两种方式：

### Claude 技能（交互式，Claude Desktop/Code）

**工作原理**：全局技能交互式地引导你创建规则，使用 MCP 工具按需检查你的代码库。

**设置**：
```bash
lc-init  # 安装技能到 ~/.claude/skills/
# 重启 Claude Desktop 或 Claude Code
```

**使用**：
```bash
# 1. 共享项目上下文
lc-context  # 任意规则 - 包含概览

# 2. 粘贴到 Claude，然后请求：
# "创建一个将认证重构为 JWT 的规则"
# "我需要一个调试支付处理的规则"
```

Claude 将会：
1. 使用已在上下文中的项目概览
2. 按需通过 `lc-missing` 检查特定文件
3. 询问关于范围的澄清问题
4. 生成优化的规则（`tmp-prm-<task>.md`）
5. 提供验证说明

**技能文档**（渐进式展示）：
- `Skill.md` - 快速工作流、决策模式
- `PATTERNS.md` - 常见规则模式
- `SYNTAX.md` - 详细参考
- `EXAMPLES.md` - 完整演练
- `TROUBLESHOOTING.md` - 问题排查

### 指令规则（适用于任何环境）

**工作原理**：将全面的规则创建文档加载到上下文中，与任何 LLM 协作。

**使用**：
```bash
# 1. 加载框架
lc-set-rule lc/prm-rule-create
lc-select
lc-context -nt

# 2. 粘贴到任何 LLM
# "我需要一个添加 OAuth 集成的规则"

# 3. LLM 使用框架生成聚焦规则

# 4. 使用新规则
lc-set-rule tmp-prm-oauth
lc-select
lc-context
```

**包含的文档**：
- `lc/ins-rule-intro` - 介绍和概览
- `lc/ins-rule-framework` - 完整的决策框架

### 对比

| 方面                     | 技能                             | 指令规则                  |
| ------------------------ | ------------------------------- | ------------------------ |
| **设置**                 | 通过 `lc-init` 自动完成          | 已内置可用               |
| **交互**                 | 交互式，使用 `lc-missing`       | 静态文档                 |
| **文件检查**             | 通过 MCP 自动完成                | 手动或通过 AI            |
| **最适合**               | Claude Desktop/Code             | 任何 LLM，任何环境       |
| **更新**                 | 版本升级时自动更新               | 内置于规则中             |

两者都需要先共享项目上下文，产生的结果相同。

## 项目自定义

### 创建基础过滤器

```bash
cat > .llm-context/rules/flt-repo-base.md << 'EOF'
---
description: "仓库特定的排除规则"
compose:
  filters: [lc/flt-base]
gitignores:
  full-files: ["*.md", "/tests", "/node_modules"]
  excerpted-files: ["*.md", "/tests"]
---
EOF
```

### 创建开发规则

```bash
cat > .llm-context/rules/prm-code.md << 'EOF'
---
description: "主开发规则"
instructions: [lc/ins-developer, lc/sty-python]
compose:
  filters: [flt-repo-base]
  excerpters: [lc/exc-base]
---
额外的项目特定指导和上下文。
EOF

lc-set-rule prm-code
```

## 部署模式

根据你的 LLM 环境选择格式：

| 模式                   | 命令               | 使用场景                  |
| --------------------- | ------------------ | ------------------------- |
| 系统消息               | `lc-context -p`    | AI Studio 等              |
| 单条用户消息            | `lc-context -p -m` | Grok 等                   |
| 分离消息               | `lc-prompt` + `lc-context -m` | 灵活放置     |
| 项目文件（包含）        | `lc-context`       | Claude Projects 等        |
| 项目文件（可搜索）      | `lc-context -m`    | 强制进入上下文             |

详见[部署模式](docs/user-guide.md#deployment-patterns)。

## 主要特性

- **智能选择**：规则自动包含/排除合适的文件
- **上下文验证**：在生成前预览大小和选择
- **代码摘录**：提取结构同时减少 token（支持 15+ 种语言）
- **MCP 集成**：AI 无需手动干预即可访问额外文件
- **可组合规则**：从可复用模式构建复杂上下文
- **AI 辅助创建**：交互式技能或基于文档的方式
- **代理友好**：CLI 和 MCP 接口支持自主操作

## 常见工作流

### 日常开发（人类）

```bash
lc-set-rule prm-code
lc-select
lc-context
# 粘贴到聊天 - AI 如有需要可通过 MCP 访问更多文件
```

### 聚焦任务（人类或代理）

```bash
# 先共享项目上下文
lc-context

# 然后创建聚焦规则：
# 通过技能："创建一个 [任务] 的规则"
# 通过指令：lc-set-rule lc/prm-rule-create && lc-context -nt

# 验证并使用
lc-preview tmp-prm-task
lc-context tmp-prm-task
```

### 代理上下文配置（CLI）

```bash
# 代理验证规则有效性
lc-preview tmp-prm-refactor-auth

# 代理为子代理生成上下文
lc-context tmp-prm-refactor-auth > /tmp/context.md
# 子代理读取上下文并执行任务
```

### 代理上下文配置（MCP）

```python
# 代理验证规则
preview = lc_preview(root_path="/path/to/project", rule_name="tmp-prm-task")

# 代理生成上下文
context = lc_outlines(root_path="/path/to/project")

# 代理按需获取额外文件
files = lc_missing(root_path, "f", "['/proj/src/auth.py']", timestamp)
```

## 路径格式

所有路径使用项目相对格式，带有项目名称前缀：

```
/{project-name}/src/module/file.py
/{project-name}/tests/test_module.py
```

这使得多项目上下文组合不会产生路径冲突。

**在规则中**，模式是项目相对路径，不包含前缀：
```yaml
also-include:
  full-files:
    - "/src/auth/**"      # ✓ 正确
    - "/myproject/src/**" # ✗ 错误 - 不要包含项目名称
```

## 了解更多

- **[用户指南](docs/user-guide.md)** - 包含示例的完整文档
- **[设计理念](https://www.cyberchitta.cc/articles/llm-ctx-why.html)** - llm-context 存在的原因
- **[实际案例](https://www.cyberchitta.cc/articles/full-context-magic.html)** - 有效使用完整上下文

## 许可证

Apache License, Version 2.0。详见 [LICENSE](LICENSE)。
