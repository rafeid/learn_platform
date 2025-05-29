import mimetypes
import os
import uuid
from datetime import datetime
from urllib.parse import quote
from django.contrib.auth import authenticate
from django.http import FileResponse
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from .serializers import *
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PlaybackStat, Collection
from django.db.models import Sum, Count


class IsCreatorOrAdmin(permissions.BasePermission):
    """
    只有创建者或超级管理员才能修改数据。
    """

    def has_object_permission(self, request, view, obj):
        # 允许 GET、HEAD、OPTIONS 请求
        if request.method in permissions.SAFE_METHODS:
            return True

        # 检查当前用户是否是创建者或超级管理员
        return obj.creator == request.user or request.user.is_superuser


@api_view(['GET'])
def hello(request):
    return Response({"message": "Hello from Django!"})


class AuthViewSet(viewsets.GenericViewSet):
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            # 返回完整的用户数据和 token
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data  # 使用 UserSerializer 序列化用户数据
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            token = Token.objects.create(user=user)
            # 返回完整的用户数据和 token
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data  # 使用 UserSerializer 序列化用户数据
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'])
    def get_name(self, request, pk=None):
        user = self.get_object()
        return Response({user.username})


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all()
    permission_classes = [IsCreatorOrAdmin]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        print('Request data:', request.data)
        print('Uploaded files:', request.FILES)
        instance = self.get_object()  # 获取要更新的合辑实例
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)  # 验证数据
        self.perform_update(serializer)  # 执行更新
        return Response(serializer.data)  # 返回更新后的数据

    def perform_update(self, serializer):
        serializer.save()  # 保存更新后的数据

    @action(detail=True, methods=['get'])
    def get_category_resources(self, request, pk=None):
        collection = self.get_object()
        category_id = request.query_params.get('categoryId')
        if not category_id:
            return Response({'error': 'categoryId is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not (request.user.is_staff or collection.id in request.user.favorite_collections.values_list('id',
                                                                                                        flat=True)):
            return Response({'error': '无权限访问该分类'}, status=status.HTTP_403_FORBIDDEN)

        category = Category.objects.get(id=category_id, collection=collection)
        resources = {
            'videos': VideoSerializer(category.videos.all(), many=True).data,
            'homeworks': HomeworkSerializer(category.homeworks.all(), many=True).data,
            'materials': MaterialSerializer(category.materials.all(), many=True).data
        }
        return Response(resources)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        collection = self.get_object()
        request.user.favorite_collections.add(collection)
        return Response({'status': '收藏成功'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfavorite(self, request, pk=None):
        collection = self.get_object()
        request.user.favorite_collections.remove(collection)
        return Response({'status': '取消收藏成功'})

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        if not request.user.is_authenticated:
            return Response({'error': '用户未登录'}, status=status.HTTP_401_UNAUTHORIZED)
        favorite_collections = request.user.favorite_collections.all()
        serializer = self.get_serializer(favorite_collections, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_created_collections(self, request):
        if not request.user.is_authenticated:
            return Response({'error': '用户未登录'}, status=status.HTTP_401_UNAUTHORIZED)
        # 获取当前用户
        user = request.user
        # 过滤出当前用户创建的合辑
        created_collections = Collection.objects.filter(creator=user)
        # 序列化合辑数据
        serializer = self.get_serializer(created_collections, many=True)
        # 返回响应
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def video_stats(self, request, pk=None):
        """
        获取单个课程的视频统计数据
        返回: {
            "total": 总视频数,
            "completed": 已完成视频数(进度>=100),
            "in_progress": 进行中视频数(进度>0但<100),
            "not_started": 未开始视频数(进度=0)
        }
        """
        collection = self.get_object()
        user = request.user

        # 获取该课程的所有视频
        videos = Video.objects.filter(category__collection=collection)
        total_videos = videos.count()

        # 获取用户在该课程的播放记录
        playback_stats = PlaybackStat.objects.filter(
            user=user,
            video__in=videos
        )

        # 统计已完成视频数(进度>=100)
        completed = playback_stats.filter(progress__gte=100).count()

        # 统计进行中视频数(进度>0但<100)
        in_progress = playback_stats.filter(progress__gt=0, progress__lt=100).count()

        # 统计未开始视频数(进度=0)
        not_started = total_videos - completed - in_progress

        return Response({
            "total": total_videos,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started
        })


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class ScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ScoreSerializer
    queryset = Score.objects.all()

    @action(detail=False, methods=['get'])
    def get_course_scores(self, request):
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        scores = Score.objects.filter(homework__category__collection_id=course_id)
        serializer = self.get_serializer(scores, many=True)
        return Response(serializer.data)


class PlaybackStatViewSet(viewsets.ModelViewSet):
    serializer_class = PlaybackStatSerializer

    def get_queryset(self):
        return PlaybackStat.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        user = request.user
        video_id = request.data.get('videoId')
        progress = request.data.get('progress')
        duration = request.data.get('duration')
        try:
            playback, created = PlaybackStat.objects.get_or_create(
                user=user,
                video_id=video_id,
                defaults={
                    'progress': progress,
                    'duration': duration,
                    'last_played_at': timezone.now()
                }
            )
            if not created and float(progress) > float(playback.progress):
                playback.progress = progress
                playback.duration = duration
                playback.last_played_at = timezone.now()
                playback.save()
            elif not created:
                playback.duration = duration
                playback.last_played_at = timezone.now()
                playback.save()
            return Response({'success': True, 'created': created})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def get_playback_stats(self, request):
        try:
            playback_stats = self.get_queryset()
            serializer = self.get_serializer(playback_stats, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = [MultiPartParser, FormParser]  # 添加解析器以处理文件上传

    def create(self, request, *args, **kwargs):
        # 检查是否上传了文件
        if 'url' not in request.data:
            return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建视频对象
        video = Video.objects.create(
            title=request.data.get('title'),
            description=request.data.get('description'),
            duration=request.data.get('duration'),
            category_id=request.data.get('categoryId'),
            thumbnail=request.data.get('thumbnail'),
            url=request.data.get('url')
        )

        serializer = self.get_serializer(video)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 处理缩略图
        thumbnail_url = request.data.get('thumbnail_url')
        if thumbnail_url:
            instance.thumbnail = thumbnail_url

        # 处理视频文件
        video_url = request.data.get('video_url')
        if video_url:
            instance.url = video_url

        # 处理 url 文件
        url_file = request.FILES.get('url')
        if url_file:
            # 保存文件到指定路径
            file_type = 'videos'
            now = datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%M')
            file_name = f"{uuid.uuid4().hex}_{url_file.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, file_type, year, month, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb+') as destination:
                for chunk in url_file.chunks():
                    destination.write(chunk)
            file_url = f"{file_type}/{year}/{month}/{file_name}"
            instance.url = file_url

        # 处理 thumbnail 文件
        thumbnail_file = request.FILES.get('thumbnail')
        if thumbnail_file:
            # 保存文件到指定路径
            file_type = 'video_thumbs'
            now = datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%M')
            file_name = f"{uuid.uuid4().hex}_{thumbnail_file.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, file_type, year, month, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb+') as destination:
                for chunk in thumbnail_file.chunks():
                    destination.write(chunk)
            file_url = f"{file_type}/{year}/{month}/{file_name}"
            instance.thumbnail = file_url

        # 更新其他字段
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 手动保存实例
        instance.save()

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_video_detail(self, request, pk=None):
        video = self.get_object()
        user = request.user

        # 检查播放记录是否存在，如果不存在则创建新记录
        playback, created = PlaybackStat.objects.get_or_create(
            user=user,
            video=video,
            defaults={
                'progress': 0,
                'duration': 0,
                'last_played_at': timezone.now()
            }
        )

        serializer = VideoSerializer(video)
        return Response({
            'video': serializer.data,
            'playback': PlaybackStatSerializer(playback).data
        })

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        user = request.user
        old_password = request.data.get('oldPwd')
        new_password = request.data.get('newPwd')

        if not user.check_password(old_password):
            return Response({'error': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'status': '密码重置成功'})


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=['get'])
    def get_category_resources(self, request, pk=None):
        category = self.get_object()
        resources = {
            'videos': VideoSerializer(category.videos.all(), many=True).data,
            'homeworks': HomeworkSerializer(category.homeworks.all(), many=True).data,
            'materials': MaterialSerializer(category.materials.all(), many=True).data
        }
        return Response(resources)

    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        category = self.get_object()
        resources = {
            'videos': VideoSerializer(category.videos.all(), many=True).data,
            'homeworks': HomeworkSerializer(category.homeworks.all(), many=True).data,
            'materials': MaterialSerializer(category.materials.all(), many=True).data
        }
        return Response(resources)


class SearchViewSet(viewsets.GenericViewSet):
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        collections = Collection.objects.filter(name__icontains=query)
        videos = Video.objects.filter(title__icontains=query)
        homeworks = Homework.objects.filter(title__icontains=query)

        results = {
            'collections': CollectionSerializer(collections, many=True).data,
            'videos': VideoSerializer(videos, many=True).data,
            'homeworks': HomeworkSerializer(homeworks, many=True).data,
        }
        return Response(results)


class HomeworkDetailViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer

    @action(detail=True, methods=['get'])
    def get_homework_detail(self, request, pk=None):
        homework = self.get_object()
        serializer = HomeworkSerializer(homework)
        return Response(serializer.data)


class UserCenterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_user_info(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_user_info(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        homework = self.get_object()
        questions = homework.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    # HomeworkViewSet 中的 save_questions 方法
    @action(detail=True, methods=['post'])
    def save_questions(self, request, pk=None):
        try:
            homework = self.get_object()
            # 直接获取已解析的JSON数据
            questions = request.data.get('questions', [])
            for question_data in questions:
                question, created = Question.objects.update_or_create(
                    id=question_data.get('id'),
                    defaults={
                        'content': question_data.get('content'),
                        'type': question_data.get('type'),
                        'options': question_data.get('options'),
                        'homework': homework,
                        'score': question_data.get('score')
                    }
                )
            return Response({'status': '题目保存成功'})
        except Exception as e:
            return Response({'status': '题目保存失败', 'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        homework = self.get_object()
        answers = request.data.get('answers', [])
        score = 0

        for answer in answers:
            question_id = answer.get('questionId')
            user_answer = answer.get('answer')
            try:
                question = Question.objects.get(id=question_id, homework=homework)

                correct_answers = [option['text'] for option in question.options if option['isCorrect']]

                # 单选题
                if question.type == 'single':
                    if user_answer in correct_answers:
                        score += question.score

                # 多选题
                elif question.type == 'multi':
                    # 将正确答案和用户答案都转换为集合，确保顺序不影响比较
                    correct_answers_set = set(correct_answers)
                    user_answers_set = set(user_answer)
                    if correct_answers_set == user_answers_set:
                        score += question.score

            except Question.DoesNotExist:
                return Response({'error': f'Question with id {question_id} does not exist'},
                                status=status.HTTP_404_NOT_FOUND)

        Score.objects.create(homework=homework, user=request.user, score=score)
        return Response({'score': score})

    @action(detail=True, methods=['get'])
    def scores(self, request, pk=None):
        homework = self.get_object()
        scores = Score.objects.filter(homework=homework)
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_current_user_scores(self, request, pk=None):
        # 获取当前用户
        user = request.user
        # 获取当前作业
        homework = self.get_object()
        # 查询当前用户在当前作业的所有成绩
        scores = Score.objects.filter(homework=homework, user=user)
        # 序列化成绩数据
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadViewSet(viewsets.GenericViewSet):
    @action(detail=False, methods=['post'])
    def upload(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        # 根据文件类型（缩略图或视频）确定保存目录
        if file.content_type.startswith('image'):
            file_type = 'video_thumbs'
        elif file.content_type.startswith('application'):
            file_type = 'materials'
        else:
            file_type = 'videos'  # 视频保存到 videos 目录

        # 按年份和月份细分目录
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')

        # 生成保存路径
        file_name = f"{uuid.uuid4().hex}_{file.name}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_type, year, month, file_name)

        # 确保保存目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 保存文件
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 返回文件的完整 URL
        file_url = f"{file_type}/{year}/{month}/{file_name}"
        return Response({'url': file_url})


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    parser_classes = [MultiPartParser, FormParser]  # 添加解析器以处理文件上传

    def create(self, request, *args, **kwargs):
        # 检查是否上传了文件
        if 'url' not in request.data:
            return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        # 创建资料对象
        material = Material.objects.create(
            title=request.data.get('title'),
            description=request.data.get('description'),
            url=request.data.get('url'),
            category_id=request.data.get('categoryId'),
            date=timezone.now()
        )
        serializer = self.get_serializer(material)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 处理文件上传
        if 'url' in request.FILES:
            file = request.FILES['url']
            file_type = 'materials'  # 文件保存到 materials 目录
            now = timezone.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            file_name = f"{uuid.uuid4().hex}_{file.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, file_type, year, month, file_name)

            # 确保保存目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # 获取文件的完整 URL
            file_url = f"{file_type}/{year}/{month}/{file_name}"
            instance.url = file_url

        # 更新其他字段
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        material = self.get_object()
        file_path = os.path.join(settings.MEDIA_ROOT, material.url)

        if os.path.exists(file_path):
            # 动态设置 Content-Type
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'  # 默认的二进制流类型

            # 对文件名进行 URL 编码
            filename = os.path.basename(file_path)
            encoded_filename = quote(filename)

            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"'
            print(f"File path: {file_path}")
            print(f"Content-Disposition: {response['Content-Disposition']}")
            return response
        return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def analyze_course_stats(request, course_id):
    try:
        # 统计课程中所有视频的数量
        total_videos = Video.objects.filter(category__collection_id=course_id).count()
        total_progress_max = total_videos * 100  # 课程的总进度上限

        # 获取播放统计数据，并按用户聚合总进度
        user_course_stats = PlaybackStat.objects.filter(video__category__collection_id=course_id) \
            .values('user__username') \
            .annotate(total_progress_sum=Sum('progress')) \
            .annotate(total_progress=Sum('progress') / total_progress_max * 100) \
            .order_by('-total_progress')

        # 获取进度前十和倒数前十的用户
        top_10 = user_course_stats[:10]
        bottom_10 = user_course_stats.reverse()[:10]

        # 计算完成率超过80%的用户占比
        total_users = user_course_stats.count()
        completed_users = user_course_stats.filter(total_progress__gte=80).count()
        pie_data = [
            {'value': completed_users, 'name': '完成率超过80%'},
            {'value': total_users - completed_users, 'name': '完成率低于80%'},
        ]

        # 返回结果
        return Response({
            'top_10': [{'username': stat['user__username'], 'progress': stat['total_progress']} for stat in top_10],
            'bottom_10': [{'username': stat['user__username'], 'progress': stat['total_progress']} for stat in
                          bottom_10],
            'pie_data': pie_data,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def get_course_scores(request, course_id):
    # 获取某个课程的分数数据
    scores = Score.objects.filter(homework__category__collection_id=course_id, user=request.user)
    serializer = ScoreSerializer(scores, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_favorite_course_stats(request):
    user = request.user
    # 获取用户喜欢的课程ID
    favorite_collection_ids = user.favorite_collections.values_list('id', flat=True)

    # 获取用户喜欢的课程的播放记录
    playback_stats = PlaybackStat.objects.filter(
        user=user,
        video__category__collection__id__in=favorite_collection_ids
    )

    # 获取用户喜欢的课程的视频数据
    videos = Video.objects.filter(
        category__collection__id__in=favorite_collection_ids
    )

    # 序列化数据
    serializer = FavoriteCourseStatsSerializer({
        "playback_stats": playback_stats,
        "videos": videos
    })

    return Response(serializer.data)
