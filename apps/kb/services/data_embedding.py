from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_chroma import Chroma
from ingest_pdf import ingest_pdf_directory
import config


class EmbeddData:

    def __init__(
        self,
        chunk_size=config.DEFAULT_CHUNK_SIZE,
        chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
        DATA_DIR=config.DATA_DIR,
        DB_DIR=config.DB_DIR,
        MODEL_NAME=config.MODEL_NAME,
        QDRANT_API_KEY=config.QDRANT_API_KEY,
        QDRANT_ENDPOINT=config.QDRANT_ENDPOINT,
        CHIPSET=config.get_optimal_chipset(),
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.DATA_DIR = DATA_DIR
        self.DB_DIR = DB_DIR
        self.MODEL_NAME = MODEL_NAME
        self.QDRANT_API_KEY = QDRANT_API_KEY
        self.QDRANT_ENDPOINT = QDRANT_ENDPOINT
        self.CHIPSET = CHIPSET
        self.db = None
        self.qdrant_client = QdrantClient(
            url=self.QDRANT_ENDPOINT,
            api_key=self.QDRANT_API_KEY
        )

    def build_knowledge_index(self):
        print("1. extracting raw text from PDFs")
        docs = ingest_pdf_directory(self.DATA_DIR)
        # print(docs)

        print("2. chunking text for optimal embeddings resolutions")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_documents(docs)
        # print(chunks)

        print("3. Initialising local embedding transformers ...")
        embedding = HuggingFaceEmbeddings(
            model_name=self.MODEL_NAME, model_kwargs={"device": self.CHIPSET}
        )
        # print(embedding)

        print("4. constructing and persisting vector Database ... ")
        self.db = Chroma.from_documents(
            documents=chunks, embedding=embedding, persist_directory=self.DB_DIR
        )
        print("Success! Database secured on local storage")

    def test_vector_embedding(self):
        # test whether the db is working well
        print("5. persisting vector Database ... ")
        results = self.db.similarity_search("What is the documents?", k=5)

        for result in results:
            print(result)
            print("\n")


if __name__ == "__main__":
    vectordb = EmbeddData(chunk_size=750, chunk_overlap=150)
    vectordb.build_knowledge_index()
    vectordb.test_vector_embedding()
