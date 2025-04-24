from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    path('fetch-posts', views.fetch_posts, name='fetch-posts'),
    path('posts/<int:post_id>', views.single_post_view, name='single-post'),
    path('like/<int:post_id>', views.like, name='like'),
    path('save/<int:post_id>', views.save, name='save'),
    path('comment/<int:post_id>', views.comment, name='comment'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('follow/<str:username>', views.follow, name='follow'),
    path('saved', views.saved, name='saved'),
    path('settings', views.settings, name='settings'),
    path('search', views.search, name='search'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('login', views.login, name='login'),
]