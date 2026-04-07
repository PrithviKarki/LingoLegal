import { useState } from 'react';
import axios from 'axios';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import './App.css';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { text: "Welcome to LingoLegal! Please upload a document to get started.", sender: 'ai' }
  ]);
  const [loading, setLoading] = useState(false);
  
  // NEW: State for the dynamic file upload
  const [selectedFile, setSelectedFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null); 
  const [isUploading, setIsUploading] = useState(false);

  // State for the Explainable AI (XAI) highlight
  const [highlightPage, setHighlightPage] = useState(null);
  const [highlightBbox, setHighlightBbox] = useState(null);

  // NEW: Function to handle the file upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setIsUploading(true);
    setHighlightBbox(null); // Clear any old highlights

    // 1. Create a local temporary URL so react-pdf can render it instantly on the right side
    const localFileUrl = URL.createObjectURL(file);
    setPdfUrl(localFileUrl);

    // 2. Package the file to send to Flask
    const formData = new FormData();
    formData.append("file", file);

    try {
      // 3. Send it to the upcoming Flask /upload endpoint
      await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setMessages(prev => [...prev, { text: `Successfully processed ${file.name}! What would you like to know about it?`, sender: 'ai' }]);
    } catch (error) {
      console.error("Error uploading file:", error);
      setMessages(prev => [...prev, { text: "Error uploading the file to the server. Is the Flask backend running?", sender: 'ai' }]);
    }
    setIsUploading(false);
  };

  const handleAskQuestion = async () => {
    if (!query) return;

    setMessages(prev => [...prev, { text: query, sender: 'user' }]);
    setLoading(true);
    setQuery('');
    setHighlightBbox(null); 

    try {
      const response = await axios.post('http://127.0.0.1:5000/ask', {
        query: query
      });

      const data = response.data;
      setMessages(prev => [...prev, { text: data.answer, sender: 'ai' }]);

      if (data.metadata && data.metadata.bbox) {
        const coords = data.metadata.bbox.replace(/[()]/g, '').split(',').map(Number);
        setHighlightPage(data.metadata.page);
        setHighlightBbox({
          x0: coords[0],
          y0: coords[1],
          x1: coords[2],
          y1: coords[3]
        });
      }
    } catch (error) {
      console.error("Error asking question:", error);
      setMessages(prev => [...prev, { text: "Error connecting to backend.", sender: 'ai' }]);
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      {/* LEFT SIDE: Chat Panel */}
      <div className="chat-panel">
        <h2>LingoLegal Assistant</h2>
        
        {/* NEW: Dynamic Upload Zone */}
        <div className="upload-zone">
          <label className="upload-label">
            {isUploading ? "Uploading..." : "Upload New PDF"}
            <input type="file" accept="application/pdf" onChange={handleFileUpload} disabled={isUploading} />
          </label>
          {selectedFile && <div className="file-name">{selectedFile.name}</div>}
        </div>

        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}-message`}>
              {msg.text}
            </div>
          ))}
          {loading && <div className="message ai-message">Thinking...</div>}
        </div>
        
        <div className="input-area">
          <input 
            type="text" 
            value={query} 
            onChange={(e) => setQuery(e.target.value)} 
            placeholder={selectedFile ? "Ask about your document..." : "Please upload a document first"}
            onKeyDown={(e) => e.key === 'Enter' && selectedFile && handleAskQuestion()}
            disabled={!selectedFile || isUploading}
          />
          <button onClick={handleAskQuestion} disabled={!selectedFile || isUploading}>Ask</button>
        </div>
      </div>

      {/* RIGHT SIDE: PDF Viewer */}
      <div className="pdf-panel">
        {/* NEW: Dynamically render the uploaded file, or a placeholder if none exists */}
        {pdfUrl ? (
          <Document file={pdfUrl} onLoadError={console.error}>
            <div className="pdf-page-wrapper">
              <Page pageNumber={1} renderTextLayer={false} renderAnnotationLayer={false} />
              
              {highlightBbox && highlightPage === 1 && (
                <div 
                  className="highlight-box"
                  style={{
                    left: `${highlightBbox.x0}px`,
                    top: `${highlightBbox.y0}px`,
                    width: `${highlightBbox.x1 - highlightBbox.x0}px`,
                    height: `${highlightBbox.y1 - highlightBbox.y0}px`,
                  }}
                />
              )}
            </div>
          </Document>
        ) : (
          <div style={{ color: "white", marginTop: "40%" }}>
            <h3>No Document Loaded</h3>
            <p>Upload a PDF on the left to begin.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;