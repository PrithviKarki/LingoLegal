import fitz  # PyMuPDF

def extract_text_with_coordinates(pdf_path):
    """
    Extracts text from a PDF at the span level with bounding box coordinates.
    """
    doc = fitz.open(pdf_path)
    extracted_data = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:  
                            extracted_data.append({
                                "page": page_num + 1,
                                "text": text,
                                "bbox": span["bbox"] 
                            })
    return extracted_data

def semantic_chunking(extracted_spans, max_chars=500):
    """
    Stitches individual text spans into larger semantic chunks (paragraphs).
    Calculates a new master bounding box that wraps the entire chunk.
    """
    chunks = []
    current_chunk_text = ""
    current_bboxes = []
    current_page = None

    for span in extracted_spans:
        # If we switch pages, or reach the character limit, finalize the current chunk
        if current_page is not None and (span["page"] != current_page or len(current_chunk_text) + len(span["text"]) > max_chars):
            
            # Calculate the Master Bounding Box for the grouped text
            master_bbox = (
                min(b[0] for b in current_bboxes),  # Minimum x0 (Left-most edge)
                min(b[1] for b in current_bboxes),  # Minimum y0 (Top-most edge)
                max(b[2] for b in current_bboxes),  # Maximum x1 (Right-most edge)
                max(b[3] for b in current_bboxes)   # Maximum y1 (Bottom-most edge)
            )
            
            chunks.append({
                "page": current_page,
                "text": current_chunk_text.strip(),
                "bbox": master_bbox
            })
            
            # Reset for the next chunk
            current_chunk_text = ""
            current_bboxes = []
        
        # Add current span to the running chunk
        current_chunk_text += span["text"] + " "
        current_bboxes.append(span["bbox"])
        current_page = span["page"]
        
    # Append the final chunk if any text is left over
    if current_chunk_text:
        master_bbox = (
            min(b[0] for b in current_bboxes),
            min(b[1] for b in current_bboxes),
            max(b[2] for b in current_bboxes),
            max(b[3] for b in current_bboxes)
        )
        chunks.append({
            "page": current_page,
            "text": current_chunk_text.strip(),
            "bbox": master_bbox
        })
        
    return chunks

if __name__ == "__main__":
    sample_pdf = "data/raw/sample_agreement.pdf"
    
    try:
        # 1. Extract the raw individual words
        raw_spans = extract_text_with_coordinates(sample_pdf)
        print(f"Extracted {len(raw_spans)} individual text spans.")
        
        # 2. Group them into semantic chunks
        processed_chunks = semantic_chunking(raw_spans, max_chars=500)
        print(f"Aggregated into {len(processed_chunks)} semantic chunks.\n")
        
        # 3. Print a sample to verify the master bounding box
        print("--- SAMPLE CHUNK ---")
        print(f"Page: {processed_chunks[0]['page']}")
        print(f"Master BBox: {processed_chunks[0]['bbox']}")
        print(f"Text: {processed_chunks[0]['text']}")
        print("--------------------")
        
    except Exception as e:
        print(f"Error parsing PDF: {e}")