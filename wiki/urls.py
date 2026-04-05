from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('write/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('upload-image/', views.image_upload, name='image_upload'),
    path('suggest-tags/', views.suggest_tags, name='suggest_tags'),

    path('post/<int:pk>/like/', views.post_like, name='post_like'), # 좋아요 기능   
 
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'), # 글 수정 (pk는 게시글의 고유 번호)
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'), # 글 삭제
    path('comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'), # 댓글 수정 (pk는 게시글의 고유 번호)
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'), # 댓글 삭제 (댓글의 pk를 사용)
]