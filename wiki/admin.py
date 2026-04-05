from django.contrib import admin
from .models import KnowledgeNode, NodePermission

class NodePermissionInline(admin.TabularInline):
    model = NodePermission
    extra = 1

@admin.register(KnowledgeNode)
class KnowledgeNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    inlines = [NodePermissionInline] # 노드 관리 화면에서 바로 권한 설정 가능