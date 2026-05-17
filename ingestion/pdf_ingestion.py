import os
import tempfile
from typing import Any, Dict, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import embeddings

# In-memory registries keyed by thread_id
_THREAD_RETRIEVERS: Dict[str, Any] = {}
_THREAD_METADATA: Dict[str, dict] = {}


def _get_retriever(thread_id: Optional[str]):
    """Return the FAISS retriever for a thread, or None if not yet indexed."""
    if thread_id and thread_id in _THREAD_RETRIEVERS:
        return _THREAD_RETRIEVERS[thread_id]
    return None


def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """
    Parse a PDF from raw bytes, build a FAISS vector store, and register
    the retriever under *thread_id*.

    Returns a summary dict: {filename, documents, chunks}.
    """
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        temp_path = tmp.name

    try:
        loader = PyPDFLoader(temp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = splitter.split_documents(docs)

        vector_store = FAISS.from_documents(chunks, embeddings)
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}
        )

        _THREAD_RETRIEVERS[str(thread_id)] = retriever
        _THREAD_METADATA[str(thread_id)] = {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }

        return {
            "filename": filename or os.path.basename(temp_path),
            "documents": len(docs),
            "chunks": len(chunks),
        }
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass


def thread_has_document(thread_id: str) -> bool:
    """Return True if a PDF has been indexed for this thread."""
    return str(thread_id) in _THREAD_RETRIEVERS


def thread_document_metadata(thread_id: str) -> dict:
    """Return ingestion metadata for the thread's PDF, or an empty dict."""
    return _THREAD_METADATA.get(str(thread_id), {})
