import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import Post, Comment, PostImage
from soynlp.noun import NewsNounExtractor

# --- [1] 게시글 목록 및 검색 ---
@login_required
def post_list(request):
    # 1. 검색어 가져오기 및 공백 제거
    search_query = request.GET.get('q', '').strip()
    
    # 2. 기본 쿼리셋 설정 (최신순 정렬)
    posts = Post.objects.all().order_by('-created_at')

    # 3. 검색어가 있을 경우 필터링 수행
    if search_query:
        # filter() 내부의 Q 객체들은 데이터베이스 레벨에서 효율적으로 처리됩니다.
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query) | # ManyToMany 관계 검색
            Q(author__username__icontains=search_query)
        ).distinct() # 다대다 관계 검색 시 발생하는 중복 행 제거

    # 4. 템플릿 렌더링
    return render(request, 'wiki/post_list.html', {
        'posts': posts,
        'search_query': search_query
    })

#------특정 태그 클릭시 모아보기 기능----
@login_required
def tag_posts(request, tag_name):
    # 해당 이름의 태그를 찾고 (없으면 404 에러)
    tag = get_object_or_404(Tag, name=tag_name)
    
    # 해당 태그와 연결된 모든 게시글 가져오기 (0.001초 만에!)
    posts = tag.posts.all().order_by('-created_at')
    
    return render(request, 'wiki/post_list.html', {
        'posts': posts,
        'tag_name': tag_name
    })
#------특정 태그 클릭시 모아보기 기능----


# --- [2] 게시글 상세 및 댓글 등록 ---
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == "POST":  # 댓글 등록 로직
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return redirect('post_detail', pk=post.pk)

    return render(request, 'wiki/post_detail.html', {'post': post})

# --- [3] 게시글 생성 ---
@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        tags = request.POST.get('tags')
        attachment = request.FILES.get('attachment')

        if title and content:
            post = Post.objects.create(
                title=title,
                content=content,
                category=category,
                attachment=attachment,
                author=request.user
            )

            # 태그 처리 로직 추가
            tag_data = request.POST.get('tags', '') # 폼에서 '어음,주간업무' 형태로 올 경우
            if tag_data:
                tag_list = [t.strip() for t in tag_data.replace(',', ' ').split() if t.strip()]
                for name in tag_list:
                    tag, created = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag) # ManyToMany 관계에 추가
                    
            return redirect('post_detail', pk=post.pk)

    return render(request, 'wiki/editor.html')

# --- [4] 게시글 수정/삭제/좋아요/복제 ---
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("본인의 글만 수정할 수 있습니다.")

    if request.method == "POST":
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.category = request.POST.get('category')
        post.save()
        return redirect('post_detail', pk=post.pk)

    return render(request, 'wiki/post_form.html', {'post': post})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("본인의 글만 삭제할 수 있습니다.")
    
    if request.method == "POST":
        post.delete()
        return redirect('post_list')
    return redirect('post_detail', pk=pk)

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
        new_category = request.POST.get('category')
        new_post = Post.objects.create(
            title=f"[복사본] {parent_post.title}",
            content=parent_post.content,
            category=new_category,
            author=request.user
        )
        return redirect('post_detail', pk=new_post.pk)
    return render(request, 'wiki/post_copy_form.html', {'post': parent_post})

# --- [5] 댓글 수정/삭제 ---
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
    if comment.author != request.user:
        return HttpResponseForbidden("본인의 댓글만 삭제할 수 있습니다.")
    
    if request.method == "POST":
        comment.delete()
    return redirect('post_detail', pk=post_pk)

# --- [6] 유틸리티 (이미지 업로드 & 태그 추천) ---
@login_required
def image_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        img_file = request.FILES['image']
        img_instance = PostImage.objects.create(image=img_file)
        return JsonResponse({'url': img_instance.image.url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def suggest_tags(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            if len(content) < 10:
                return JsonResponse({'tags': []})

            noun_extractor = NewsNounExtractor()
            nouns = noun_extractor.train_extract([content]) 
            suggested_tags = sorted(nouns.keys(), key=lambda x: nouns[x].frequency, reverse=True)
            final_tags = [word for word in suggested_tags if len(word) > 1][:7]

            return JsonResponse({'tags': final_tags})
        except Exception as e:
            return JsonResponse({'tags': []})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


