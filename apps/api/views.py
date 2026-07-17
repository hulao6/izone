# -*- coding: utf-8 -*-

from rest_framework import viewsets, permissions
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from webstack.models import NavigationSite

from blog.models import Article, Tag, Category, Timeline
from oauth.models import Ouser
from tool.models import ToolLink
from .serializers import (UserSerializer, ArticleSerializer,
                          TimelineSerializer, TagSerializer,
                          CategorySerializer, ToolLinkSerializer,
                          NavigationSiteSerializer)


# from .permissions import IsAdminUserOrReadOnly

# RESEful API VIEWS
class UserListSet(viewsets.ModelViewSet):
    queryset = Ouser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ArticleListSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    # 使用全局认证方案（TokenAuthentication + SessionAuthentication + BasicAuthentication）
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # 仅返回 is_publish=True 的数据
        return Article.objects.filter(is_publish=True)


class TagListSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class CategoryListSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class TimelineListSet(viewsets.ModelViewSet):
    queryset = Timeline.objects.all()
    serializer_class = TimelineSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class ToolLinkListSet(viewsets.ModelViewSet):
    queryset = ToolLink.objects.all()
    serializer_class = ToolLinkSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)


class NavigationSiteListSet(viewsets.ModelViewSet):
    queryset = NavigationSite.objects.all()
    serializer_class = NavigationSiteSerializer
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        is_show = self.request.query_params.get('is_show', None)
        if is_show == 'true':
            queryset = queryset.filter(is_show=True)
        elif is_show == 'false':
            queryset = queryset.filter(is_show=False)
        return queryset


# ==================== Skill 专用 Views ====================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers as drf_serializers
from blog.models import Topic
from .serializers import SkillCategorySerializer, SkillTagSerializer, SkillTopicSerializer


class SkillMetaView(APIView):
    """聚合返回分类、标签、主题列表，供 skill 匹配决策"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        tags = Tag.objects.all()
        topics = Topic.objects.select_related('subject').all()

        return Response({
            'categories': SkillCategorySerializer(categories, many=True).data,
            'tags': SkillTagSerializer(tags, many=True).data,
            'topics': SkillTopicSerializer(topics, many=True).data,
        })


from .serializers import ArticlePublishSerializer


class SkillArticleQueryView(APIView):
    """按 slug 查询文章，供 skill 判断是创建还是更新"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        slug = request.query_params.get('slug', '').strip()
        if not slug:
            return Response({'success': False, 'error': '请提供 slug 参数'}, status=400)

        try:
            article = Article.objects.get(slug=slug)
            return Response({
                'success': True,
                'exists': True,
                'article': {
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'summary': article.summary,
                    'body': article.body,
                    'is_publish': article.is_publish,
                    'is_top': article.is_top,
                    'category': article.category.name if article.category else None,
                    'tags': [t.name for t in article.tags.all()],
                    'topic': article.topic.name if article.topic else None,
                    'create_date': article.create_date.strftime('%Y-%m-%d %H:%M'),
                    'update_date': article.update_date.strftime('%Y-%m-%d %H:%M'),
                }
            })
        except Article.DoesNotExist:
            return Response({'success': True, 'exists': False})


class SkillPublishView(APIView):
    """Skill 专用文章发布/更新接口，slug 已存在则更新，否则创建"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        slug = request.data.get('slug', '')
        article = Article.objects.filter(slug=slug).first() if slug else None
        is_update = article is not None

        serializer = ArticlePublishSerializer(
            article, data=request.data, context={'request': request}
        ) if is_update else ArticlePublishSerializer(
            data=request.data, context={'request': request}
        )

        if not serializer.is_valid():
            errors = serializer.errors
            first_field = next(iter(errors))
            first_error = errors[first_field]
            if isinstance(first_error, list):
                msg = first_error[0]
            elif isinstance(first_error, dict):
                nested_field = next(iter(first_error))
                msg = f"{first_field}.{nested_field}: {first_error[nested_field][0]}"
            else:
                msg = str(first_error)
            return Response({'success': False, 'error': msg}, status=400)

        try:
            article = serializer.save()
            return Response({
                'success': True,
                'id': article.id,
                'url': article.get_absolute_url(),
                'title': article.title,
                'action': 'update' if is_update else 'create',
            }, status=200 if is_update else 201)
        except drf_serializers.ValidationError as e:
            detail = e.detail
            msg = detail[0] if isinstance(detail, list) else str(detail)
            return Response({'success': False, 'error': msg}, status=400)
