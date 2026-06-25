# API 接口文档

> **项目名称**：izone（TendCode 个人博客）
> **最后更新**：2026-06-25

---

## 1. 概述

izone 的 API 以散落在各应用中的视图函数形式提供，返回 JSON 响应。大部分写操作接口要求 AJAX 请求方式。

---

## 2. Blog 应用 API

挂载于根路径 `/`。

### 2.1 更新文章

```
POST /article-update/
```

| 项目 | 说明 |
|------|------|
| 请求方式 | POST（AJAX） |
| 鉴权 | 作者本人或超级管理员 |
| Content-Type | `application/x-www-form-urlencoded` |

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| article_slug | string | 是 | 文章 slug 标识 |
| article_body | string | 是 | 更新后的 Markdown 内容 |
| article_img_link | string | 否 | 新的封面图地址 |
| change_img_link_flag | string | 否 | 值为 `"true"` 时更新封面图 |

**成功响应**：
```json
{
  "message": "Success",
  "code": 0,
  "data": {
    "callback": "/article/hello-world/"
  }
}
```

---

### 2.2 友链申请

```
POST /friend/add/
```

| 项目 | 说明 |
|------|------|
| 请求方式 | POST（AJAX） |
| 鉴权 | 无需登录 |

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 网站名称 |
| description | string | 否 | 网站描述 |
| link | string | 是 | 友链地址（完整 URL） |

**成功响应**：
```json
{
  "code": 0,
  "data": { "id": 1 },
  "message": "",
  "error": ""
}
```

提交后 `is_active=False`, `is_show=True`，等待管理员审核。

---

### 2.3 笔记列表

```
GET /api/notes/
```

| 项目 | 说明 |
|------|------|
| 请求方式 | GET |
| 鉴权 | 无需登录 |

**响应**（JSON 数组）：
```json
[
  {
    "title": "笔记标题",
    "content": "笔记内容（Markdown）",
    "tags": ["Python", "Django"]
  }
]
```

仅返回 `is_publish=True` 的笔记，按创建时间倒序排列。

---

### 2.4 专题 JSON 数据

```
GET /vitepress/subjects/
```

| 项目 | 说明 |
|------|------|
| 请求方式 | GET / POST |
| 鉴权 | 无（CSRF exempt） |

**响应**：
```json
{
  "code": 0,
  "error": "",
  "data": [
    {
      "name": "专题名称",
      "description": "描述",
      "pk": "1",
      "items": [
        {
          "name": "主题名称",
          "items": [
            { "title": "文章标题", "slug": "article-slug" }
          ]
        }
      ]
    }
  ]
}
```

返回所有专题的完整层级结构（Subject → Topic → Article）。

---

### 2.5 Celery 任务管理

```
GET  /task/run/      # 查看定时任务列表（仅管理员）
POST /task/execute/  # 手动触发 Celery 任务（仅管理员）
```

**execute 请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_name | string | 是 | 任务名称（如 `easytask.tasks.update_cache`） |
| args | JSON string | 否 | 位置参数，JSON 数组格式，默认 `"[]"` |
| kwargs | JSON string | 否 | 关键字参数，JSON 对象格式，默认 `"{}"` |

**成功响应**：
```json
{
  "message": "Task executed",
  "task_id": "uuid-string",
  "task_status": "PENDING"
}
```

---

## 3. Comment 应用 API

挂载于 `/comment/`。

### 3.1 提交评论

```
POST /comment/add/
```

| 项目 | 说明 |
|------|------|
| 请求方式 | POST（AJAX） |
| 鉴权 | 需要登录 |

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| article_id | int | 是 | 文章 ID |
| content | string | 是 | 评论内容（最大 1048 字符） |
| rep_id | int | 否 | 回复的目标评论 ID（为空则为顶级评论） |

**成功响应**：
```json
{ "msg": "评论提交成功！", "new_point": "#com-123" }
```

**错误响应**：
```json
{ "msg": "你的评论字数超过1048，无法保存。" }
```

---

### 3.2 通知管理

```
POST /comment/notification/mark-to-read/    # 标记已读
POST /comment/notification/mark-to-delete/  # 删除通知
```

| 项目 | 说明 |
|------|------|
| 请求方式 | POST（AJAX） |
| 鉴权 | 需要登录 |

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 通知 ID |
| tag | string | 是 | 通知类型：`"comment"` 或 `"system"` |

**成功响应**：
```json
{ "msg": "mark success", "code": 0 }
```

---

## 4. Monitor 应用 API

挂载于 `/monitor/`。

### 4.1 获取服务器列表

```
GET /monitor/servers
```

返回 JSON 格式的监控服务器列表及当前状态数据。

### 4.2 客户端上报数据

```
POST /monitor/server/push
```

| 项目 | 说明 |
|------|------|
| 鉴权 | 加密凭证（`secret_key` 解密验证 username/password/push_url） |
| Content-Type | `application/json` |

