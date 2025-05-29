from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.html import format_html
from django.conf import settings


# 用户模型Admin
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_staff', 'display_favorite_collections')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        ('合集相关', {
            'fields': ('favorite_collections',),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('favorite_collections',)

    def display_favorite_collections(self, obj):
        """显示用户收藏的合集"""
        return ", ".join([collection.name for collection in obj.favorite_collections.all()])

    display_favorite_collections.short_description = '收藏的合集'


# 合集Admin
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'thumbnail_preview')
    search_fields = ('name', 'creator__username')
    raw_id_fields = ('creator',)

    def thumbnail_preview(self, obj):
        """封面预览"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}{}" style="max-height:100px;">',
                settings.MEDIA_URL,
                obj.thumbnail
            )
        return format_html(
            '<img src="{}" style="max-height:100px;" alt="默认封面">',
            settings.STATIC_URL + 'defaults/collection_default.jpg'
        )

    thumbnail_preview.short_description = '封面预览'


# 分类Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'collection', 'progress')
    list_filter = ('collection__name', 'progress')
    search_fields = ('name',)


# 视频Admin
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'thumbnail_preview', 'duration', 'created_at')
    search_fields = ('title', 'category__name')
    list_filter = ('category__collection__name',)
    raw_id_fields = ('category',)
    readonly_fields = ('duration',)

    def thumbnail_preview(self, obj):
        """缩略图预览"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}{}" style="max-height:80px; object-fit:cover;" alt="{}">',
                settings.MEDIA_URL,
                obj.thumbnail,
                obj.title
            )
        return format_html(
            '<img src="{}" style="max-height:80px;" alt="默认缩略图">',
            settings.STATIC_URL + 'defaults/video_default.jpg'
        )

    thumbnail_preview.short_description = '缩略图'

    def get_readonly_fields(self, request, obj=None):
        """创建后禁止修改时长字段"""
        if obj:
            return ['duration'] + list(super().get_readonly_fields(request, obj))
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        """直接调用模型保存逻辑"""
        obj.save()


# 播放记录Admin
class PlaybackStatAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'progress', 'last_played_at')
    search_fields = ('user__username', 'video__title')
    list_filter = ('last_played_at',)
    raw_id_fields = ('user', 'video')


# 作业Admin
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'deadline', 'display_related_questions')
    list_filter = ('category__collection__name', 'deadline')
    search_fields = ('title', 'description')
    raw_id_fields = ('category',)

    def display_related_questions(self, obj):
        """显示关联的题目"""
        return ", ".join([question.content for question in obj.related_questions.all()])

    display_related_questions.short_description = '关联题目'


# 学习资料Admin
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'url')
    list_filter = ('category__collection__name', 'date')
    search_fields = ('title', 'description')
    raw_id_fields = ('category',)


# 题目Admin
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'type', 'homework', 'score')
    search_fields = ('content', 'homework__title')
    list_filter = ('type', 'homework__category__collection__name')
    raw_id_fields = ('homework',)


# 成绩Admin
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'homework', 'score', 'submitted_at')
    search_fields = ('user__username', 'homework__title')
    list_filter = ('submitted_at', 'homework__category__collection__name')
    raw_id_fields = ('user', 'homework')


# 自定义Admin分组显示
class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        """
        自定义应用列表分组显示
        """
        app_list = super().get_app_list(request)

        # 自定义分组
        custom_app_list = [
            {
                'name': '用户管理',
                'models': [
                    {'name': '用户', 'admin_url': '/admin/core/user/'},
                ]
            },
            {
                'name': '内容管理',
                'models': [
                    {'name': '合集', 'admin_url': '/admin/core/collection/'},
                    {'name': '分类', 'admin_url': '/admin/core/category/'},
                    {'name': '视频', 'admin_url': '/admin/core/video/'},
                ]
            },
            {
                'name': '学习管理',
                'models': [
                    {'name': '作业', 'admin_url': '/admin/core/homework/'},
                    {'name': '学习资料', 'admin_url': '/admin/core/material/'},
                    {'name': '题目', 'admin_url': '/admin/core/question/'},
                ]
            },
            {
                'name': '数据统计',
                'models': [
                    {'name': '播放记录', 'admin_url': '/admin/core/playbackstat/'},
                    {'name': '成绩', 'admin_url': '/admin/core/score/'},
                ]
            },
        ]

        return custom_app_list


# 使用自定义AdminSite
custom_admin_site = CustomAdminSite(name='custom_admin')

# 注册所有模型
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Collection, CollectionAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Video, VideoAdmin)
custom_admin_site.register(PlaybackStat, PlaybackStatAdmin)
custom_admin_site.register(Homework, HomeworkAdmin)
custom_admin_site.register(Material, MaterialAdmin)
custom_admin_site.register(Question, QuestionAdmin)
custom_admin_site.register(Score, ScoreAdmin)

# 自定义Admin标题
custom_admin_site.site_header = "在线学习平台管理"
custom_admin_site.site_title = "平台管理"
custom_admin_site.index_title = "数据管理"
