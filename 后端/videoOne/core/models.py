from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
import subprocess
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def media_path(instance, filename, base_path):
    """通用媒体文件路径生成"""
    timestamp = instance.created_at or timezone.now()
    return os.path.join(base_path,
                        f"{timestamp.year}",
                        f"{timestamp.month:02d}",
                        filename)


def collection_thumb_path(instance, filename):
    return media_path(instance, filename, "collection_thumbs")


def video_thumb_path(instance, filename):
    return media_path(instance, filename, "video_thumbs")


class User(AbstractUser):
    favorite_collections = models.ManyToManyField('Collection', related_name='favorited_by', blank=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Collection(models.Model):
    name = models.CharField('合辑名称', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    thumbnail = models.ImageField(
        '缩略图',
        upload_to=collection_thumb_path,
        blank=True,
        null=True,
        help_text='上传合辑封面图'
    )

    class Meta:
        verbose_name = '合辑'
        verbose_name_plural = verbose_name


class Category(models.Model):
    name = models.CharField('分类名称', max_length=100)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='categories')
    progress = models.PositiveSmallIntegerField('进度', default=0)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name


class Video(models.Model):
    title = models.CharField('标题', max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='videos')
    description = models.TextField('描述', blank=True)
    url = models.FileField('视频地址', upload_to='videos/%Y/%m/')
    duration = models.CharField('时长', max_length=10, default='00:00')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    thumbnail = models.ImageField(
        '缩略图',
        upload_to=video_thumb_path,
        blank=True,
        null=True,
        help_text='上传视频缩略图'
    )

    def save(self, *args, **kwargs):
        # 先保存模型，确保文件写入存储
        super().save(*args, **kwargs)

        # 使用FFmpeg提取视频时长
        if self.url:
            try:
                cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    self.url.path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    duration = result.stdout.strip()
                    if duration:
                        total_seconds = int(float(duration))
                        minutes = total_seconds // 60
                        seconds = total_seconds % 60
                        self.duration = f"{minutes:02d}:{seconds:02d}"
                        super().save(update_fields=['duration'])
            except Exception as e:
                logger.error(f"视频时长提取失败: {str(e)}")

    @property
    def duration_seconds(self):
        """获取秒数格式的时长"""
        if ':' in self.duration:
            parts = list(map(int, self.duration.split(':')))
            return parts[0] * 60 + parts[1]
        return 0

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name


class Homework(models.Model):
    title = models.CharField('标题', max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='homeworks')
    description = models.TextField('描述', blank=True)
    deadline = models.DateTimeField('截止时间')
    related_questions = models.ManyToManyField('Question', related_name='related_homeworks', blank=True)

    class Meta:
        verbose_name = '作业'
        verbose_name_plural = verbose_name


class Material(models.Model):
    title = models.CharField('标题', max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='materials')
    description = models.TextField('描述', blank=True)
    url = models.CharField('资料地址', max_length=200)
    date = models.DateTimeField('日期', auto_now_add=True)

    class Meta:
        verbose_name = '学习资料'
        verbose_name_plural = verbose_name


class Question(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=50)
    content = models.TextField()
    options = models.JSONField()
    score = models.IntegerField()

    class Meta:
        verbose_name = '题目'
        verbose_name_plural = verbose_name


class Score(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='scores')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '成绩'
        verbose_name_plural = verbose_name


class PlaybackStat(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='playback_stats')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playback_stats')
    progress = models.IntegerField()
    duration = models.IntegerField()
    last_played_at = models.DateTimeField()

    class Meta:
        verbose_name = '播放记录'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'video')


@receiver(post_delete, sender=Collection)
def delete_collection_thumbnail(sender, instance, **kwargs):
    """
    删除 Collection 记录时，同步删除对应的缩略图文件。
    """
    if instance.thumbnail:  # 检查是否存在缩略图
        try:
            if os.path.isfile(instance.thumbnail.path):  # 检查文件是否存在
                os.remove(instance.thumbnail.path)  # 删除文件
        except Exception as e:
            print(f"Error deleting file: {e}")  # 捕获并打印异常


@receiver(post_delete, sender=Video)
def delete_video_files(sender, instance, **kwargs):
    # 删除视频文件
    if instance.url:
        try:
            if os.path.isfile(instance.url.path):
                os.remove(instance.url.path)
        except Exception as e:
            logger.error(f"删除视频文件失败: {str(e)}")

    # 删除缩略图文件
    if instance.thumbnail:
        try:
            if os.path.isfile(instance.thumbnail.path):
                os.remove(instance.thumbnail.path)
        except Exception as e:
            logger.error(f"删除缩略图文件失败: {str(e)}")


@receiver(post_delete, sender=Material)
def delete_material_file(sender, instance, **kwargs):
    if instance.url:
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, instance.url)
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
