#!/bin/bash
set -e  # 只要有错误就退出

echo "正在执行数据库迁移..."
python manage.py migrate --noinput

echo "正在收集静态文件..."
python manage.py collectstatic --noinput

echo "初始化完成，启动 supervisord..."
exec "$@"