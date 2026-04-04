from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    # ProseMirror는 구조화된 JSON이나 HTML을 뱉어냅니다. 
    # 여기서는 HTML 형태로 저장한다고 가정합니다.
    content = models.TextField() 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    ######이미지 업로드 기능 구현###############################################################
    # 이미지 업로드는 Tiptap 에디터 내부에 삽입하는 방식이 더 직관적이지만, 
    # 우선 별도 첨부 기능을 추가합니다.
    attachment = models.FileField(upload_to='wiki/files/%Y/%m/%d/', blank=True, null=True)
    #########################################################################################

    CATEGORY_CHOICES = [
        ('manual', '업무 매뉴얼'),
        ('history', '과거 업무 처리'),
        ('notice', '공지사항'),
        ('weekly', '주간업무'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='manual')
    tags = models.CharField(max_length=255, blank=True) # 해시태그 저장용 (예: #복합기 #수리)


    def __str__(self):
        return self.title
    

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='wiki/post_images/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
