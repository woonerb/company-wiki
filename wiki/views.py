import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from wiki.decorators import node_permission_required
from .models import Node, Post, Comment, PostImage, Tag, NodePermission
from soynlp.noun import NewsNounExtractor
from django.contrib.auth.models import User

# --- [1] 게시글 목록 및 검색 ---
@login_required
def post_list(request):
    # 1. 파라미터 가져오기 (가장 흔한 파라미터명인 'q'와 'search_query' 둘 다 체크 가능)
    search_query = request.GET.get('search_query', request.GET.get('q', '')).strip()
    node_id = request.GET.get('node')
    
    # 2. 기본 쿼리셋 (select_related로 node 정보까지 한 번에 가져옴)
    posts = Post.objects.all().select_related('author', 'node').prefetch_related('tags').order_by('-created_at')
    nodes = Node.objects.all().order_by('order')
    current_node = None 

    # 3. 노드 필터링 (가장 확실한 방법인 node_id=node_id 사용)
    if node_id and node_id.isdigit():
        # 이 부분이 핵심입니다: 직접 node_id 필드와 비교하거나 객체를 가져옵니다.
        try:
            current_node = Node.objects.get(id=int(node_id))
            # 필터링 시 객체를 직접 넣는 것이 가장 정확합니다.
            posts = posts.filter(node=current_node)
        except (Node.DoesNotExist, ValueError):
            current_node = None

    # 4. 검색 필터링 (노드 필터링이 된 상태에서 추가로 적용)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        ).distinct()

    return render(request, 'wiki/post_list.html', {
        'posts': posts,
        'current_node': current_node,
        'nodes': nodes,
        'search_query': search_query,
    })

# --- [2] 특정 태그 클릭 시 모아보기 ---
@login_required
def tag_posts(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    posts = tag.posts.all().order_by('-created_at')
    nodes = Node.objects.all().order_by('order')
    
    return render(request, 'wiki/post_list.html', {
        'posts': posts,
        'tag_name': tag_name,
        'nodes': nodes,
    })

# --- [3] 게시글 상세 및 댓글 ---
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    nodes = Node.objects.all().order_by('order')
    
    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return redirect('post_detail', pk=post.pk)

    return render(request, 'wiki/post_detail.html', {
        'post': post,
        'nodes': nodes,
    })

# --- [4] 게시글 생성 (Editor) ---
@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        node_id = request.POST.get('node') # HTML <select name="node">
        attachment = request.FILES.get('attachment')

        if title and content and node_id:
            # Post 생성 (category 필드에 선택한 노드 ID 저장)
            post = Post.objects.create(
                title=title,
                content=content,
                node_id=node_id,
                attachment=attachment,
                author=request.user
            )

            # 태그 처리
            tag_data = request.POST.get('tags', '')
            if tag_data:
                tag_list = [t.strip() for t in tag_data.replace(',', ' ').split() if t.strip()]
                for name in tag_list:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)
                    
            return redirect('post_detail', pk=post.pk)

    # GET 요청 시: 콤보박스에 뿌려줄 노드 목록 전달
    nodes = Node.objects.all().order_by('order')
    return render(request, 'wiki/editor.html', {'nodes': nodes})

# --- [5] 게시글 수정 ---
@node_permission_required('edit')
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("본인의 글만 수정할 수 있습니다.")

    if request.method == "POST":
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.category = request.POST.get('node') # 수정된 노드 ID 반영
        post.save()

        # 태그 업데이트 (기존 태그 삭제 후 재등록)
        tag_data = request.POST.get('tags', '')
        if tag_data:
            post.tags.clear()
            tag_list = [t.strip() for t in tag_data.replace(',', ' ').split() if t.strip()]
            for name in tag_list:
                tag, _ = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)

        return redirect('post_detail', pk=post.pk)
    
    nodes = Node.objects.all().order_by('order')
    return render(request, 'wiki/editor.html', {
        'post': post,
        'nodes': nodes,
    })

# --- [6] 게시글 삭제/좋아요/복제 ---
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("본인의 글만 삭제할 수 있습니다.")
    post.delete()
    return redirect('post_list')

@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post_detail', args=[str(pk)]))

@login_required
def post_copy(request, pk):
    parent_post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        new_node_id = request.POST.get('node')
        new_post = Post.objects.create(
            title=f"[복사본] {parent_post.title}",
            content=parent_post.content,
            category=new_node_id,
            author=request.user
        )
        return redirect('post_detail', pk=new_post.pk)
    
    nodes = Node.objects.all().order_by('order')
    return render(request, 'wiki/post_copy_form.html', {'post': parent_post, 'nodes': nodes})

