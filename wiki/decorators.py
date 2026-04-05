from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import get_object_or_404
from .models import Post, Node

def node_permission_required(perm_type='read'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. 관리자(슈퍼유저)는 모든 권한 체크를 무시하고 통과
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # URL 패턴에서 ID 가져오기
            node_id = kwargs.get('node_id')
            post_id = kwargs.get('pk') or kwargs.get('post_id')
            
            target_node = None
            
            # 2. 게시글 ID가 있는 경우
            if post_id:
                post = get_object_or_404(Post, pk=post_id)
                # 작성자 본인이라면 수정/삭제 권한 허용 (선택 사항)
                if post.author == request.user and perm_type in ['read', 'edit']:
                    return view_func(request, *args, **kwargs)
                target_node = post.node
            
            # 3. 노드 ID가 직접 전달된 경우
            elif node_id:
                target_node = get_object_or_404(Node, pk=node_id)
            
            # 4. 권한 최종 확인 (Node 모델의 has_perm 메서드 사용)
            if target_node and target_node.has_perm(request.user, perm_type):
                return view_func(request, *args, **kwargs)
            
            # 모든 조건에 해당하지 않으면 거부
            raise PermissionDenied(f"이 페이지에 대한 {perm_type} 권한이 없습니다.")
            
        return _wrapped_view
    return decorator