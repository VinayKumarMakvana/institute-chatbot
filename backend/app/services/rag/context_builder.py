from typing import List, Dict

class ContextBuilder:
    def build(self, retrieved_chunks: List[Dict]) -> str:
        if not retrieved_chunks:
            return ""
            
        context_parts = []
        for item in retrieved_chunks:
            chunk = item["chunk"]
            doc = item["doc"]
            
            part = f"""SOURCE
Document: {doc.title or 'Unknown'}
Page: {chunk.page_number or 'Unknown'}

Content:
{chunk.text or ''}
"""
            context_parts.append(part)
            
        return "\n\n".join(context_parts)

context_builder = ContextBuilder()
