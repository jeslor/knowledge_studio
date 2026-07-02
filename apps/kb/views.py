from django.http import JsonResponse
from .services import EmbeddData
import json
import asyncio
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from asgiref.sync import async_to_sync

# Your internal logic imports
from .services import (
    processor_service,
    retriever_service,
    rerank_service,
    build_context,
    local_model
)


def stream_rag_pipeline(user_query, conversation_history):
    """Generator that runs the pipeline and yields state updates to frontend"""
    user_questions = [conv['user_message'] for conv in conversation_history]
    sanitized_question = local_model.generate_query(user_query, prev_user_queries=user_questions)
    print(sanitized_question)
    try:
        # Step 1: Process
        yield f"data: {json.dumps({'step': 'process', 'msg': 'Analyzing and processing query...'})}\n\n"
        processed = processor_service.process_query(sanitized_question)

        # Step 2: Retrieve
        yield f"data: {json.dumps({'step': 'retrieve', 'msg': 'Searching knowledge base...'})}\n\n"
        docs = retriever_service().search_knowledge_base(processed)

        # Step 3: Rerank
        yield f"data: {json.dumps({'step': 'rerank', 'msg': 'Evaluating document relevance...'})}\n\n"
        ranked = rerank_service.rerank(sanitized_question, docs)


        # Step 4: Context
        yield f"data: {json.dumps({'step': 'context', 'msg': 'Building optimized context payload...'})}\n\n"
        context, citations = build_context(ranked, 3100)


        # Step 5: Generate
        yield f"data: {json.dumps({'step': 'generate', 'msg': 'Synthesizing final response...'})}\n\n"

        # 📍 Direct Fix: Call it normally since it returns an AIMessage immediately!
        result = local_model.prompt_model(user_query, context, conversation_history)

        # Final Payload
        yield f"data: {json.dumps({
            'step': 'complete',
            'answer': result.content,
            'sources': citations
        })}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'step': 'error', 'msg': str(e)})}\n\n"


@csrf_protect
def rag_pipeline_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_query = data.get('query')
            conversation = data.get('conversation')

            if not user_query:
                return JsonResponse({'success': False, 'error': 'No query provided'}, status=400)

            response = StreamingHttpResponse(
                stream_rag_pipeline(user_query, conversation),
                content_type="text/event-stream"
            )
            # Prevent proxy buffering so events stream instantly
            response['X-Accel-Buffering'] = 'no'
            return response

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)


async def embed_document_api(request):
    """API endpoint that JS calls to run the embed step-by-step"""
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('documents')
        if len(uploaded_files) > 10:
            return JsonResponse({'success': False, 'error': 'Maximum limit of 5 files exceeded.'}, status=400)

        vectordb = EmbeddData(chunk_size=750, chunk_overlap=150)
        vectordb.build_knowledge_index(uploaded_files)

        return JsonResponse({'success': True}, status=200)
