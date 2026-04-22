# LingoLegal

## Project Description
LingoLegal is a Retrieval-Augmented Generation (RAG) web application designed to help international students easily parse, understand, and navigate complex administrative, banking, and visa documents. Built with a Flask/Python backend and a React frontend, the system dynamically parses uploaded PDFs, vectorizes the text using ChromaDB, and uses Google Gemini to answer user queries while drawing Explainable AI (XAI) highlight bounding boxes directly over the source text.

---

## Prerequisites
Before running this project, ensure you have the following installed on your machine:
- Python 3.10 or higher
- Node.js and npm
- A Google Gemini API Key

---

## Installation and Setup Instructions

### 1. Backend Setup (Flask & AI Pipeline)

1. Clone the repository:
```bash
   git clone https://github.com/PrithviKarki/LingoLegal.git
```

2. Navigate into the project folder:
```bash
   cd LingoLegal
```

3. Create a virtual environment:
```bash
   python -m venv venv
```

4. Activate the virtual environment:
   - **Mac/Linux:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

5. Install the required Python dependencies:
```bash
   pip install -r requirements.txt
```

6. Create a `.env` file in the root directory and add your Google API key: GOOGLE_API_KEY=your_gemini_api_key_here

### 2. Frontend Setup (React & PDF.js)

1. Open a second terminal window and navigate to the frontend folder:
```bash
   cd frontend
```

2. Install the React dependencies:
```bash
   npm install
```

---

## How to Run the Application Locally

You must run both the backend and frontend servers **simultaneously** for the application to function.

**Terminal 1 — Backend:**

Ensure your virtual environment `(venv)` is active, then start the Flask API:
```bash
python src/api.py
```
> The server will start on http://127.0.0.1:5000

**Terminal 2 — Frontend:**

Ensure you are inside the `frontend` folder, then start the Vite development server:
```bash
npm run dev
```
> The React app will be accessible at http://localhost:5173

---

## Example Usage

1. Open your web browser and navigate to `http://localhost:5173`.
2. Click the **Upload New PDF** button in the left chat panel and select a document from your computer.
3. Wait for the file to render on the right and for the backend to finish parsing and indexing the text.
4. Type a question into the chat panel regarding the document's contents.
5. The AI will generate a contextual answer in the chat, and a **yellow bounding box** will automatically highlight the exact source paragraph on the PDF used to formulate the response.

---

## Screenshots

*(Insert an image of the split-screen application working here. You can drag and drop an image file directly into this README via the GitHub website.)*

---

## Acknowledgements

All submitted work reflects my own effort. Artificial Intelligence (AI) tools were utilized as an assistive resource during the development of this project to debug code, identify open-source packages (PyMuPDF, ChromaDB), and format structural descriptions. All core architectural decisions, logic flows, and final implementations are my own.