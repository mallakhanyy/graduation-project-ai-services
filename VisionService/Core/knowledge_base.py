"""
RAG-based knowledge base for dynamic recommendations.
"""

import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

from .problem_info import get_knowledge_documents, PROBLEM_INFO

class SimpleKnowledgeBase:
    """
    Simple knowledge base with document retrieval.
    This is a lightweight version that doesn't require external LLM.
    """
    
    def __init__(self):
        self.documents = get_knowledge_documents()
        self._build_index()
    
    def _build_index(self):
        """Build a simple keyword-based index."""
        self.index = {}
        for doc in self.documents:
            content = doc["page_content"].lower()
            words = content.split()
            for word in words:
                if len(word) > 3:
                    if word not in self.index:
                        self.index[word] = []
                    if doc not in self.index[word]:
                        self.index[word].append(doc)
    
    def query_knowledge(self, query: str) -> Dict[str, Any]:
        """
        Query the knowledge base.
        
        Args:
            query: Question or problem description
            
        Returns:
            Dictionary with answer and sources
        """
        # Simple keyword matching
        query_words = query.lower().split()
        relevant_docs = []
        scores = {}
        
        for word in query_words:
            if len(word) > 3 and word in self.index:
                for doc in self.index[word]:
                    doc_id = doc["page_content"][:50]
                    scores[doc_id] = scores.get(doc_id, 0) + 1
                    if doc not in relevant_docs:
                        relevant_docs.append(doc)
        
        # Sort by relevance
        relevant_docs.sort(
            key=lambda d: scores.get(d["page_content"][:50], 0),
            reverse=True
        )
        
        # Get top 3
        top_docs = relevant_docs[:3]
        
        if not top_docs:
            return {
                "answer": "No relevant information found.",
                "sources": []
            }
        
        # Combine documents
        combined = "\n\n".join([d["page_content"] for d in top_docs])
        
        return {
            "answer": combined,
            "sources": top_docs
        }
    
    def add_document(self, content: str, metadata: Dict[str, Any]):
        """Add a new document."""
        doc = {
            "page_content": content,
            "metadata": metadata
        }
        self.documents.append(doc)
        self._build_index()
        print(f"✅ Added new document: {metadata}")

# Create singleton instance
knowledge_base = SimpleKnowledgeBase()

def get_knowledge_recommendation(
    problem_type: str,
    confidence: float,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Get recommendation using knowledge base with fallback to rule-based.
    
    Args:
        problem_type: Detected problem type
        confidence: AI confidence
        context: Context dictionary (weather, location, etc.)
    
    Returns:
        Recommendation dictionary
    """
    if context is None:
        context = {}
    
    # Build query
    query = f"""
    Problem Type: {problem_type}
    Confidence: {confidence}%
    Context: {json.dumps(context, ensure_ascii=False)}
    
    Provide recommendation:
    1. What is the problem? (Arabic)
    2. What should the user do?
    3. Why is this happening?
    4. Steps to fix
    5. Severity level
    """
    
    # Query knowledge base
    result = knowledge_base.query_knowledge(query)
    answer = result.get("answer", "")
    
    # If no answer or using fallback, use static PROBLEM_INFO
    if not answer or "No relevant" in answer:
        info = PROBLEM_INFO.get(problem_type, {})
        return {
            "arabic": info.get("arabic", problem_type),
            "recommendation": info.get("recommendation", ""),
            "explanation": info.get("explanation", "").strip(),
            "steps": info.get("steps", []),
            "sources": result.get("sources", []),
            "generated": False
        }
    
    # Parse the answer
    return parse_recommendation(answer, problem_type)

def parse_recommendation(answer: str, problem_type: str) -> Dict[str, Any]:
    """Parse the knowledge base response into structured recommendation."""
    info = PROBLEM_INFO.get(problem_type, {})
    
    return {
        "arabic": info.get("arabic", problem_type),
        "recommendation": extract_section(answer, "Recommendation") or info.get("recommendation", ""),
        "explanation": extract_section(answer, "Explanation") or info.get("explanation", "").strip(),
        "steps": extract_steps(answer) or info.get("steps", []),
        "sources": [],
        "generated": True
    }

def extract_section(text: str, section: str) -> str:
    """Extract a section from the text."""
    pattern = rf"{section}[:](.*?)(?:\n\n|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def extract_steps(text: str) -> List[str]:
    """Extract steps from the text."""
    steps = []
    pattern = r"(\d+)[.)]\s*(.*?)(?=\n\d+[.)]|$)"
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        steps.append(match[1].strip())
    return steps