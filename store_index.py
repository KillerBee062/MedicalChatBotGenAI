# store_index.py

from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec

# Corrected the typo in the function name ("download")
from src.helper import load_pdf, split_text, download_huggingface_embeddings
from langchain_pinecone import PineconeVectorStore

def main():
    """
    Main function to load data, create embeddings, and store them in Pinecone.
    """
    load_dotenv()

    # --- Configuration ---
    PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
    index_name = "medchatbot"

    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is not set in the environment or .env file.")

    # --- 1. Load and Process Data ---
    print("Loading PDF documents...")
    # Make sure the 'data/' folder exists and contains your PDFs
    extracted_data = load_pdf(data_path='data/')
    print(f"Loaded {len(extracted_data)} documents.")

    print("Splitting documents into smaller chunks...")
    text_chunks = split_text(extracted_data)
    print(f"Split into {len(text_chunks)} text chunks.")

    # --- 2. Create Embeddings ---
    print("Downloading and initializing HuggingFace embeddings model...")
    embeddings = download_huggingface_embeddings()
    print("Embeddings model loaded.")

    # --- 3. Initialize Pinecone ---
    print("Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # --- 4. Check for and Create Index if Needed ---
    # This is the simplified and correct way to check if an index exists.
    if index_name not in pc.list_indexes().names():
        print(f"Index '{index_name}' does not exist. Creating it now...")
        pc.create_index(
            name=index_name,
            dimension=384,      # Dimension of the 'all-MiniLM-L6-v2' model
            metric="cosine",    # Metric for similarity search
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists. Skipping creation.")

    # --- 5. Upsert Data to Pinecone ---
    print("Upserting document chunks into Pinecone. This may take a while...")
    # This command creates the LangChain VectorStore object and upserts the data.
    docsearch = PineconeVectorStore.from_documents(
        documents=text_chunks,
        index_name=index_name,
        embedding=embeddings
    )
    print("Data has been successfully stored in the Pinecone index.")


if __name__ == '__main__':
    # This block ensures the code only runs when you execute `python store_index.py`
    # and not when it's imported by another file.
    main()