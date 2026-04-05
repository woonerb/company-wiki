from django import template

register = template.Library()  # 이 변수명이 정확히 register여야 합니다.

@register.filter
def children_of(node, all_nodes):
    return [n for n in all_nodes if n.parent_id == node.id]