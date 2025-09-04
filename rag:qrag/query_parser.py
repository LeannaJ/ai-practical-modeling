import re
from typing import Dict, Optional, List

class QueryParser:
    """Class for semantically parsing user queries"""
    
    def __init__(self):
        # Bloom's Taxonomy levels
        self.bloom_levels = {
            "remember": ["remember", "recall", "identify", "list", "name", "define"],
            "understand": ["understand", "explain", "describe", "summarize", "interpret"],
            "apply": ["apply", "use", "implement", "execute", "demonstrate"],
            "analyze": ["analyze", "compare", "contrast", "examine", "investigate"],
            "evaluate": ["evaluate", "assess", "judge", "critique", "appraise"],
            "create": ["create", "design", "develop", "construct", "produce"]
        }
        
        # Education-related topics
        self.education_topics = [
            "ai in education", "artificial intelligence", "machine learning",
            "critical thinking", "reading comprehension", "mathematics",
            "science education", "language learning", "assessment",
            "personalized learning", "digital literacy", "problem solving"
        ]
    
    def extract_bloom_level(self, query: str) -> Optional[str]:
        """Extract Bloom's Taxonomy level from query."""
        query_lower = query.lower()
        
        # Direct level matching
        for level, keywords in self.bloom_levels.items():
            if level in query_lower:
                return level.title()
            
            # Keyword matching
            for keyword in keywords:
                if keyword in query_lower:
                    return level.title()
        
        return None
    
    def extract_topic(self, query: str) -> Optional[str]:
        """Extract topic from query."""
        query_lower = query.lower()
        
        # "about" pattern matching
        about_pattern = r"about\s+([^,\.]+)"
        about_match = re.search(about_pattern, query_lower)
        if about_match:
            topic = about_match.group(1).strip()
            return topic.title()
        
        # Education topic matching
        for topic in self.education_topics:
            if topic in query_lower:
                return topic.title()
        
        return None
    
    def extract_question_type(self, query: str) -> Optional[str]:
        """Extract question type from query."""
        query_lower = query.lower()
        
        if "question" in query_lower:
            return "question"
        elif "problem" in query_lower:
            return "problem"
        elif "task" in query_lower:
            return "task"
        elif "exercise" in query_lower:
            return "exercise"
        
        return None
    
    def extract_quantity(self, query: str) -> Optional[int]:
        """Extract requested quantity from query."""
        # Number pattern matching
        number_pattern = r"(\d+)\s+(question|problem|task|exercise)"
        match = re.search(number_pattern, query.lower())
        if match:
            return int(match.group(1))
        
        # Text number matching
        text_numbers = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        
        for text, num in text_numbers.items():
            if text in query.lower():
                return num
        
        return None
    
    def parse_query(self, query: str) -> Dict:
        """Parse query completely."""
        parsed = {
            "original_query": query,
            "bloom_level": self.extract_bloom_level(query),
            "topic": self.extract_topic(query),
            "question_type": self.extract_question_type(query),
            "quantity": self.extract_quantity(query),
            "confidence": 0.0
        }
        
        # Calculate confidence score based on extracted information
        confidence_score = 0
        if parsed["bloom_level"]:
            confidence_score += 0.3
        if parsed["topic"]:
            confidence_score += 0.3
        if parsed["question_type"]:
            confidence_score += 0.2
        if parsed["quantity"]:
            confidence_score += 0.2
        
        parsed["confidence"] = confidence_score
        
        return parsed
    
    def generate_retrieval_query(self, parsed: Dict) -> str:
        """Generate retrieval query based on parsed information."""
        parts = []
        
        if parsed["topic"]:
            parts.append(parsed["topic"])
        
        if parsed["bloom_level"]:
            parts.append(f"Bloom's Taxonomy {parsed['bloom_level']} level")
        
        if parsed["question_type"]:
            parts.append(f"{parsed['question_type']} examples")
        
        # Add default keywords
        parts.extend(["education", "learning", "assessment"])
        
        return " AND ".join(parts)

def main():
    """Main function for testing"""
    parser = QueryParser()
    
    # Test queries
    test_queries = [
        "Generate two Evaluate-level questions about AI in Education based on Bloom's Taxonomy.",
        "Create three Analyze questions for critical thinking in mathematics.",
        "Make one Remember question about reading comprehension.",
        "Design four Apply problems for science education."
    ]
    
    for query in test_queries:
        print(f"\nOriginal query: {query}")
        parsed = parser.parse_query(query)
        print(f"Parsing result: {parsed}")
        
        retrieval_query = parser.generate_retrieval_query(parsed)
        print(f"Retrieval query: {retrieval_query}")

if __name__ == "__main__":
    main() 