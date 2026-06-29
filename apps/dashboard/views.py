from django.shortcuts import render
from django.http import JsonResponse
import json

# Your internal logic imports
from apps.kb.services import (
    processor_service,
    retriever_service,
    rerank_service,
    build_context,
    local_model
)


def home(request):
    """Renders the HTML workspace page"""
    return render(request, 'dashboard/home.html')


async def rag_pipeline_api(request):
    """API endpoint that JS calls to run the pipeline step-by-step"""
    if request.method == 'POST':
        data = json.loads(request.body)
        user_query = data.get('query')
        step = data.get('step')  # 'process', 'retrieve', 'rerank', 'context', 'generate'

        try:
            if step == 'process':
                processed = processor_service.process_query(user_query)
                return JsonResponse({'success': True, 'data': processed})

            elif step == 'retrieve':
                processed_query = data.get('processed_query')
                docs = retriever_service.search_knowledge_base(processed_query)
                # Ensure docs are JSON serializable
                return JsonResponse({'success': True, 'data': docs})

            elif step == 'rerank':
                retrieved_docs = data.get('retrieved_docs')
                ranked = rerank_service.rerank(user_query, retrieved_docs)
                return JsonResponse({'success': True, 'data': ranked})

            elif step == 'context':
                ranked_docs = data.get('ranked_docs')
                context, token_count = build_context(ranked_docs, 3100)
                return JsonResponse({'success': True, 'context': context})

            elif step == 'generate':
                context = data.get('context')
                result = await local_model.prompt_model(user_query, context)
                return JsonResponse({'success': True, 'answer': result.content})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)