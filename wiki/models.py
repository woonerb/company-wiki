from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils.html import strip_tags  # 이 줄을 반드시 추가해야 합니다!

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField() 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    attachment = models.FileField(upload_to='wiki/files/%Y/%m/%d/', blank=True, null=True) #이미지 업로드 기능 구현

    CATEGORY_CHOICES = [
        ('manual', '업무 매뉴얼'),
        ('history', '과거 업무 처리'),
        ('notice', '공지사항'),
        ('weekly', '주간업무'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='manual')

    # 해시태그 ---------------------------------------------------------
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    def get_tags_list(self):
        """저장된 태그 문자열을 리스트로 변환 (예: '사과,포도' -> ['사과', '포도'])"""
        if self.tags:
            # 쉼표나 공백으로 구분된 경우를 처리
            return [tag.strip() for tag in self.tags.replace(',', ' ').split()]
        return []
    # 해시태그 ---------------------------------------------------------


    # 좋아요 필드
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.title
    
    def total_likes(self):
            return self.likes.count()
    
    def get_clean_excerpt(self):
            """HTML 태그 제거 및 &nbsp; 특수문자 처리 후 100자 요약"""
            if not self.content:
                return ""
            # 1. 모든 HTML 태그 제거
            text = strip_tags(self.content)
            # 2. &nbsp;를 일반 공백으로 치환하고 앞뒤 공백 제거
            text = text.replace('&nbsp;', ' ').strip()
            # 3. 100자까지 자르고 넘치면 ... 붙이기
            if len(text) > 100:
                return text[:100] + "..."
            return text


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='wiki/post_images/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # 오래된 댓글이 위로 (대화 흐름 순)

    def __str__(self):
        return f'{self.author}님의 댓글'