# src/helper.py

# UPDATED: Imports from langchain_community, the new standard for LangChain integrations.
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


def load_pdf(data_path):
    """
    Loads all PDF files from a specified directory.

    Args:
        data_path (str): The path to the folder containing PDF files.

    Returns:
        list: A list of loaded document objects.
    """
    loader = DirectoryLoader(
        data_path,
        glob="*.pdf",  # Looks for any file ending with .pdf
        loader_cls=PyPDFLoader,
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()
    return documents


def split_text(documents):
    """
    Splits the loaded documents into smaller chunks.

    Args:
        documents (list): A list of document objects.

    Returns:
        list: A list of smaller text chunk documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50  # Increased overlap slightly for better context continuity
    )
    texts = text_splitter.split_documents(documents)
    return texts


# FIXED: Corrected the typo in the function name ("download")
def download_huggingface_embeddings():
    """
    Downloads and initializes the HuggingFace sentence-transformer embeddings.

    Returns:
        HuggingFaceEmbeddings: An embedding model object.
    """
    # Using the standard HuggingFaceEmbeddings class for this model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}  # Specify CPU for consistent performance
    )
    return embeddings