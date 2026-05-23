import os
from llama_index.core import (
    StorageContext, VectorStoreIndex, load_index_from_storage
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.file import PDFReader
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.getcwd()
PDF_PATH = BASE_DIR + "\\indian_history.pdf"
PERSIST_DIR = BASE_DIR + "\\storage_history_pdf_llamaindex"
CHUNKSIZE = 300
OVERLAP = 0.1

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),
             model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
             temperature=0)
embeddings = OpenAIEmbedding(model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"))
nodeparser = SentenceSplitter(chunk_size=CHUNKSIZE,chunk_overlap=int(CHUNKSIZE*OVERLAP))

# -------------------------------
# Load and enrich PDF documents
# -------------------------------
def load_pdf_documents(pdf_path):
    enriched_docs = []
    try:
        reader = PDFReader()
        docs = reader.load_data(file=pdf_path)
        for i, doc in enumerate(docs, start=1):
            metadata = {
                "source_file": pdf_path,
                "page_number": i,
                "document_type": "Indian_history_notes",
            }
            doc.metadata = metadata
            enriched_docs.append(doc)
    except Exception as e:
        return ["EXCEPTION", f"load_pdf_documents(). {str(e)}"]
    return enriched_docs
#-------------------------------------------------
#Add the node parser to do the Sentence Chunking
# -----------------------------------------------
def create_nodes(documents):
    nodes = nodeparser.get_nodes_from_documents(documents)
    return nodes
# -------------------------------
# Build or load index
# -------------------------------
def build_or_load_index() -> VectorStoreIndex:
    if os.path.exists(PERSIST_DIR):
        storage_context = StorageContext.from_defaults(persist_dir=str(PERSIST_DIR))
        return load_index_from_storage(storage_context)
    else:
        documents = load_pdf_documents(PDF_PATH)
        print(f"Total chunks created: {len(documents)}")
        if isinstance(documents[0], str):  # error case
            raise RuntimeError(f"Error loading PDF: {documents}")
        # Creating the chunk nodes
        nodes = create_nodes(documents)
        # index = VectorStoreIndex.from_documents(documents)
        index = VectorStoreIndex(nodes)  # new code
        index.storage_context.persist(persist_dir=str(PERSIST_DIR))
        return index

# -------------------------------
# Build query engine
# -------------------------------
def build_query_engine(top_k: int = 5, response_mode: str = "refine") -> RetrieverQueryEngine:
    index = build_or_load_index()
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
    response_synthesizer = get_response_synthesizer(response_mode=response_mode)
    return RetrieverQueryEngine(retriever=retriever, response_synthesizer=response_synthesizer)

# -------------------------------
# Retrieval only
# -------------------------------
def retrieve_only(query: str, top_k: int = 5):
    result = pd.DataFrame()
    index = build_or_load_index()
    retriever = VectorIndexRetriever(index=index, similarity_top_k=top_k)
    nodes = retriever.retrieve(query)

    for i, node in enumerate(nodes, start=1):
        row = {
            "rank": i,
            "score": node.score,
            "metadata": node.metadata,
            "response": node.text,
        }
        result = result._append(row, ignore_index=True)
    return result

# -------------------------------
# Classic RAG
# -------------------------------
def classic_rag(query: str, top_k: int = 5, response_mode: str = "refine"):
    query_engine = build_query_engine(top_k=top_k, response_mode=response_mode)
    response = query_engine.query(query)

    answer = str(response)
    sources = []
    for i, src in enumerate(response.source_nodes, start=1):
        sources.append({
            "rank": i,
            "score": src.score,
            "metadata": src.metadata,
            "text": src.text[:300]
        })
    return answer, sources
