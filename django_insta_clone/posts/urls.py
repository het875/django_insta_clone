from django.urls import path
from .views import *
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('posts/', create_post, name='create_post'),  # Create a new post
    path('posts/<int:post_id>/', views.get_post, name='get_post'),  # Get a post with comments
    path('posts/<int:post_id>/comments/', views.create_comment, name='create_comment'),  # Create a comment on a post
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

