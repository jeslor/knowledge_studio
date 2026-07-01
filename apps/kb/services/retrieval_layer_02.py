from django.core.checks import database
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore  # 📍 Swap Chroma for Qdrant bridge
from qdrant_client import QdrantClient
import config as config

class Retriever:
    def __init__(self):
        self.chipset = config.get_optimal_chipset()
        # load the model to be used to embedd the query
        print("Loading embedding model...🟢")
        self.embedding = HuggingFaceEmbeddings(
            model_name=config.MODEL_NAME, model_kwargs={"device": self.chipset}
        )

        # initialize and connect to Qdrant vector database
        print("Connecting to Qdrant Vector DB Collection...🟢")
        client = QdrantClient(
            url=config.QDRANT_ENDPOINT,
            api_key=config.QDRANT_API_KEY
        )

        if not client.collection_exists(config.COLLECTION_NAME):
            print("Creating collection...")


        self.vector_db = QdrantVectorStore(
            client=client,
            collection_name=config.COLLECTION_NAME,
            embedding=self.embedding,
            vector_name="safer"
        )
        print("Qdrant collection successfully re-initialized with 1024 dimensions! 🚀")


    # search the knowledge base to find details about someone
    def search_knowledge_base(self, query, num_of_candidates=10):
        print(f"🔍 Executing Qdrant vector lookup for query: '{query}'")
        found_results = self.vector_db.similarity_search(query, k=num_of_candidates)
        print(found_results)
        return found_results




# Single shared instance exported for your views/services layer
retriever_service = Retriever()

if __name__ == "__main__":
    user_query = "ebola | intent:general"
    retriever = Retriever()
    documents = retriever.search_knowledge_base(user_query)
    print(f"Successfully retrieved {len(documents)} context document(s):")
    for doc in documents:
        print(f"- From: {doc.metadata.get('file_name', 'Unknown Source')} (Page {doc.metadata.get('page', '?')})")