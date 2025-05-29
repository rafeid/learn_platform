from django.apps import AppConfig

class App01Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = '学习平台数据管理'