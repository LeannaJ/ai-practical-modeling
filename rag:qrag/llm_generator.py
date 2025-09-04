import os
from openai import OpenAI
from typing import List, Dict, Optional

class LLMGenerator:
    """Class for generating questions using OpenAI LLM"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        
        # Default system prompt
        self.default_system_prompt = """You are an expert educational content creator specializing in creating high-quality questions based on Bloom's Taxonomy. You create questions that promote critical thinking and deep understanding.

Your role is to:
1. Analyze the provided context and user requirements
2. Generate appropriate questions based on the specified Bloom's Taxonomy level
3. Ensure questions are clear, relevant, and educational
4. Follow the exact format requested by the user

Guidelines for Bloom's Taxonomy levels:
- Remember: Recall facts, terms, basic concepts
- Understand: Explain ideas, interpret information
- Apply: Use information in new situations
- Analyze: Break down information, compare and contrast
- Evaluate: Make judgments, critique, assess
- Create: Design, construct, develop new ideas"""
    
    def create_question_prompt(self, context: str, parsed_query: Dict) -> str:
        """Create prompt for question generation."""
        
        bloom_level = parsed_query.get("bloom_level", "Evaluate")
        topic = parsed_query.get("topic", "general education")
        quantity = parsed_query.get("quantity", 2)
        question_type = parsed_query.get("question_type", "question")
        
        prompt = f"""Context Information:
{context}

User Request:
- Bloom's Taxonomy Level: {bloom_level}
- Topic: {topic}
- Number of {question_type}s: {quantity}
- Original Query: {parsed_query.get('original_query', '')}

Please generate {quantity} {bloom_level}-level {question_type}s about {topic} based on the provided context.

Requirements:
1. Each {question_type} should clearly demonstrate {bloom_level} level thinking
2. {question_type}s should be relevant to the context provided
3. {question_type}s should be appropriate for educational use
4. Format each {question_type} clearly and concisely
5. Do not include explanations or additional text, just the {question_type}s

Generate the {question_type}s now:"""
        
        return prompt
    
    def generate_questions(self, context: str, parsed_query: Dict, 
                          system_prompt: Optional[str] = None) -> Dict:
        """Generate questions based on context and parsed query."""
        
        try:
            # Create prompt
            user_prompt = self.create_question_prompt(context, parsed_query)
            
            # Set system prompt
            if not system_prompt:
                system_prompt = self.default_system_prompt
            
            # Call LLM
            completion = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract result
            generated_content = completion.choices[0].message.content
            
            return {
                "success": True,
                "questions": generated_content,
                "model": "gpt-4-turbo",
                "usage": completion.usage,
                "parsed_query": parsed_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "parsed_query": parsed_query
            }
    
    def generate_questions_with_fallback(self, context: str, parsed_query: Dict) -> Dict:
        """Generate questions using fallback model."""
        
        try:
            # Create prompt
            user_prompt = self.create_question_prompt(context, parsed_query)
            
            # Use GPT-3.5-turbo as fallback
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self.default_system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            generated_content = completion.choices[0].message.content
            
            return {
                "success": True,
                "questions": generated_content,
                "model": "gpt-3.5-turbo (fallback)",
                "usage": completion.usage,
                "parsed_query": parsed_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "parsed_query": parsed_query
            }
    
    def format_questions(self, questions_text: str) -> List[str]:
        """Format generated question text into individual question list."""
        # Split by line breaks
        lines = questions_text.strip().split('\n')
        
        # Remove empty lines and numbering
        formatted_questions = []
        for line in lines:
            line = line.strip()
            if line:
                # Remove numbering (1., 2., etc.)
                if line[0].isdigit() and '. ' in line:
                    line = line.split('. ', 1)[1]
                formatted_questions.append(line)
        
        return formatted_questions
    
    def validate_questions(self, questions: List[str], bloom_level: str) -> Dict:
        """Validate that generated questions meet requirements."""
        validation_result = {
            "valid": True,
            "issues": [],
            "question_count": len(questions)
        }
        
        # Check question count
        if len(questions) == 0:
            validation_result["valid"] = False
            validation_result["issues"].append("No questions generated")
        
        # Validate each question
        for i, question in enumerate(questions):
            if len(question.strip()) < 10:
                validation_result["issues"].append(f"Question {i+1} is too short")
            
            if not question.endswith('?'):
                validation_result["issues"].append(f"Question {i+1} doesn't end with '?'")
        
        if validation_result["issues"]:
            validation_result["valid"] = False
        
        return validation_result

def main():
    """Main function for testing"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("OPENAI_API_KEY environment variable not set.")
        return
    
    # Initialize LLMGenerator
    generator = LLMGenerator(api_key)
    
    # Test data
    test_context = """Artificial Intelligence (AI) in education has become increasingly prevalent in recent years. AI technologies can personalize learning experiences, provide instant feedback, and help teachers identify areas where students need additional support. However, there are also concerns about privacy, data security, and the potential replacement of human teachers."""
    
    test_parsed_query = {
        "original_query": "Generate two Evaluate-level questions about AI in Education based on Bloom's Taxonomy.",
        "bloom_level": "Evaluate",
        "topic": "AI in Education",
        "question_type": "question",
        "quantity": 2,
        "confidence": 0.9
    }
    
    # Test question generation
    print("Generating questions...")
    result = generator.generate_questions(test_context, test_parsed_query)
    
    if result["success"]:
        print("✅ Question generation successful!")
        print(f"Model: {result['model']}")
        print(f"Token usage: {result['usage']}")
        print("\nGenerated questions:")
        print(result["questions"])
        
        # Format and validate questions
        formatted_questions = generator.format_questions(result["questions"])
        validation = generator.validate_questions(formatted_questions, "Evaluate")
        
        print(f"\nValidation result: {'✅ Passed' if validation['valid'] else '❌ Failed'}")
        if validation["issues"]:
            print("Issues:")
            for issue in validation["issues"]:
                print(f"  - {issue}")
    else:
        print(f"❌ Question generation failed: {result['error']}")

if __name__ == "__main__":
    main() 