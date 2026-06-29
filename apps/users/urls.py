from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.redirect_to_own_profile, name='redirect_to_own_profile'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile/<int:pk>/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.logout, name='logout'),


]