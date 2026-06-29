from langchain_huggingface import HuggingFaceEmbeddings
import config as config
from langchain_chroma import Chroma


class Retriever:
    def __init__(self):
        self.chipset = config.get_optimal_chipset()

        print("Loading embedding model...🟢")
        self.embedding = HuggingFaceEmbeddings(
            model_name=config.MODEL_NAME, model_kwargs={"device": self.chipset}
        )

        print("Loading vector DB...🟢")
        self.vector_db = Chroma(
            persist_directory=config.DB_DIR, embedding_function=self.embedding
        )

    def search_knowledge_base(self, query, num_of_candidates=10):

        return self.vector_db.similarity_search(query, num_of_candidates)


retriever_service = Retriever()

if __name__ == "__main__":
    user_query = "ebola | intent:general"
    retriever = Retriever()
    documents = retriever.search_knowledge_base(user_query)
    print(documents)
