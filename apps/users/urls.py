from django.urls import path

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/<int:pk>', views.profile, name='profile'),

]