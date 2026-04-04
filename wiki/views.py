from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Post
from django.contrib.auth.decorators import login_required

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