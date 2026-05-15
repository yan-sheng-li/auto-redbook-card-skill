---
name: xhs-note-creator
description: 小红书笔记素材创作技能。当用户需要创建小红书笔记素材时使用这个技能。技能包含：根据用户的需求和提供的资料，撰写小红书笔记内容（标题+正文），生成图片卡片（封面+正文卡片），以及发布小红书笔记。支持 9 种精美排版主题和 4 种智能分页模式。
---

# 小红书笔记创作技能

根据用户提供的资料或需求，创作小红书笔记内容、生成精美图片卡片，并可选择发布到小红书。

> 详细参数文档见 `references/params.md`

---

## 工作流程

### 第一步：创建主题目录

**根据主题名称创建独立目录**，所有相关文件统一存放：

```bash
# 主题名称建议：小写、无空格、用连字符分隔
mkdir -p mycli
# 或
mkdir -p lazygit-guide
```

**目录结构示例**：
```
mycli/                    # 主题目录
├── mycli_content.md      # 渲染用 Markdown
├── mycli_posting.txt     # 发布文案（自动生成）
├── cover.png             # 封面图片（自动生成）
├── card_1.png            # 正文卡片（自动生成）
├── card_2.png
└── ...
```

---

### 第二步：撰写小红书笔记内容

根据用户需求和资料，创作符合小红书风格的内容：

**标题**：不超过 20 字，吸引眼球，可用数字/疑问句/感叹号增强吸引力。

**正文**：段落清晰，点缀少量 Emoji（每段 1-2 个），短句短段，结尾附 5-10 个 SEO 标签。

---

### 第三步：生成渲染用 Markdown 文档

**在主题目录内创建**，此 Markdown 专为图片渲染设计：

```markdown
---
emoji: "🚀"
title: "封面大标题（≤15字）"
subtitle: "封面副标题（≤15字）"
---

# 正文内容...

---

# 第二张卡片内容...（使用 --- 手动分隔时）
```

分页策略选择：
- 内容需精确切分 → 用 `---` 手动分隔，配合 `-m separator`
- 内容长短不稳定 → 生成普通 Markdown，使用 `-m auto-split`

---

### 第四步：渲染图片卡片

**在主题目录内执行**，输出到当前目录：

```bash
# 进入主题目录
cd mycli

# 渲染（输出到当前目录）
python /path/to/scripts/render_xhs.py mycli_content.md -o . -t cyberpunk -m auto-fit
```

**推荐命令**（一键完成）：

```bash
# 创建目录 + 渲染 + 生成文案
mkdir -p mycli && cd mycli

# 渲染图片（指定输出到当前目录）
python /path/to/scripts/render_xhs.py mycli_content.md -o . -t cyberpunk -m auto-fit --cover-image "URL"

# 生成发布文案
python /path/to/scripts/generate_posting.py mycli_content.md
```

**封面显示逻辑**：优先使用 `--cover-image` 参数或 YAML 中的 `cover_image`/`image` 字段；若无图片则显示 emoji 作为备选方案。

**可用主题**（`-t`）：`sketch`、`default`、`playful-geometric`、`neo-brutalism`、`botanical`、`professional`、`retro`、`terminal`、`cyberpunk`

**分页模式**（`-m`）：`separator`、`auto-fit`、`auto-split`、`dynamic`

> 完整参数说明见 `references/params.md`

---

### 第五步：生成小红书笔记文案（自动生成）

**在主题目录内执行**，自动创建 `<主题名>_posting.txt`：

```bash
python /path/to/scripts/generate_posting.py mycli_content.md
```

生成文件包含：
1. **3-5 个标题建议**（选一，不超过 20 字）
2. **描述文案**（正文开头部分）
3. **话题标签**（核心 + 扩展 + 风格标签）

**示例** (`mycli_posting.txt`)：
```
标题建议（选一）：
1. MySQL 终端神器 MyCLI！🐬
2. 告别枯燥 SQL，MyCLI 来救你！
3. 程序员必备：MyCLI 智能客户端

描述文案：
MySQL 终端智能客户端，告别枯燥 SQL 操作...

#MyCLI #MySQL #终端工具 #程序员必备 #开发效率
```

---

### 第六步：发布小红书笔记（可选）

**在主题目录内执行**，直接使用当前目录的图片：

```bash
# 进入主题目录
cd mycli

# 默认仅自己可见（推荐先预览确认）
python /path/to/scripts/publish_xhs.py \
  --title "MyCLI 高效指南" \
  --desc "MySQL 终端智能客户端..." \
  --images cover.png card_*.png

# 确认无误后公开发布
python /path/to/scripts/publish_xhs.py \
  --title "MyCLI 高效指南" \
  --desc "MySQL 终端智能客户端..." \
  --images cover.png card_*.png --public
```

**前置条件**：配置好 `.env` 文件中的 `XHS_COOKIE`（详见 `references/params.md`）

> **默认以「仅自己可见」发布**，加 `--public` 参数才会公开。

---

## 完整示例流程

以 **MyCLI** 主题为例：

```bash
# 1. 创建主题目录
mkdir -p mycli && cd mycli

# 2. 创建内容文件（手动或使用技能生成）
# mycli_content.md

# 3. 渲染图片
python /root/.claude/skills/auto-redbook-card-skill/scripts/render_xhs.py \
  mycli_content.md -o . -t cyberpunk -m auto-fit \
  --cover-image "http://cdn.qiniu.liyansheng.top/img/20260514171844.png"

# 4. 生成发布文案
python /root/.claude/skills/auto-redbook-card-skill/scripts/generate_posting.py \
  mycli_content.md

# 5. 查看结果
ls -la
# mycli_content.md  mycli_posting.txt  cover.png  card_1.png ...

# 6. 发布（可选）
python /root/.claude/skills/auto-redbook-card-skill/scripts/publish_xhs.py \
  --title "MyCLI 高效指南" --desc "..." --images cover.png card_*.png
```

---

## 技能资源

### 脚本
- `scripts/render_xhs.py` — 渲染脚本（主推，9 主题 + 4 分页模式）
- `scripts/render_xhs_v2.py` — 渲染脚本 V2（备用，7 种渐变色彩风格）
- `scripts/publish_xhs.py` — 发布脚本
- `scripts/generate_posting.py` — 笔记文案生成脚本（自动创建标题、描述、标签）

### 模板与样式
- `assets/cover.html` — 封面 HTML 模板
- `assets/card.html` — 正文卡片 HTML 模板
- `assets/styles.css` — 公共容器样式
- `assets/themes/` — 各主题 CSS 文件

### 参考文档
- `references/params.md` — 完整参数参考（主题/模式/发布参数）
