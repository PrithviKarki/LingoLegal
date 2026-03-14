import chromadb
from sentence_transformers import SentenceTransformer

# 1. Initialize the ChromaDB client to save data locally to a folder
chroma_client = chromadb.PersistentClient(path="./data/index")

# 2. Create or open a collection (like a table in a relational database)
collection = chroma_client.get_or_create_collection(name="lingolegal_docs")

# 3. Load a fast, free, open-source embedding model from Hugging Face
print("Loading embedding model... (This may take a few seconds the first time)")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def index_semantic_chunks(chunks):
    """
    Takes the semantic chunks from the parser, converts the text to vector embeddings,
    and stores them in ChromaDB alongside their spatial metadata.
    """
    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(chunks):
        documents.append(chunk["text"])
        
        # We must convert the bounding box tuple to a string so ChromaDB can store it
        metadatas.append({
            "page": chunk["page"],
            "bbox": str(chunk["bbox"])
        })
        
        # Create a unique ID for each chunk
        ids.append(f"doc1_chunk_{i}")

    print(f"Generating embeddings for {len(documents)} chunks...")
    # Convert the text into numbers (vectors)
    embeddings = embedding_model.encode(documents).tolist()

    print("Saving to ChromaDB...")
    # Add everything to the database
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Indexing complete! Data is securely stored in ./data/index")

if __name__ == "__main__":
    # Import your parser function to test the pipeline end-to-end
    from parser import extract_text_with_coordinates, semantic_chunking
    
    sample_pdf = "data/raw/sample_agreement.pdf"
    
    print("--- Starting Pipeline ---")
    # Step A: Parse
    raw_spans = extract_text_with_coordinates(sample_pdf)
    # Step B: Chunk
    processed_chunks = semantic_chunking(raw_spans, max_chars=500)
    # Step C: Index
    index_semantic_chunks(processed_chunks)