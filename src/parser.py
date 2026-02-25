import fitz  # PyMuPDF

def extract_text_with_coordinates(pdf_path):
    """
    Extracts text from a PDF along with its page number and bounding box coordinates.
    This spatial metadata is critical for the XAI highlighting feature.
    """
    doc = fitz.open(pdf_path)
    extracted_data = []

    # Iterate through every page in the document
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract text as a dictionary to retain layout and coordinate data
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            # Check if the block contains text lines
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:  # Ignore empty strings
                            extracted_data.append({
                                "page": page_num + 1,
                                "text": text,
                                "bbox": span["bbox"] # Coordinates: (x0, y0, x1, y1)
                            })
    
    return extracted_data

if __name__ == "__main__":
    # Test the function (Make sure to put a sample PDF in your data/raw folder!)
    sample_pdf = "./data/raw/sample_agreement.pdf"
    
    try:
        data = extract_text_with_coordinates(sample_pdf)
        print(f"Successfully extracted {len(data)} text spans.")
        print("Sample of first span:", data[0])
    except Exception as e:
        print(f"Error parsing PDF: {e}")