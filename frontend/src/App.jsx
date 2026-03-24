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
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // State for the Explainable AI (XAI) highlight
  const [highlightPage, setHighlightPage] = useState(null);
  const [highlightBbox, setHighlightBbox] = useState(null);

  const handleAskQuestion = async () => {
    if (!query) return;

    // Add user question to chat
    setMessages(prev => [...prev, { text: query, sender: 'user' }]);
    setLoading(true);
    setQuery('');
    setHighlightBbox(null); // Clear previous highlight

    try {
      // Call your Flask Backend
      const response = await axios.post('http://127.0.0.1:5000/ask', {
        query: query
      });

      const data = response.data;
      
      // Add AI answer to chat
      setMessages(prev => [...prev, { text: data.answer, sender: 'ai' }]);

      // Parse the bounding box coordinates for the highlight
      if (data.metadata && data.metadata.bbox) {
        // Convert string "(x0, y0, x1, y1)" to an array of numbers
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
            placeholder="Ask about your document..."
            onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
          />
          <button onClick={handleAskQuestion}>Ask</button>
        </div>
      </div>

      {/* RIGHT SIDE: PDF Viewer */}
      <div className="pdf-panel">
        <Document file="/sample_agreement.pdf" onLoadError={console.error}>
          <div className="pdf-page-wrapper">
            {/* Hardcoded to page 1 for now, matches our simple parser */}
            <Page pageNumber={1} renderTextLayer={false} renderAnnotationLayer={false} />
            
            {/* The XAI Highlight Logic */}
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
      </div>
    </div>
  );
}

export default App;