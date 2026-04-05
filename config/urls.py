from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # 로그인/로그아웃용 임포트

urlpatterns = [
    # 1. 관리자 페이지
    path('admin/', admin.site.urls),
    
    # 2. 위키 앱 기능 연동 (wiki/urls.py 불러오기)
    path('', include('wiki.urls')),
    
    # 3. 로그인 및 로그아웃 (기본 장고 인증 뷰 사용)
    path('login/', auth_views.LoginView.as_view(template_name='wiki/login.html'), name='login'), # 로그인 후 게시판 페이지로 이동
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'), # 로그아웃 후 'login' 페이지로 이동

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # 이미지 파일 경로 설정