# 简历样式重设计

> 日期：2026-06-26

## 目标

替换当前简陋的简历样式，采用木及简历极简风格：深色头部 + 蓝色点缀 + 清晰信息层级。利用现有的 `ResumeTemplate` 机制，通过数据迁移写入模板 CSS。

## 设计方向

- **深色（黑）头部**：姓名 + 职位 + 联系方式，黑底白字
- **分区标题**：蓝色竖线 + 文字，底部细线分割
- **技能标签**：浅灰底 + 细边框
- **排版**：system-ui 字体栈，宽松行距，左侧对齐

## 实现方案

利用现有的 `ResumeTemplate` 模板系统：
- `ResumeTemplate` 模型的 `content` 字段本就存储 CSS，通过 `<style>` 标签注入页面
- 在 Django admin 中手动添加一条 "现代简约" 模板记录，CSS 内容另存为参考文件
- `detail.html` 增加结构容器，为模板 CSS 提供样式锚点
- `detail.css` 提供打印等基础共享样式

### 改动范围

| 文件 | 改动 |
|------|------|
| `apps/resume/templates/resume/detail.html` | 添加 `.resume-wrapper` / `.resume-header` / `.resume-body` 结构容器 |
| `apps/resume/static/resume/css/detail.css` | 精简为打印样式 + 通用基础 |

**不涉及数据库变更**。模板 CSS 通过 Django admin 手动添加到 `ResumeTemplate` 表即可。

### 不改动

- `resume/utils.py`（Markdown 扩展）
- `resume/models.py`
- `resume/views.py`
- `resume/templates/resume/base.html`

## 数据流

```
ResumeTemplate.content (CSS)
    │
    ▼
detail.html:
    <link detail.css>           ← 基础/打印样式
    <style>{{ template.content }}</style>  ← 模板 CSS（覆盖/增强）
    <div class="resume-wrapper">
        <div class="resume-header">{{ resume.title }}</div>
        <div class="resume-body">{{ resume.body|safe }}</div>
    </div>
```

## CSS 架构

### 容器结构（detail.html 提供）

```
.resume-wrapper              ← 整体卡片容器
├── .resume-header           ← 深色背景，模板 CSS 负责
│   └── h1.resume-name       ← 简历标题，模板 CSS 负责
└── .resume-body             ← 白色背景，Markdown 渲染内容
    ├── h1/h2/h3             ← 模板 CSS 负责
    ├── p / ul > li          ← 模板 CSS 负责
    └── .flex-container      ← Markdown :::: 扩展生成
```

### 模板 CSS 要点（存在 ResumeTemplate.content 中）

1. **头部**：`background: #1a1a1a`，白色文字，姓名 28px/300 字重/4px 字间距
2. **分区标题 h2**：`::before` 伪元素 3px 蓝色竖线，`border-bottom: 1px solid #e8e8e8`
3. **列表项**：`·` 前缀，无标准圆点，13px 字号，1.7 行高
4. **技能标签**：`background: #f5f5f5`，`border: 1px solid #eee`，padding 3px 12px
5. **打印适配**：`@media print` 完整覆盖

### 颜色变量

| 用途 | 色值 |
|------|------|
| 头部背景 | `#1a1a1a` |
| 强调色 | `#2563eb` |
| 主文字 | `#1a1a1a` |
| 次文字 | `#666` |
| 辅助文字 | `#999` |
| 分割线 | `#e8e8e8` |
| 标签背景 | `#f5f5f5` |
| 标签文字 | `#444` |