# --- [7] 댓글 수정/삭제 ---
@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return HttpResponseForbidden("본인의 댓글만 수정할 수 있습니다.")
    if request.method == "POST":
        comment.content = request.POST.get('content')
        comment.save()
        return redirect('post_detail', pk=comment.post.pk)
    return render(request, 'wiki/comment_form.html', {'comment': comment})

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.author == request.user:
        comment.delete()
    return redirect('post_detail', pk=post_pk)

# --- [8] 이미지 업로드 & 태그 추천 API ---
@login_required
def image_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        img_instance = PostImage.objects.create(image=request.FILES['image'])
        return JsonResponse({'url': img_instance.image.url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def suggest_tags(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            if len(content) < 10: return JsonResponse({'tags': []})
            
            noun_extractor = NewsNounExtractor()
            nouns = noun_extractor.train_extract([content]) 
            suggested = sorted(nouns.keys(), key=lambda x: nouns[x].frequency, reverse=True)
            return JsonResponse({'tags': [w for w in suggested if len(w) > 1][:7]})
        except:
            return JsonResponse({'tags': []})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# --- [9] 지식 노드(트리) 관리 API ---
@login_required
@require_POST
def update_node_api(request):
    try:
        data = json.loads(request.body)
        node = get_object_or_404(Node, id=data.get('id'))


        # 권한 체크
        # 관리자는 권한 체크 통과
        if not request.user.is_superuser:
            if not node.has_user_permission(request.user, 'edit'):
                return JsonResponse({'status': 'error', 'message': '수정 권한이 없습니다.'}, status=403)

            node.name = data.get('name')
            node.save()
            return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def update_node_order_api(request):
    try:
        data = json.loads(request.body)
        node = get_object_or_404(Node, id=data.get('id'))

        if not node.has_user_permission(request.user, 'edit'):
            return JsonResponse({'status': 'error', 'message': '순서 변경 권한이 없습니다.'}, status=403)

        node.order = data.get('position')
        node.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
#------ 지식트리 관리페이지 구현--------------------------    
# 관리 페이지 렌더링
@login_required
def tree_management(request):
    # 다른 조건 없이 무조건 전체 노드를 가져옵니다.
    all_nodes = Node.objects.all().order_by('order')

    # 반드시 'nodes'라는 키값으로 넘겨줘야 템플릿의 {% for node in nodes %}가 작동합니다.
    return render(request, 'wiki/tree_management.html', {
        'nodes': all_nodes, 
    })

# 트리 구조 저장 API (드래그 앤 드롭 결과 저장)
@login_required
@require_POST
def save_tree_api(request):
    try:
        data = json.loads(request.body)
        for item in data:
            node = get_object_or_404(Node, id=item.get('id'))
            p_id = item.get('parent')

            # [핵심] "null" 문자열이나 빈 값, 혹은 자기 자신인 경우 체크
            if not p_id or str(p_id).lower() == 'null' or str(p_id) == str(node.id):
                node.parent = None
            else:
                node.parent = Node.objects.get(id=p_id)

            node.order = item.get('position', 0)
            node.save()
        return JsonResponse({"status": "success", "message": "트리 구조가 저장되었습니다."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

#------ 지식트리 관리페이지 구현--------------------------    


# 권한 부여 API
def update_node_permission(request):
    if request.method == "POST":
        data = json.loads(request.body)
        node_id = data.get('node_id')
        user_email = data.get('email')
        # User 모델에서 이메일로 사용자를 찾아 Node 권한 테이블에 추가하는 로직
        return JsonResponse({"status": "success"})    

def user_search_api(request):
    query = request.GET.get('q', '')
    if len(query) < 2: # 최소 2글자 이상 입력 시 검색
        return JsonResponse({'results': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    )[:10] # 최대 10명만 반환
    
    results = [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]
    return JsonResponse({'results': results})

@require_POST
def add_node_permission(request):
    data = json.loads(request.body)
    node_id = data.get('node_id')
    user_id = data.get('user_id')
    role = data.get('role') # 'read', 'edit', 'all'

    try:
        node = Node.objects.get(id=node_id)
        user = User.objects.get(id=user_id)

        # 기존 권한 초기화 (중복 방지)
        node.viewers.remove(user)
        node.editors.remove(user)
        node.managers.remove(user)

        # 새 권한 부여
        if role == 'read':
            node.viewers.add(user)
        elif role == 'edit':
            node.editors.add(user)
        elif role == 'all':
            node.managers.add(user)

        return JsonResponse({'status': 'success', 'message': f'{user.username}님께 권한을 부여했습니다.'})
    except (Node.DoesNotExist, User.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': '노드 또는 유저를 찾을 수 없습니다.'}, status=404)
