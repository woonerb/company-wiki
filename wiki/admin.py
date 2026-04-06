from django.contrib import admin
from .models import Node, NodePermission, Post

class NodePermissionInline(admin.TabularInline):
    model = NodePermission
    extra = 1

@admin.register(Node)
class KnowlNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    inlines = [NodePermissionInline] # 노드 관리 화면에서 바로 권한 설정 가능

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
# 1. 목록에 NODE(지식 트리)를 표시합니다.
    list_display = ('title', 'node', 'author', 'created_at')
    
    # 2. 수정 화면에서 'category'를 빼고 'node'를 넣습니다.
    # fields나 fieldsets 설정을 통해 입력창을 제어할 수 있습니다.
    fields = ('title', 'node', 'content', 'author', 'tags') 
    
    # 3. 사이드바 필터에 node를 추가해서 관리하기 편하게 만듭니다.
    list_filter = ('node', 'author')