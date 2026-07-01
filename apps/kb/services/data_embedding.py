from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse
from qdrant_client import QdrantClient

# Import both ingestion entrypoints
from .ingest_pdf import process_single_pdf, ingest_pdf_directory
import config

class EmbeddData:
    def __init__(
        self,
        chunk_size=config.DEFAULT_CHUNK_SIZE,
        chunk_overlap=config.DEFAULT_CHUNK_OVERLAP,
        DATA_DIR=config.DATA_DIR,
        MODEL_NAME=config.MODEL_NAME,
        QDRANT_API_KEY=config.QDRANT_API_KEY,
        QDRANT_ENDPOINT=config.QDRANT_ENDPOINT,
        CHIPSET=config.get_optimal_chipset(),
        COLLECTION_NAME=config.COLLECTION_NAME,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.DATA_DIR = DATA_DIR
        self.MODEL_NAME = MODEL_NAME
        self.QDRANT_API_KEY = QDRANT_API_KEY
        self.QDRANT_ENDPOINT = QDRANT_ENDPOINT
        self.CHIPSET = CHIPSET
        self.COLLECTION_NAME = COLLECTION_NAME
        self.db = None
        self.client = QdrantClient(
            url=config.QDRANT_ENDPOINT,
            api_key=config.QDRANT_API_KEY,
        )


    def build_knowledge_index(self, django_files=None):
        docs = []

        # 📍 Check if handling live frontend uploads
        if django_files:
            print(f"1. Processing {len(django_files)} web-uploaded files via common parser")
            for uploaded_file in django_files:
                file_name = uploaded_file.name

                if file_name.lower().endswith('.pdf'):
                    # 📍 Pass the Django uploaded file pointer directly into the identical logic block!
                    file_docs = process_single_pdf(uploaded_file, file_name)
                    docs.extend(file_docs)

                elif file_name.lower().endswith(('.txt', '.md')):
                    text = uploaded_file.read().decode('utf-8', errors='ignore')
                    if text.strip():
                        from .ingest_pdf import Document
                        docs.append(Document(page_content=text, metadata={"source": file_name, "file_name": file_name}))
        else:
            print("1. Scanning local storage path directories...")
            docs = ingest_pdf_directory(self.DATA_DIR)

        if not docs:
            raise ValueError("Zero documents were extracted from the upload stream.")


        # 2. Text Splitting
        print("2. Chunking extracted text elements...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_documents(docs)

        # 3. Model Load for embedding
        print("3. Compiling embedding vectors on native chipset...")
        embedding = HuggingFaceEmbeddings(
            model_name=self.MODEL_NAME, model_kwargs={"device": self.CHIPSET}
        )

        sparse_embedding = FastEmbedSparse(
            model_name="Qdrant/bm25"
        )

        # 4. Save directly into Qdrant Cloud Cluster
        print(f"4. Pushing vectors to Qdrant cluster under: '{self.COLLECTION_NAME}'")
        self.db = QdrantVectorStore(
            client=self.client,
            embedding=embedding,
            collection_name=self.COLLECTION_NAME,
            sparse_embedding=sparse_embedding,
            vector_name="safer"
        )

        self.db.add_documents(chunks)
        print("Success! Qdrant DB vector records synchronized.")
        return len(chunks)

