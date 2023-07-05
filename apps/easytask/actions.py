# -*- coding: utf-8 -*-
"""
    定义一些任务的执行操作，将具体的操作从tasks.py里面抽离出来
    每个任务需要饮用的模块放到函数里面引用，方便单独调试函数
"""


def action_update_article_cache():
    """
    更新所有文章的缓存，缓存格式跟文章视图保持一致
    @return:
    """
    from markdown import Markdown
    from markdown.extensions.toc import TocExtension  # 锚点的拓展
    from markdown.extensions.codehilite import CodeHiliteExtension
    from django.core.cache import cache
    from django.utils.text import slugify
    from blog.utils import CustomHtmlFormatter
    from blog.models import Article

    total_num, done_num = 0, 0
    # 查询到所有缓存的key
    keys = cache.keys('article:markdown:*')
    for obj in Article.objects.all():
        total_num += 1
        ud = obj.update_date.strftime("%Y%m%d%H%M%S")
        md_key = f'article:markdown:{obj.id}:{ud}'
        # 设置不存在的缓存
        if md_key not in keys:
            md = Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown_checklist.extension',
                CodeHiliteExtension(pygments_formatter=CustomHtmlFormatter),
                TocExtension(slugify=slugify),
            ])
            # 设置过期时间的时候分散时间，不要设置成同一时间
            cache.set(md_key, (md.convert(obj.body), md.toc), 3600 * 24 + 10 * done_num)
            done_num += 1
    data = {'total': total_num, 'done': done_num}
    return data


def action_check_friend_links(site_link=None, white_list=None):
    """
    检查友链:
        1、检查当前显示的友链，请求友链，将非200的友链标记为不显示，并记录禁用原因
        2、检查当前不显示的友链，请求友链，将200返回的标记为显示，并删除禁用原因
        3、新增补充校验：可以添加参数site_link，则不仅仅校验网页是否打开200，还会校验网站中是否有site_link外链
    @return:
    """
    import re
    import requests
    from blog.models import FriendLink

    def get_link_status(url):
        try:
            resp = requests.get(url, timeout=5, verify=False)
        except Exception:
            return 500, ''
        return resp.status_code, resp.text

    white_list = white_list or []  # 设置白名单，不校验
    active_num = 0
    to_not_show = 0
    to_show = 0
    active_friend_list = FriendLink.objects.filter(is_active=True)
    for active_friend in active_friend_list:
        active_num += 1
        if active_friend.name in white_list:
            continue
        if active_friend.is_show is True:
            code, text = get_link_status(active_friend.link)
            if code != 200:
                active_friend.is_show = False
                active_friend.not_show_reason = f'网页请求状态{code}不等于200'
                active_friend.save(update_fields=['is_show', 'not_show_reason'])
                to_not_show += 1
            else:
                # 设置了网站参数则校验友链中是否包含本站外链
                if site_link:
                    site_check_result = re.findall(site_link, text)
                    if not site_check_result:
                        active_friend.is_show = False
                        active_friend.not_show_reason = f'网站未找到本站外链'
                        active_friend.save(update_fields=['is_show', 'not_show_reason'])
                        to_not_show += 1
        else:
            code, text = get_link_status(active_friend.link)
            if code == 200:
                if not site_link:
                    active_friend.is_show = True
                    active_friend.not_show_reason = ''
                    active_friend.save(update_fields=['is_show', 'not_show_reason'])
                    to_show += 1
                else:
                    site_check_result = re.findall(site_link, text)
                    if site_check_result:
                        active_friend.is_show = True
                        active_friend.not_show_reason = ''
                        active_friend.save(update_fields=['is_show', 'not_show_reason'])
                        to_show += 1
    data = {'active_num': active_num, 'to_not_show': to_not_show, 'to_show': to_show}
    return data


def action_clear_notification(day=200, is_read=True):
    """
    清理消息推送
    @param is_read: False表示清理所有，True表示只清理已读，默认清理已读
    @param day: 清理day天前的信息
    @return:
    """
    from datetime import datetime, timedelta
    from django.db.models import Q
    from comment.models import Notification, SystemNotification

    current_date = datetime.now()
    delta = timedelta(days=day)
    past_date = current_date - delta
    if is_read is True:
        query = Q(create_date__lte=past_date, is_read=True)
    else:
        query = Q(create_date__lte=past_date)

    comment_notification_objects = Notification.objects.filter(query)
    system_notification_objects = SystemNotification.objects.filter(query)
    comment_num = comment_notification_objects.count()
    system_num = system_notification_objects.count()
    comment_notification_objects.delete()
    system_notification_objects.delete()
    return {'comment_num': comment_num, 'system_num': system_num}


if __name__ == '__main__':
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'izone.settings')
    django.setup()

    print(action_clear_notification(100))