客户端（Golang/Python）定期向此端点上报服务器运行数据，数据以加密形式传输。`secret_key` 和 `secret_value` 在 `MonitorServer` 模型保存时自动生成。

---

## 5. Flow 应用 API

挂载于 `/flow/`。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/flow/api/processes/` | 流程图列表 |
| POST | `/flow/api/processes/create/` | 创建流程图 |
| GET | `/flow/api/processes/<id>/` | 流程图详情 |
| POST | `/flow/api/processes/<id>/update/` | 更新流程图 |
| POST | `/flow/api/processes/<id>/delete/` | 删除流程图 |

**流程图 JSON 结构**：
```json
{
  "id": 1,
  "name": "流程名称",
  "description": "描述",
  "data": { "nodes": [...], "edges": [...] }
}
```

---

## 6. DRF REST API

条件启用（`API_FLAG=True`，默认关闭），由 Django REST Framework DefaultRouter 提供标准 RESTful 接口。挂载于 `/openapi/v1/`。

### 6.1 文章

```
GET    /openapi/v1/articles/         # 文章列表
POST   /openapi/v1/articles/         # 创建文章
GET    /openapi/v1/articles/{id}/    # 文章详情
PUT    /openapi/v1/articles/{id}/    # 全量更新
PATCH  /openapi/v1/articles/{id}/    # 部分更新
DELETE /openapi/v1/articles/{id}/    # 删除文章
```

| 项目 | 说明 |
|------|------|
| 权限 | `IsAdminUser`（全部操作需管理员） |
| 认证 | BasicAuth / SessionAuth |
| 过滤 | 仅返回 `is_publish=True` 的文章 |

`ArticleSerializer` 嵌套了 `CategorySerializer`（分类详情）和 `TagSerializer`（标签列表），keywords 以 `SlugRelatedField` 展示名称数组。

### 6.2 标签

```
GET    /openapi/v1/tags/
POST   /openapi/v1/tags/
GET    /openapi/v1/tags/{id}/
PUT    /openapi/v1/tags/{id}/
PATCH  /openapi/v1/tags/{id}/
DELETE /openapi/v1/tags/{id}/
```

权限：`DjangoModelPermissionsOrAnonReadOnly`（读公开，写需模型权限）。

### 6.3 分类

```
GET    /openapi/v1/categorys/
POST   /openapi/v1/categorys/
GET    /openapi/v1/categorys/{id}/
PUT    /openapi/v1/categorys/{id}/
PATCH  /openapi/v1/categorys/{id}/
DELETE /openapi/v1/categorys/{id}/
```

权限：`DjangoModelPermissionsOrAnonReadOnly`。

### 6.4 时间线

```
GET    /openapi/v1/timelines/
POST   /openapi/v1/timelines/
GET    /openapi/v1/timelines/{id}/
PUT    /openapi/v1/timelines/{id}/
PATCH  /openapi/v1/timelines/{id}/
DELETE /openapi/v1/timelines/{id}/
```

权限：`DjangoModelPermissionsOrAnonReadOnly`。

### 6.5 工具链接

```
GET    /openapi/v1/toollinks/
POST   /openapi/v1/toollinks/
GET    /openapi/v1/toollinks/{id}/
PUT    /openapi/v1/toollinks/{id}/
PATCH  /openapi/v1/toollinks/{id}/
DELETE /openapi/v1/toollinks/{id}/
```

权限：`DjangoModelPermissionsOrAnonReadOnly`。序列化器嵌套 `ToolCategorySerializer`。

### 6.6 导航网站

```
GET    /openapi/v1/navigation/
POST   /openapi/v1/navigation/
GET    /openapi/v1/navigation/{id}/
PUT    /openapi/v1/navigation/{id}/
PATCH  /openapi/v1/navigation/{id}/
DELETE /openapi/v1/navigation/{id}/
```

权限：`DjangoModelPermissionsOrAnonReadOnly`。支持查询过滤 `?is_show=true` 或 `?is_show=false`。序列化器含 `menu` 只读字段。

### 6.7 全局配置

| 项目 | 配置值 |
|------|--------|
| 分页 | `LimitOffsetPagination`，每页 20 条 |
| 全局默认权限 | `AllowAny` |
| 启用条件 | 环境变量 `IZONE_API_FLAG=True` |

---

## 7. 通用说明

### 通用响应格式（Blog 工具类）

`blog.utils.ApiResponse` 系列类定义的响应格式：

```json
{
  "code": 0,        // 0=成功, 1=失败
  "data": {},       // 业务数据
  "message": "",    // 成功消息
  "error": ""       // 错误信息
}
```

### AJAX 要求

大部分 POST 接口要求请求头包含 `X-Requested-With: XMLHttpRequest`（Django `is_ajax()` 方法检测）。
