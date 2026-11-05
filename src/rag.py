import os
import json
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict

# Mock-векторне сховище та реранкер для ізольованого виклику у Colab
@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]  # містить sensitivity_level, access_roles тощо

class MockVectorStore:
    def __init__(self, docs: List[Document]):
        self.docs = docs

    def search_with_prefilter(self, query: str, user_role: str, top_k: int = 5) -> List[Document]:
        """Pre-filtering за правами доступу користувача."""
        filtered_docs = []
        for doc in self.docs:
            allowed_roles = doc.metadata.get("allowed_roles", [])
            if user_role in allowed_roles or "admin" in allowed_roles:
                filtered_docs.append(doc)
        return filtered_docs[:top_k]

class MockReranker:
    def rerank(self, query: str, docs: List[Document], top_n: int = 3) -> List[Document]:
        """Переранжування результатів (mock-версія повертає top_n)."""
        return docs[:top_n]

class RAGPipeline:
    def __init__(self, vector_store: MockVectorStore, reranker: MockReranker, system_prompt: str, llm_client=None):
        self.vector_store = vector_store
        self.reranker = reranker
        self.system_prompt = system_prompt
        self.llm_client = llm_client
        self.execution_log = []

    def validate_citations(self, response_text: str, context_docs: List[Document]) -> Tuple[bool, List[str]]:
        """Крок 3: Перевірка, що всі цитовані [id] присутні у наданому контексті."""
        import re
        valid_ids = {doc.id for doc in context_docs}
        cited_ids = set(re.findall(r'\[(.*?)\]', response_text))
        
        invalid_citations = [c_id for c_id in cited_ids if c_id not in valid_ids]
        is_valid = len(invalid_citations) == 0
        return is_valid, invalid_citations

    def generate_mock_llm_response(self, query: str, context_docs: List[Document]) -> Tuple[str, Dict[str, int]]:
        """Імітація відповіді LLM згідно з правилами промпту."""
        if not context_docs:
            return "Я не можу відповісти на це запитання на основі наданого контексту.", {"prompt_tokens": 50, "completion_tokens": 15, "total_tokens": 65}
        
        # Симуляція обробки запитів
        if "невідоме" in query.lower():
            text = "Я не можу відповісти на це запитання на основі наданого контексту."
        elif "конфлікт" in query.lower():
            text = f"Згідно з [{context_docs[0].id}] термін складає 3 дні, але за [{context_docs[1].id}] термін дорівнює 5 днів."
        else:
            text = f"На основі наданих даних, основний регламент виконується за схемою A [{context_docs[0].id}]."

        tokens = {"prompt_tokens": 120, "completion_tokens": 30, "total_tokens": 150}
        return text, tokens

    def run(self, query: str, user_role: str = "user") -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Пошук з pre-filter
        retrieved_docs = self.vector_store.search_with_prefilter(query, user_role=user_role, top_k=5)
        
        # 2. Reranking
        ranked_docs = self.reranker.rerank(query, retrieved_docs, top_n=3)
        
        # 3. Генерація відповіді
        response_text, token_usage = self.generate_mock_llm_response(query, ranked_docs)
        
        # 4. Валідація цитат
        citations_valid, invalid_citations = self.validate_citations(response_text, ranked_docs)
        
        latency = round(time.time() - start_time, 4)
        
        # 5. Логування (Крок 4)
        log_entry = {
            "query": query,
            "user_role": user_role,
            "retrieved_source_ids": [d.id for d in ranked_docs],
            "response": response_text,
            "citations_valid": citations_valid,
            "invalid_citations": invalid_citations,
            "tokens": token_usage,
            "latency_sec": latency
        }
        self.execution_log.append(log_entry)
        return log_entry
