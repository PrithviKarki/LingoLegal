import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename # NEW: Safely handles uploaded file names
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
from parser import extract_text_with_coordinates, semantic_chunking # NEW: Imports your custom logic
# Load API keys from your .env file
load_dotenv()

app = Flask(__name__)
CORS(app) 

# NEW: Configure upload folder
UPLOAD_FOLDER = './data/raw'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Creates the folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 1. Connect to the local Vector Database
chroma_client = chromadb.PersistentClient(path="./data/index")
collection = chroma_client.get_collection(name="lingolegal_docs")

# 2. Load the Embedding Model
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 3. Initialize the Google Gemini Client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 1. Check if a file was actually sent
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        # 2. Securely save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            print(f"Processing new file: {filename}...")
            
            # 3. Run your custom PyMuPDF Parser and Chunker
            raw_spans = extract_text_with_coordinates(filepath)
            processed_chunks = semantic_chunking(raw_spans, max_chars=500)

            # 4. WIPE THE OLD DATABASE (Crucial for dynamic uploads)
            global collection
            try:
                chroma_client.delete_collection(name="lingolegal_docs")
            except Exception:
                pass # Collection might not exist yet, which is fine
            
            # Create a fresh collection for the new document
            collection = chroma_client.create_collection(name="lingolegal_docs")

            # 5. Format data for ChromaDB
            documents = []
            metadatas = []
            ids = []

            for i, chunk in enumerate(processed_chunks):
                documents.append(chunk["text"])
                metadatas.append({
                    "page": chunk["page"],
                    "bbox": str(chunk["bbox"])
                })
                ids.append(f"doc_chunk_{i}")

            print("Generating new embeddings...")
            embeddings = embedding_model.encode(documents).tolist()

            print("Saving to ChromaDB...")
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            return jsonify({"status": "success", "message": f"Successfully processed {filename}"})

        except Exception as e:
            print(f"Error processing file: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file format. Please upload a PDF."}), 400

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