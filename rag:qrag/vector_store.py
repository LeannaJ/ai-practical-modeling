import os
import pinecone
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import numpy as np

class VectorStore:
    """Class for interacting with vector database"""
    
    def __init__(self, api_key: str, environment: str, index_name: str):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        
        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        
        # Initialize embedding model
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Connect to index
        try:
            self.index = pinecone.Index(index_name)
            print(f"Connected to Pinecone index '{index_name}'.")
        except Exception as e:
            print(f"Failed to connect to Pinecone index: {e}")
            self.index = None
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Convert list of texts to embeddings."""
        try:
            embeddings = self.embed_model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return []
    
    def upsert_documents(self, documents: List[Dict]) -> bool:
        """Upsert documents to vector database."""
        if not self.index:
            print("Index not connected.")
            return False
        
        try:
            # Create embeddings
            texts = [doc["text"] for doc in documents]
            embeddings = self.create_embeddings(texts)
            
            if not embeddings:
                return False
            
            # Prepare data for Pinecone upsert
            vectors = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                vector_data = {
                    "id": f"doc_{doc.get('chunk_id', i)}",
                    "values": embedding,
                    "metadata": {
                        "text": doc["text"],
                        "chunk_id": doc.get("chunk_id", i),
                        "source": doc.get("source", "pdf"),
                        "topic": doc.get("topic", ""),
                        "bloom_level": doc.get("bloom_level", "")
                    }
                }
                vectors.append(vector_data)
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            print(f"Successfully stored {len(vectors)} documents in vector database.")
            return True
            
        except Exception as e:
            print(f"Error upserting documents: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Search for documents similar to query."""
        if not self.index:
            print("Index not connected.")
            return []
        
        try:
            # Create query embedding
            query_embedding = self.create_embeddings([query])
            if not query_embedding:
                return []
            
            # Execute search
            search_params = {
                "vector": query_embedding[0],
                "top_k": top_k,
                "include_metadata": True
            }
            
            # Apply filter
            if filter_dict:
                search_params["filter"] = filter_dict
            
            results = self.index.query(**search_params)
            
            # Process results
            documents = []
            for match in results["matches"]:
                doc = {
                    "id": match["id"],
                    "score": match["score"],
                    "text": match["metadata"]["text"],
                    "metadata": match["metadata"]
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def search_by_bloom_level(self, query: str, bloom_level: str, top_k: int = 5) -> List[Dict]:
        """Search filtered by specific Bloom's Taxonomy level."""
        filter_dict = {
            "bloom_level": {"$eq": bloom_level}
        }
        return self.search(query, top_k, filter_dict)
    
    def search_by_topic(self, query: str, topic: str, top_k: int = 5) -> List[Dict]:
        """Search filtered by specific topic."""
        filter_dict = {
            "topic": {"$eq": topic}
        }
        return self.search(query, top_k, filter_dict)
    
    def get_index_stats(self) -> Dict:
        """Get index statistics."""
        if not self.index:
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"Error retrieving index stats: {e}")
            return {}
    
    def delete_all_vectors(self) -> bool:
        """Delete all vectors from index."""
        if not self.index:
            return False
        
        try:
            self.index.delete(delete_all=True)
            print("All vectors deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            return False

def main():
    """Main function for testing"""
    # Get API key from environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    index_name = os.getenv("PINECONE_INDEX_NAME", "boost-ctc-index")
    
    if not api_key:
        print("PINECONE_API_KEY environment variable not set.")
        return
    
    # Initialize VectorStore
    vector_store = VectorStore(api_key, environment, index_name)
    
    # Test documents
    test_documents = [
        {
            "text": "AI in education can help personalize learning experiences for students.",
            "chunk_id": 1,
            "topic": "AI in Education",
            "bloom_level": "Understand"
        },
        {
            "text": "Critical thinking involves analyzing and evaluating information.",
            "chunk_id": 2,
            "topic": "Critical Thinking",
            "bloom_level": "Analyze"
        }
    ]
    
    # Test document upsert
    success = vector_store.upsert_documents(test_documents)
    if success:
        print("Test document upsert successful")
        
        # Test search
        query = "AI in education"
        results = vector_store.search(query, top_k=3)
        print(f"\nSearch results ({len(results)} found):")
        for i, doc in enumerate(results):
            print(f"{i+1}. Score: {doc['score']:.3f}")
            print(f"   Text: {doc['text'][:100]}...")
            print()

if __name__ == "__main__":
    main() 