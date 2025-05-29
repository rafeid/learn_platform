from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, UserViewSet, CollectionViewSet, PlaybackStatViewSet,
    HomeworkViewSet, VideoViewSet, CategoryViewSet, SearchViewSet, hello,
    HomeworkDetailViewSet, UserCenterViewSet, UploadViewSet, MaterialViewSet,ScoreViewSet,
    analyze_course_stats,get_course_scores,get_favorite_course_stats
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'playback-stats', PlaybackStatViewSet, basename='playbackstat')
router.register(r'homeworks', HomeworkViewSet, basename='homework')
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'homework-details', HomeworkDetailViewSet, basename='homeworkdetail')
router.register(r'user-center', UserCenterViewSet, basename='usercenter')
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'score',ScoreViewSet,basename='score')

urlpatterns = [
    path('auth/', include([
        path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
        path('register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    ])),
    path('hello/', hello),
    path('upload/', UploadViewSet.as_view({'post': 'upload'}), name='upload'),
    path('analyze_course_stats/<int:course_id>/', analyze_course_stats, name='analyze_course_stats'),
    path('course-scores/<int:course_id>/', get_course_scores, name='course-scores'),
    path('favorite-course-stats/', get_favorite_course_stats, name='favorite-course-stats'),
    path('', include(router.urls)),
]
