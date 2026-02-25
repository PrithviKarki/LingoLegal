# LingoLegal

## Project Description
LingoLegal is an AI-powered, RAG-based document navigator tailored specifically for international students studying in the United States. Essential administrative documents—such as credit card terms and conditions, health insurance policies, and banking agreements—are often filled with dense, technical jargon. This fragmented information makes it difficult for individuals unfamiliar with the American financial and legal systems to understand their rights and obligations. 

LingoLegal bridges this gap by allowing users to upload complex PDFs and query them via a chat interface. It utilizes Retrieval-Augmented Generation (RAG) to ensure answers are strictly grounded in the uploaded text. To build trust and prevent AI hallucinations, the system incorporates an Explainable AI (XAI) feature that highlights the exact source clause in the original PDF used to formulate the AI's response.

## Technologies Used
* **Frontend:** React, HTML/CSS, PDF.js (for rendering and highlighting)
* **Backend:** Python, Flask
* **AI & Machine Learning:** LangChain / LlamaIndex (RAG Orchestration), PyMuPDF / fitz (Coordinate-Aware PDF Parsing), Hugging Face Embeddings, Google Gemini / OpenAI APIs
* **Database:** PostgreSQL (User & Metadata), Pinecone / ChromaDB (Vector Search)

## Setup Instructions
To set up the development environment on your local machine, follow these steps:

1. **Clone the repository:**
   git clone [https://github.com/Prithvi](https://github.com/Prithvi) Karki/LingoLegal.git
   cd LingoLegal

2. **Create a virtual environment:**
    python -m venv venv

3. **Activate the virtual environment:**
    * On macOS/Linux:
    source venv/bin/activate

4. **Install the dependencies:**
    pip install pymupdf python-dotenv langchain flask

5. **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your necessary API keys (ensure this file is listed in your `.gitignore` to prevent secret leaks).
    OPENAI_API_KEY=your_api_key_here


## How to Run the Project

*Note: The project is currently in the early implementation phase. The core data ingestion and coordinate-aware parsing pipeline is active.*

1. Ensure your virtual environment is activated.
2. Place a sample PDF document (e.g., a credit card agreement) into the `data/raw/` directory and name it `sample_agreement.pdf`.
3. Run the PDF parsing script to extract text and bounding box coordinates: python src/parser.py
4. The terminal will output the number of extracted text spans and a sample dictionary object containing the page number, extracted text, and its `(x0, y0, x1, y1)` layout coordinates.
