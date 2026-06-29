from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
path('api/rag/', views.rag_pipeline_api, name='rag_pipeline_api'),
]