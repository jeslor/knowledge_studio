from django.urls import path
from . import views

urlpatterns = [
    path('api/rag/', views.rag_pipeline_api, name='rag_pipeline_api'),
    path('api/embed/', views.embed_document_api, name='kb_embed_api'),
]