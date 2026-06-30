from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/admin/', views.admin_dashboard_view, name='kb_admin_dashboard'),
]