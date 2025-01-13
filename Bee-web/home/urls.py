from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Add your URL patterns here
    # Example: path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),  
    path('logout/', views.logout, name='logout'),
    path('identify/', views.identify, name='identify'),
    path('tracker/', views.tracker, name='tracker'),
    path('history/', views.history, name='history'),
    path('research/', views.research, name='research'),
    path('result/<int:pk>', views.result, name='result'),
    path('stream_video/<str:folder>/<str:name>', views.stream_video, name='stream_video'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)