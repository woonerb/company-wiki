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
    path('tag/<str:tag_name>/', views.tag_posts, name='tag_posts'),

    # 댓글 관련
    path('comment/<int:pk>/edit/', views.comment_edit, name='comment_edit'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),

    # 유틸리티 (이미지 업로드, 태그 추천 등)
    path('upload-image/', views.image_upload, name='image_upload'),
    path('suggest-tags/', views.suggest_tags, name='suggest_tags'),

    # 지식 트리 수정을 위한 API 경로
    path('node/update/', views.update_node_api, name='update_node_api'),
    path('node/update-order/', views.update_node_order_api, name='update_node_order_api'),

    # 지식 트리 관리 페이지 구현
    path('manage/tree/', views.tree_management, name='tree_management'),
    path('api/node/save-structure/', views.save_tree_api, name='save_tree_api'),
    path('api/node/permission/', views.update_node_permission, name='update_node_permission'),

    path('api/user/search/', views.user_search_api, name='user_search_api'),
    path('api/node/permission/add/', views.add_node_permission, name='add_node_permission'),
]