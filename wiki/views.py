from django.shortcuts import render, redirect
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