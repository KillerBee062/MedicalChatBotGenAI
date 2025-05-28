from flask import Flask, request, jsonify, render_template
# Assuming 'download_huggingface_embeddings' and 'system_prompt' are correctly defined in your src files
from src.helper import download_huggingface_embeddings
from src.prompt import system_prompt
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI # CHANGED: Using the Chat model for better chat prompt compatibility
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# --- Initialization ---
app = Flask(__name__) # FIXED: Typo from Flast to Flask
load_dotenv()

# --- API Key Configuration ---
# This method is fine. LangChain libraries will automatically pick up the environment variables.
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") # RENAMED for consistency with official docs

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY # RENAMED for consistency

# --- LangChain Components Setup ---

# 1. Load Embeddings
# Make sure this function returns a valid LangChain embedding object (e.g., HuggingFaceEmbeddings)
print("Loading Embeddings...")
embeddings = download_huggingface_embeddings()
print("Embeddings Loaded.")

# 2. Initialize Pinecone Vector Store
index_name = "medchatbot"
print(f"Connecting to Pinecone index: {index_name}...")
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)
print("Pinecone connection successful.")

# 3. Create Retriever
retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# 4. Initialize LLM
# CHANGED: Using ChatGoogleGenerativeAI for better compatibility with chat prompts
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0.2,
    # The API key is automatically picked up from the environment variable GOOGLE_API_KEY
)

# 5. Define the Prompt Template
# IMPORTANT: Your `system_prompt` from src/prompt.py MUST contain "{context}" for the RAG chain to work.
# Example of a good system_prompt string:
# """You are a medical expert. Use the following pieces of retrieved context to answer the question.
# If you don't know the answer, just say that you don't know. Keep the answer concise.
# Context: {context}"""
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])


# 6. Create Chains
# This chain takes the user's question and the retrieved documents and generates an answer.
Youtube_chain = create_stuff_documents_chain(llm, prompt)

# This is the main chain that orchestrates the retrieval and answer generation.
rag_chain = create_retrieval_chain(retriever, Youtube_chain)


# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main chat page."""
    return render_template('chatbot.html')


# FIXED: Route name and request/response handling
@app.route('/chat', methods=['POST'])
def chat():
    """Handles the chat interaction."""
    try:
        # FIXED: Changed from request.form to request.json to match the frontend
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        print(f"User Input: {user_input}")

        # FIXED: The input key for invoke must match the key in the prompt ('input')
        response = rag_chain.invoke({"input": user_input})
        answer = response.get('answer', "Sorry, I couldn't process that.")

        print(f"Response: {answer}")

        # FIXED: Return a proper JSON response
        return jsonify({'answer': answer})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred. Please try again later."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)