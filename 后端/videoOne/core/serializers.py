from rest_framework import serializers
from .models import User, Collection, Category, Video, Homework, Question, Material, PlaybackStat, Score
from django.conf import settings


# 用户序列化器
class UserSerializer(serializers.ModelSerializer):
    favorite_collections = serializers.PrimaryKeyRelatedField(many=True, queryset=Collection.objects.all(),
                                                              required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'favorite_collections']
        extra_kwargs = {'password': {'write_only': True}}


# 视频序列化器
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        extra_kwargs = {
            'url': {'required': False},
            'thumbnail': {'required': False},
        }


# 作业序列化器
class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = '__all__'


# 题目序列化器
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


# 资料序列化器
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.url:
            return request.build_absolute_uri(settings.MEDIA_URL + obj.url)
        return None


# 分类序列化器
class CategorySerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True, required=False)
    homeworks = HomeworkSerializer(many=True, read_only=True, required=False)
    materials = MaterialSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'progress', 'collection', 'videos', 'homeworks', 'materials']


# 合集序列化器
class CollectionSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = '__all__'
        extra_kwargs = {
            'thumbnail': {'required': False},
        }

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return request and request.user in obj.favorited_by.all()


# 播放记录序列化器
class PlaybackStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaybackStat
        fields = '__all__'
        read_only_fields = ('user', 'last_played_at')


# 成绩序列化器
class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'
        read_only_fields = ('submitted_at',)


class FavoriteCourseStatsSerializer(serializers.Serializer):
    playback_stats = PlaybackStatSerializer(many=True)
    videos = VideoSerializer(many=True)
