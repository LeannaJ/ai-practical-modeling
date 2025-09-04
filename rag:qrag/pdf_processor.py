import PyPDF2
import re
from typing import List, Dict
import os

class PDFProcessor:
    """Class for processing PDF files to extract text and split into chunks"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_text(self) -> str:
        """Extract text from PDF file."""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove unnecessary whitespace
        text = re.sub(r'\s+', ' ', text)
        # Clean special characters
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        return text.strip()
    
    def split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Split text into overlapping chunks."""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": len(chunks),
                    "start_word": i,
                    "end_word": min(i + chunk_size, len(words))
                })
        
        return chunks
    
    def process_pdf(self, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """Process PDF and return list of chunks."""
        print(f"Processing PDF file: {self.pdf_path}")
        
        # Extract text
        raw_text = self.extract_text()
        if not raw_text:
            return []
        
        # Clean text
        cleaned_text = self.clean_text(raw_text)
        
        # Split into chunks
        chunks = self.split_into_chunks(cleaned_text, chunk_size, overlap)
        
        print(f"Generated {len(chunks)} chunks successfully")
        return chunks

def main():
    """Main function for testing"""
    pdf_path = "PISA2018_Released_REA_Items_12112019.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    processor = PDFProcessor(pdf_path)
    chunks = processor.process_pdf()
    
    # Print first chunk example
    if chunks:
        print("\nFirst chunk example:")
        print(chunks[0]["text"][:500] + "...")

if __name__ == "__main__":
    main() 