from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Comment
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import PostImage
import re # 정규표현식 사용
from soynlp.noun import NewsNounExtractor # 해쉬태그 추출기
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse

@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content') # 에디터의 HTML 데이터
        
        if title and content:
            # DB에 저장
            post = Post.objects.create(
                title=title, 
                content=content, 
                author=request.user
            )
            return redirect('post_detail', pk=post.pk) # 저장 후 상세 페이지로 이동
            
    return render(request, 'wiki/editor.html')

def post_detail(request, pk):
    post = Post.objects.get(pk=pk)
    return render(request, 'wiki/detail.html', {'post': post})

###검색 기능 구현##################################################################
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    
    # 검색 로직
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        ).distinct()
        
    return render(request, 'wiki/list.html', {'posts': posts, 'query': query})
#################################################################################


@csrf_exempt # 에디터의 비동기 업로드를 위해 임시 허용
def image_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        img_file = request.FILES['image']
        img_instance = PostImage.objects.create(image=img_file)
        # 저장된 이미지의 절대 경로를 리턴
        return JsonResponse({'url': img_instance.image.url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt # 테스트를 위해 잠시 CSRF 체크를 끕니다
@login_required  # 로그인이 안 되어 있으면 로그인 페이지로 보냅니다.
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category')
        tags = request.POST.get('tags') # 하단 태그 입력창에서 온 데이터
        attachment = request.FILES.get('attachment')

        post = Post.objects.create(
            title=title,
            content=content,
            category=category,
            tags=tags,
            attachment=attachment,
            author=request.user
        )
        return redirect('post_detail', pk=post.pk)

    return render(request, 'wiki/editor.html')

# --- 게시글 본문의 키워드를 기반으로 해시태그 단어 추천 ---
@csrf_exempt # 테스트를 위해 잠시 CSRF 체크를 끕니다
def suggest_tags(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()

            if len(content) < 10:
                return JsonResponse({'tags': []})

            # 명사 추출기 초기화
            noun_extractor = NewsNounExtractor()
            
            # 본문에서 명사 추출 및 빈도수 분석
            nouns = noun_extractor.train_extract([content]) 
            
            # nouns 결과에서 명사만 뽑아 빈도수 순으로 정렬
            # NewsNounExtractor의 결과는 {단어: NounScore} 형태입니다.
            suggested_tags = sorted(nouns.keys(), key=lambda x: nouns[x].frequency, reverse=True)
            
            # 한 글자 제외 및 상위 7개 선택
            final_tags = [word for word in suggested_tags if len(word) > 1][:7]

            return JsonResponse({'tags': final_tags})
        except Exception as e:
            print(f"Extraction Error: {e}") # 에러 확인용
            return JsonResponse({'tags': []})

# --- 게시글 본문의 키워드를 기반으로 해시태그 단어 추천 ---        


# --- 검색 기능 구현 ---        
def post_list(request):
    search_query = request.GET.get('q', '')  # URL에서 'q' 파라미터를 가져옴
    posts = Post.objects.all().order_by('-created_at')

    if search_query:
        # 제목(title) 또는 본문(content) 또는 태그(tags)에 검색어가 포함된 경우 필터링
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        ).distinct()

    return render(request, 'wiki/post_list.html', {
        'posts': posts,
        'search_query': search_query
    })
# --- 검색 기능 구현 ---        


# --- 좋아요 기능 구현 ---        
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user) # 이미 눌렀다면 취소
    else:
        post.likes.add(request.user) # 안 눌렀다면 추가
    
    return HttpResponseRedirect(reverse('post_detail', args=[str(pk)]))
# --- 좋아요 기능 구현 ---        


# --- 글 수정 기능 구현 ---        
@login_required  # 1. 로그인한 사용자만 접근 가능
def post_edit(request, pk):
    # 수정할 글 객체 가져오기
    post = get_object_or_404(Post, pk=pk)
    
    # 2. 작성자 본인이 아니면 403 Forbidden 에러 반환
    if post.author != request.user:
        return HttpResponseForbidden("본인의 글만 수정할 수 있습니다.")

    if request.method == "POST":
        # 3. 실제 DB 저장 로직 (POST 방식일 때만 수행)
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.category = request.POST.get('category') # 카테고리도 있다면 추가
        post.save()
        return redirect('post_detail', pk=post.pk)

    # GET 방식일 때는 기존 내용이 채워진 수정 페이지를 보여줌
    return render(request, 'wiki/post_form.html', {'post': post})
# --- 글 수정 기능 구현 ---    



# --- 글 삭제 기능 구현 ---    
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("본인의 글만 삭제할 수 있습니다.")
    
    if request.method == "POST":
        post.delete()
        return redirect('post_list')
    return redirect('post_detail', pk=pk)
# --- 글 삭제 기능 구현 ---    


# --- 댓글 기능 구현 ---        
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == "POST": # 댓글 제출 시
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
            return redirect('post_detail', pk=post.pk)

    return render(request, 'wiki/post_detail.html', {'post': post})
# --- 댓글 기능 구현 ---   

# --- 댓글 수정 기능 구현 ---   
@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return HttpResponseForbidden("본인의 댓글만 수정할 수 있습니다.")

    if request.method == "POST":
        comment.content = request.POST.get('content')
        comment.save()
        return redirect('post_detail', pk=comment.post.pk)
    
    # 댓글 수정은 별도 페이지보다 상세페이지에서 처리하는 경우가 많지만, 
    # 로직 분리를 위해 수정 폼으로 보내거나 템플릿에서 분기 처리합니다.
    return render(request, 'wiki/comment_form.html', {'comment': comment})
# --- 댓글 수정 기능 구현 ---  



# --- 댓글 삭제 기능 구현 ---  
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.author != request.user:
        return HttpResponseForbidden("본인의 댓글만 삭제할 수 있습니다.")
    
    if request.method == "POST":
        comment.delete()
    return redirect('post_detail', pk=post_pk)
# --- 댓글 삭제 기능 구현 ---  
