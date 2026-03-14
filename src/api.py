import os
from flask import Flask, request, jsonify
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

# Load API keys from your .env file
load_dotenv()

app = Flask(__name__)

# 1. Connect to the local Vector Database
chroma_client = chromadb.PersistentClient(path="./data/index")
collection = chroma_client.get_collection(name="lingolegal_docs")

# 2. Load the Embedding Model
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. Initialize the Google Gemini Client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

@app.route('/ask', methods=['POST'])
def ask_document():
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Step A: Convert the user's question into a vector
        query_embedding = embedding_model.encode([query]).tolist()

        # Step B: Search ChromaDB for the 1 most relevant paragraph
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=1 
        )

        source_text = results['documents'][0][0]
        source_metadata = results['metadatas'][0][0]

        # Step C: Send the retrieved text and the user's question to Gemini
        prompt = f"""
        You are a helpful legal assistant for international students. 
        Read the following document excerpt and answer the user's question. 
        If the answer is not in the excerpt, say "I cannot find the answer in the provided document."
        
        Excerpt: "{source_text}"
        
        Question: "{query}"
        """

        response = gemini_model.generate_content(prompt)
        ai_answer = response.text

        # Step D: Return the AI answer AND the XAI coordinates to the frontend
        return jsonify({
            "status": "success",
            "answer": ai_answer,
            "source_text": source_text,
            "metadata": source_metadata
        })

    except Exception as e:
        return jsonify({
            "status": "partial_success_llm_failed",
            "error": str(e),
            "retrieved_source_text": source_text if 'source_text' in locals() else None,
            "metadata": source_metadata if 'source_metadata' in locals() else None
        })

if __name__ == '__main__':
    print("Starting LingoLegal Backend API on port 5000...")
    app.run(debug=True, port=5000)