import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

from pdf_processor import PDFProcessor
from query_parser import QueryParser
from vector_store import VectorStore
from llm_generator import LLMGenerator

class QRAGSystem:
    """Main class for QRAG (Query-Augmented Retrieval Generation) system"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "boost-ctc-index")
        
        # Initialize components
        self.query_parser = QueryParser()
        self.vector_store = None
        self.llm_generator = None
        
        # Initialize vector store (if API key is available)
        if self.pinecone_api_key:
            self.vector_store = VectorStore(
                self.pinecone_api_key,
                self.pinecone_environment,
                self.pinecone_index_name
            )
        
        # Initialize LLM generator (if API key is available)
        if self.openai_api_key:
            self.llm_generator = LLMGenerator(self.openai_api_key)
        
        print("🚀 QRAG system initialized!")
    
    def setup_vector_database(self, pdf_path: str) -> bool:
        """Process PDF file and set up vector database."""
        if not self.vector_store:
            print("❌ Pinecone API key not configured.")
            return False
        
        try:
            # Process PDF
            print("📄 Processing PDF file...")
            pdf_processor = PDFProcessor(pdf_path)
            chunks = pdf_processor.process_pdf()
            
            if not chunks:
                print("❌ Could not extract chunks from PDF.")
                return False
            
            # Upsert to vector database
            print("🗄️ Uploading documents to vector database...")
            success = self.vector_store.upsert_documents(chunks)
            
            if success:
                print(f"✅ Successfully stored {len(chunks)} documents in vector database.")
                return True
            else:
                print("❌ Failed to upload to vector database.")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up vector database: {e}")
            return False
    
    def process_query(self, user_query: str, top_k: int = 5) -> Dict:
        """Process user query to generate questions."""
        
        print(f"\n🔍 Starting query processing: {user_query}")
        
        # Step 1: Query semantic parsing
        print("📝 Step 1: Query semantic parsing...")
        parsed_query = self.query_parser.parse_query(user_query)
        print(f"   Parsing result: {parsed_query}")
        
        if parsed_query["confidence"] < 0.3:
            print("⚠️ Query parsing confidence is low.")
        
        # Step 2: Generate retrieval query
        print("🔎 Step 2: Generate retrieval query...")
        retrieval_query = self.query_parser.generate_retrieval_query(parsed_query)
        print(f"   Retrieval query: {retrieval_query}")
        
        # Step 3: Vector search
        print("🔍 Step 3: Vector search...")
        if not self.vector_store:
            print("❌ Vector store not initialized.")
            return {
                "success": False,
                "error": "Vector store not initialized",
                "parsed_query": parsed_query
            }
        
        search_results = self.vector_store.search(retrieval_query, top_k=top_k)
        print(f"   Search results: {len(search_results)} documents")
        
        if not search_results:
            print("⚠️ No search results found.")
            return {
                "success": False,
                "error": "No search results found",
                "parsed_query": parsed_query
            }
        
        # Create context
        context_text = "\n\n".join([doc["text"] for doc in search_results])
        print(f"   Context length: {len(context_text)} characters")
        
        # Step 4: LLM question generation
        print("🤖 Step 4: LLM question generation...")
        if not self.llm_generator:
            print("❌ LLM generator not initialized.")
            return {
                "success": False,
                "error": "LLM generator not initialized",
                "parsed_query": parsed_query,
                "context": context_text
            }
        
        generation_result = self.llm_generator.generate_questions(context_text, parsed_query)
        
        if generation_result["success"]:
            print("✅ Question generation completed!")
            
            # Process results
            formatted_questions = self.llm_generator.format_questions(
                generation_result["questions"]
            )
            
            return {
                "success": True,
                "original_query": user_query,
                "parsed_query": parsed_query,
                "retrieval_query": retrieval_query,
                "search_results": search_results,
                "context": context_text,
                "generated_questions": generation_result["questions"],
                "formatted_questions": formatted_questions,
                "model": generation_result["model"],
                "usage": generation_result.get("usage")
            }
        else:
            print(f"❌ Question generation failed: {generation_result['error']}")
            return {
                "success": False,
                "error": generation_result["error"],
                "parsed_query": parsed_query,
                "context": context_text
            }
    
    def get_system_status(self) -> Dict:
        """Check system status."""
        status = {
            "openai_configured": bool(self.openai_api_key),
            "pinecone_configured": bool(self.pinecone_api_key),
            "vector_store_ready": bool(self.vector_store and self.vector_store.index),
            "llm_generator_ready": bool(self.llm_generator)
        }
        
        if self.vector_store and self.vector_store.index:
            try:
                stats = self.vector_store.get_index_stats()
                status["vector_db_stats"] = stats
            except:
                status["vector_db_stats"] = "Error retrieving stats"
        
        return status
    
    def test_system(self) -> Dict:
        """Test the entire system."""
        print("🧪 Starting QRAG system test...")
        
        # Check system status
        status = self.get_system_status()
        print(f"System status: {status}")
        
        # Test query
        test_query = "Generate two Evaluate-level questions about AI in Education based on Bloom's Taxonomy."
        
        # Test query parsing
        print("\n📝 Testing query parsing...")
        parsed = self.query_parser.parse_query(test_query)
        print(f"Parsing result: {parsed}")
        
        # Test retrieval query generation
        print("\n🔎 Testing retrieval query generation...")
        retrieval_query = self.query_parser.generate_retrieval_query(parsed)
        print(f"Retrieval query: {retrieval_query}")
        
        # Test vector search (if vector store is available)
        if self.vector_store:
            print("\n🔍 Testing vector search...")
            search_results = self.vector_store.search(retrieval_query, top_k=3)
            print(f"Search results: {len(search_results)} found")
        
        # Test LLM generation (if LLM is available)
        if self.llm_generator:
            print("\n🤖 Testing LLM generation...")
            test_context = "AI in education can help personalize learning experiences for students."
            result = self.llm_generator.generate_questions(test_context, parsed)
            print(f"Generation result: {'Success' if result['success'] else 'Failed'}")
        
        return {
            "status": status,
            "test_query": test_query,
            "parsed_query": parsed,
            "retrieval_query": retrieval_query
        }

def main():
    """Main function - Test QRAG system"""
    
    # Initialize QRAG system
    qrag = QRAGSystem()
    
    # Check system status
    status = qrag.get_system_status()
    print("\n📊 System Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test system
    test_result = qrag.test_system()
    
    # Process actual query (if API keys are configured)
    if status["openai_configured"] and status["pinecone_configured"]:
        print("\n🚀 Testing actual query processing...")
        
        # Check if PDF file exists
        pdf_path = "PISA2018_Released_REA_Items_12112019.pdf"
        if os.path.exists(pdf_path):
            print("📄 PDF file found! Setting up vector database...")
            qrag.setup_vector_database(pdf_path)
        
        # Process query
        user_query = "Generate two Evaluate-level questions about AI in Education based on Bloom's Taxonomy."
        result = qrag.process_query(user_query)
        
        if result["success"]:
            print("\n✅ QRAG system working successfully!")
            print(f"Original query: {result['original_query']}")
            print(f"Generated questions:")
            for i, question in enumerate(result["formatted_questions"], 1):
                print(f"{i}. {question}")
        else:
            print(f"\n❌ Query processing failed: {result['error']}")
    else:
        print("\n⚠️ API keys not configured, skipping actual query processing.")
        print("Please create .env file referring to env_example.txt.")

if __name__ == "__main__":
    main() 