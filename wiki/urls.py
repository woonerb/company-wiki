from django.urls import path
from . import views

urlpatterns = [
    # 게시글 관련
    path('', views.post_list, name='post_list'),
    path('write/', views.post_create, name='post_new'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:pk>/like/', views.post_like, name='post_like'),
    path('post/<int:pk>/copy/', views.post_copy, name='post_copy'),

    # 댓글 관련
    path('comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),

    # 유틸리티 (이미지 업로드, 태그 추천 등)
    path('upload-image/', views.image_upload, name='image_upload'),
    path('suggest-tags/', views.suggest_tags, name='suggest_tags'),
]