from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    # ProseMirror는 구조화된 JSON이나 HTML을 뱉어냅니다. 
    # 여기서는 HTML 형태로 저장한다고 가정합니다.
    content = models.TextField() 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title