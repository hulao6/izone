# API Reference

## Endpoints

Base URL: `$IZONE_API_BASE` (e.g. `http://127.0.0.1:8000/openapi/v1`)

### GET /skill/meta/

Returns all existing categories, tags, and topics for matching.

**Auth:** `Authorization: Token <token>`

**Response 200:**

```json
{
  "categories": [
    { "id": 1, "name": "Python Web开发", "slug": "Python-Web-development", "description": "..." },
    { "id": 2, "name": "Linux 笔记", "slug": "linux-notes", "description": "..." }
  ],
  "tags": [
    { "id": 1, "name": "Python", "slug": "python", "description": "..." },
    { "id": 2, "name": "Django", "slug": "django", "description": "..." }
  ],
  "topics": [
    {
      "id": 1,
      "name": "安装部署",
      "subject_id": 1,
      "subject_name": "Django实战系列",
      "subject_status": "ongoing"
    }
  ]
}
```

### POST /skill/articles/publish/

Create a new article (draft by default).

**Auth:** `Authorization: Token <token>`

**Request body:**

```json
{
  "title": "文章标题",
  "slug": "article-slug",
  "body": "markdown 正文",
  "summary": "文章摘要",
  "is_publish": false,
  "is_top": false,
  "category": {
    "name": "分类名",
    "slug": "category-slug",
    "description": "SEO描述"
  },
  "tags": [
    { "name": "标签名", "slug": "tag-slug", "description": "SEO描述" }
  ],
  "keywords": ["关键词1", "关键词2"],
  "topic": { "id": 1, "name": "主题名" },
  "topic_order": 99,
  "topic_short_title": ""
}
```

**Response 201 (success):**

```json
{
  "success": true,
  "id": 42,
  "url": "/article/article-slug/",
  "title": "文章标题"
}
```

**Response 400 (error):**

```json
{"success": false, "error": "中文错误描述"}
```

## Field Constraints

All constraints derive from the Django model definitions.

### Article Fields

| Field | Type | Required | Max Length | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `title` | string | **yes** | 150 | — | |
| `slug` | string | **yes** | 50 | — | Unique. Lowercase, hyphens. |
| `body` | string | **yes** | — | — | Raw markdown. |
| `summary` | string | **yes** | 230 | — | AI-generated, not truncated. |
| `is_publish` | boolean | no | — | `false` | Draft mode. When later set to `true`, `create_date` resets to publish time. |
| `is_top` | boolean | no | — | `false` | |
| `img_link` | — | — | — | — | **Never send.** Uses default image. |

### Category Object

| Field | Type | Required | Max Length | Notes |
|-------|------|----------|------------|-------|
| `name` | string | **yes** | 20 | Not unique (slug is). Lookup uses `.filter().first()`. |
| `slug` | string | **yes** | 50 | Unique. |
| `description` | string | yes | 240 | Default placeholder: "分类描述". |

### Tag Object

| Field | Type | Required | Max Length | Notes |
|-------|------|----------|------------|-------|
| `name` | string | **yes** | 20 | Not unique (slug is). |
| `slug` | string | **yes** | 50 | Unique. |
| `description` | string | yes | 240 | Default placeholder: "标签描述". |

### Topic Object

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | integer | no | Preferred lookup method |
| `name` | string | no | Fallback lookup. **Never auto-created.** |

### Keyword

Array of strings, each ≤20 chars. Get-or-create by name.

## Server-Side Behavior

### Category/Tag: Get-or-Create + Description Update

- If `name` matches existing → reuse, update `description` if the incoming value is better (not the placeholder "分类描述"/"标签描述")
- If `name` is new → create with AI-provided `slug` and `description`
- If `slug` conflicts with an existing different-named record → error

### Topic: Lookup Only

- Lookup by `id` first, then by `name`
- If not found → error with list of available topic names
- Never auto-created

### Keywords: Simple Get-or-Create

- `Keyword.objects.get_or_create(name=name)` for each entry

### Author

Automatically set from the authenticated user (via Token).
