from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name = 'settings'), #user settings
    path('upload', views.upload, name = 'upload'), #users can upload posts
    path('follow', views.follow, name = 'follow'), #users can follow other users
    path('search', views.search, name = 'search'), #users can search
    path('profile/<str:pk>', views.profile, name = 'profile'), #user profiles
    path('like-post', views.like_post, name = 'like-post'),
    path('signup', views.signup, name='signup'), #so users can sign up
    path('signin', views.signin, name='signin'), #so users can sign in
    path('logout', views.logout, name='logout') #so users can log out
]