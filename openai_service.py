import json
import os
from openai import OpenAI

# Alpha Nex AI Content Analysis Service
# Provides AI-powered content quality assessment and duplicate detection

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def detect_duplicate_content(file_path, description):
    """
    Analyze content for potential duplicates and spam using AI.
    
    Args:
        file_path (str): Path to the uploaded file
        description (str): User-provided content description
        
    Returns:
        tuple: (duplicate_score, spam_score) both float values 0.0-1.0
    """
    if not openai_client:
        # Return default scores if OpenAI is not available
        return 0.0, 0.0
    
    try:
        # Create analysis prompt
        prompt = f"""
        Analyze the following content description for potential issues:
        
        Description: "{description}"
        
        Please evaluate:
        1. Duplicate/repetitive content likelihood (0.0-1.0)
        2. Spam/low-quality content likelihood (0.0-1.0)
        
        Consider factors like:
        - Generic or template-like descriptions
        - Excessive promotional language
        - Lack of specific details
        - Common spam patterns
        
        Respond with JSON in this format:
        {{"duplicate_score": number, "spam_score": number}}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a content quality analyzer. Evaluate content descriptions for duplicate/spam likelihood and return scores between 0.0 (clean) and 1.0 (problematic)."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        
        result = json.loads(response.choices[0].message.content)
        duplicate_score = max(0.0, min(1.0, result.get("duplicate_score", 0.0)))
        spam_score = max(0.0, min(1.0, result.get("spam_score", 0.0)))
        
        return duplicate_score, spam_score
        
    except Exception as e:
        print(f"OpenAI analysis failed: {e}")
        # Return conservative scores on error
        return 0.2, 0.2

def check_content_quality(content_text):
    """
    Evaluate content quality for review accuracy.
    Returns quality score 0.0-1.0
    """
    if not openai_client:
        return 0.5  # Default neutral score
    
    try:
        prompt = f"""
        Evaluate the quality of this content review:
        
        Review: "{content_text}"
        
        Consider:
        - Constructiveness and helpfulness
        - Specific details vs generic comments
        - Appropriate tone and language
        - Evidence of actual content evaluation
        
        Return quality score 0.0 (poor) to 1.0 (excellent) as JSON:
        {{"quality_score": number}}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a review quality evaluator. Score reviews based on their constructiveness and specificity."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=50
        )
        
        result = json.loads(response.choices[0].message.content)
        return max(0.0, min(1.0, result.get("quality_score", 0.5)))
        
    except Exception as e:
        print(f"Quality check failed: {e}")
        return 0.5

def analyze_content_description(description, category):
    """
    Analyze if content description matches its category and is appropriate.
    Returns analysis results with suggestions.
    """
    if not openai_client:
        return {"appropriate": True, "confidence": 0.5, "suggestions": []}
    
    try:
        prompt = f"""
        Analyze this content description and category match:
        
        Category: {category}
        Description: "{description}"
        
        Evaluate:
        1. Does description match the category?
        2. Is content appropriate for a professional platform?
        3. Any red flags or policy violations?
        
        Respond with JSON:
        {{
            "appropriate": boolean,
            "confidence": number,
            "category_match": boolean,
            "issues": [list of strings],
            "suggestions": [list of strings]
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a content moderation assistant evaluating uploads for appropriateness and category matching."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=300
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Content analysis failed: {e}")
        return {
            "appropriate": True,
            "confidence": 0.5,
            "category_match": True,
            "issues": [],
            "suggestions": []
        }
