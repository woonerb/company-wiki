from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.html import strip_tags

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Node(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.PositiveIntegerField(default=0)
    
    # 권한 종류별 유저 매핑 (ManyToMany 방식 유지)
    viewers = models.ManyToManyField(User, related_name='viewable_nodes', blank=True)
    editors = models.ManyToManyField(User, related_name='editable_nodes', blank=True)
    managers = models.ManyToManyField(User, related_name='manageable_nodes', blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    def has_perm(self, user, perm_type='read'):
        """재귀적으로 부모 노드를 탐색하며 사용자의 권한을 확인합니다."""
        if user.is_superuser:
            return True
        
        # 1. 현재 노드에 직접 부여된 권한 확인
        if perm_type == 'read':
            if self.viewers.filter(id=user.id).exists() or \
               self.editors.filter(id=user.id).exists() or \
               self.managers.filter(id=user.id).exists():
                return True
        elif perm_type == 'edit':
            if self.editors.filter(id=user.id).exists() or \
               self.managers.filter(id=user.id).exists():
                return True
        elif perm_type == 'all':
            if self.managers.filter(id=user.id).exists():
                return True

        # 2. 부모 노드가 있다면 부모의 권한을 상속받아 확인
        if self.parent:
            return self.parent.has_perm(user, perm_type)
            
        return False
    
    def save(self, *args, **kwargs):
            # 1. 저장 전 수행하고 싶은 로직 (예: 부모가 자기 자신인지 검증)
            if self.parent and self.parent.id == self.id:
                self.parent = None
                
            # 2. [필수] 실제 DB에 저장하는 명령 (이게 빠지면 저장이 안 됩니다!)
            super().save(*args, **kwargs)
            
            # 3. 저장 후 수행하고 싶은 로직 (필요할 때만 작성)
            # 예: 캐시 비우기 등    

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='wiki/files/%Y/%m/%d/', blank=True, null=True)    
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def get_clean_excerpt(self):
        if not self.content: return ""
        text = strip_tags(self.content)
        text = text.replace('&nbsp;', ' ').strip()
        return (text[:100] + "...") if len(text) > 100 else text

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='wiki/post_images/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

# 만약 별도의 권한 테이블이 필요하다면 유지 (ManyToMany와 병행 가능)
class NodePermission(models.Model):
    PERMISSION_CHOICES = [
        ('read', '읽기'),
        ('edit', '수정/관리'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES)

    class Meta:
        unique_together = ('user', 'node')