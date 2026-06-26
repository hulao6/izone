# izone

一个以 Django 框架搭建的个人博客系统。

线上地址：https://tendcode.com/

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 2.2 + Python 3.9 |
| 数据库 | MySQL（utf8mb4） |
| 缓存 / 消息队列 | Redis |
| 异步任务 | Celery 4.4（Worker + Beat） |
| 搜索引擎 | Whoosh + Jieba 中文分词 + django-haystack |
| 前端 | Bootstrap 4 + jQuery |
| 容器化 | Docker + Gunicorn + Supervisord |

## 文档索引

| 文档 | 说明 |
|------|------|
| [产品需求规格说明书](docs/design/01_PRD_产品需求规格说明书.md) | 产品需求，包含功能列表和非功能需求 |
| [架构设计文档](docs/design/02_TDD_架构设计文档.md) | 技术选型、模块划分、部署架构 |
| [数据库设计文档](docs/design/03_ERD_数据库设计文档.md) | 实体定义、关系说明、设计决策 |
| [API 接口文档](docs/design/04_API_接口文档.md) | 各应用 JSON API 端点 |

## 功能

- Django 后台管理系统，方便管理文章、用户及其他动态内容
- 文章分类、标签、专题（Subject → Topic → Article）层级结构
- 全文搜索（Whoosh + Jieba 中文分词，实时索引更新）
- 文章评论系统（二级回复、微博表情、Markdown）、评论通知
- 用户认证（Django 用户系统 + OAuth 微博/GitHub 第三方登录）
- 浏览量统计（爬虫过滤、session 去重、每日快照）
- 友链管理（在线申请、定时自动校链）
- RSS 订阅、Sitemap 网站地图、百度 SEO 推送
- RESTful API（条件启用，DRF DefaultRouter）
- 在线工具（条件启用）、服务监控、导航网站、流程图
- 响应式设计（PC / iPad / 手机），暗色主题支持
- Redis 缓存系统，Celery 定时任务调度

## 快速开始

### Docker 部署

```bash
# 构建镜像
docker build -t hopetree/izone:lts .

# slim 镜像（国内构建）
docker build --build-arg pip_index_url=http://mirrors.aliyun.com/pypi/simple/ \
             --build-arg pip_trusted_host=mirrors.aliyun.com \
             --build-arg debian_host=mirrors.ustc.edu.cn \
             -f Dockerfile-slim -t hopetree/izone:lts .

# 运行（需要预先启动 MySQL 和 Redis）
docker run -d \
  -e IZONE_MYSQL_HOST=mysql_host \
  -e IZONE_MYSQL_PASSWORD=your_password \
  -e IZONE_REDIS_HOST=redis_host \
  -p 8000:8000 \
  hopetree/izone:lts
```

### 本地开发

```bash
# 安装依赖
python -m venv env
source env/bin/activate
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 构建搜索索引
python manage.py rebuild_index

# 启动开发服务器
python manage.py runserver

# 启动 Celery（可选，异步任务需要）
celery -A izone worker -l info
celery -A izone beat -l info
```

## 环境变量

关键配置通过环境变量注入，完整列表见 [架构设计文档](docs/design/02_TDD_架构设计文档.md)。

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `IZONE_DEBUG` | 调试模式 | `True` |
| `IZONE_MYSQL_HOST` | MySQL 主机 | `127.0.0.1` |
| `IZONE_MYSQL_PASSWORD` | 数据库密码 | `python` |
| `IZONE_REDIS_HOST` | Redis 主机 | `127.0.0.1` |
| `IZONE_TOOL_FLAG` | 启用在线工具 | `True` |
| `IZONE_API_FLAG` | 启用 REST API | `False` |

## 项目结构

```
izone/
├── izone/              # Django 项目配置（settings/urls/wsgi）
├── apps/               # 所有 Django 应用
│   ├── blog/           # 核心博客应用
│   ├── oauth/          # 自定义用户模型 + OAuth 认证
│   ├── comment/        # 评论与通知系统
│   ├── easytask/       # Celery 异步任务
│   ├── api/            # REST API（条件启用）
│   ├── tool/           # 在线工具（条件启用）
│   ├── monitor/        # 服务监控
│   └── ...             # webstack, resume, flow, portinfo, rsshub
├── templates/          # 共享模板
├── utils/              # 共享工具（Markdown 扩展等）
├── docs/design/        # 设计文档
├── Dockerfile
└── manage.py
```

## 许可

[MIT License](LICENSE)
=======
一个以 Django 作为框架搭建的个人博客。

博客效果： https://tendcode.com/

## 功能介绍
- Django 自带的后台管理系统，方便对于文章、用户及其他动态内容的管理
- 文章分类、标签、浏览量统计以及规范的 SEO 设置
- 用户认证系统，在 Django 自带的用户系统的基础上扩展 Oauth 认证，支持微博、Github 等第三方认证
- 文章评论系统，炫酷的输入框特效，支持 markdown 语法，二级评论结构和回复功能
- 信息提醒功能，登录和退出提醒，收到评论和回复提醒，信息管理
- 强大的全文搜索功能，只需要输入关键词就能展现全站与之关联的文章
- RSS 博客订阅功能及规范的 Sitemap 网站地图
- 实用的在线工具
- 友情链接和推荐工具网站的展示
- 缓存系统，遵循缓存原则，加速网站打开速度
- RESTful API 风格的 API 接口

## 博客页面效果（响应式）
- PC 页面效果

![PC首页](https://github.com/Hopetree/izone/assets/30201215/e221d09b-9921-4707-977d-95c263d282b6)

- PC 暗色主题效果

![PC首页暗色主题](https://github.com/Hopetree/izone/assets/30201215/ca505bfc-e5d0-40a1-b501-946975c03f73)

- PC 文章详情页，左边显示专题目录，右边显示文章目录，支持代码高亮

![PC文章页面](https://github.com/Hopetree/izone/assets/30201215/0c219bbd-6f29-4866-a827-6e98536f689a)

- PC 专题页，按文章归类

![PC 专题页，按文章归类](https://github.com/Hopetree/izone/assets/30201215/c0a828cc-2201-438b-a983-0c6c04a429c4)

- 云监控服务，提供服务器的监控能力，客户端提供 Golang 版本，也可以自行编写 Python 版本的客户端用来上报数据

![20240404_232431 (1)](https://github.com/Hopetree/izone/assets/30201215/038200c3-1ada-4ab2-9ac5-42848a80ee21)

- PC 友情链接页，定时任务自动校验网址有效性

![PC 友情链接页](https://github.com/Hopetree/izone/assets/30201215/033cdd61-75cf-41b4-bb45-9b45948daf3a)

- PC 在线工具，平台自带工具

![PC 在线工具](https://github.com/Hopetree/izone/assets/30201215/8336fd89-916b-49e5-94f2-a5a72e990158)

- ipad 效果

![ipad](https://user-images.githubusercontent.com/30201215/60588800-7e558800-9dca-11e9-8beb-5d2dcf01b869.jpg)

- 手机效果

![iphone](https://user-images.githubusercontent.com/30201215/60588832-8e6d6780-9dca-11e9-84fa-f1d71510c81e.jpg)

## 运行指导
- 由于本项目分为几个不同的分支，每个分支的功能是一样的，但是运行的方式不同，所以需要根据分支查看对应的运行wiki
- 指导 wiki：https://github.com/Hopetree/izone/wiki
- 部署指导完整步骤：https://tendcode.com/subject/article/izone-install-docs/
