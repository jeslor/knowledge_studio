from sentence_transformers import CrossEncoder

# Initializes ONCE when imported
reranker_model = CrossEncoder("BAAI/bge-reranker-large")


class Reranker:
    def __init__(self, top_k: int = 3, model: CrossEncoder = reranker_model):
        self.model = model

        self.top_k = top_k

    def rerank(self, query: str, documents: list) -> list:
        if not documents:
            return []

        doc_texts = [doc.page_content for doc in documents]

        # Simple, straightforward synchronous execution
        rank_results = self.model.rank(
            query=query, documents=doc_texts, top_k=self.top_k
        )

        reranked_documents = []
        for hit in rank_results:
            original_index = hit["corpus_id"]
            document = documents[original_index]
            document.metadata["rerank_score"] = float(hit["score"])
            reranked_documents.append(document)

        return reranked_documents


rerank_service = Reranker()
