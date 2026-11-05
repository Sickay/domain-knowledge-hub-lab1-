from fastapi import FastAPI, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time

app = FastAPI(
    title="Domain Knowledge Hub API",
    version="1.0.0",
    description="REST API для гібридного RAG-чату з графом знань, валідацією та ролевою системою доступу."
)

# База даних документів для перевірки джерел та рівнів чутливості (sensitivity)
DATABASE = {
    "doc_101": {"id": "doc_101", "content": "Основний регламент виконується за схемою A.", "sensitivity": "public"},
    "doc_102": {"id": "doc_102", "content": "Альтернативний термін обробки складає 5 днів.", "sensitivity": "public"},
    "doc_103": {"id": "doc_103", "content": "Конфіденційні параметри сервера X та внутрішня топологія.", "sensitivity": "internal"}
}

# Реєстр API-ключів для симуляції ролей
API_KEYS = {
    "secret_user_token": "user",
    "secret_admin_token": "admin"
}

def get_current_user(x_api_key: Optional[str] = Header(None)) -> Dict[str, str]:
    """Перевірка автентифікації за заголовком X-API-Key та визначення ролі."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Відсутній API-ключ у заголовку X-API-Key"
        )
    if x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недійсний API-ключ або заборонений доступ"
        )
    return {"role": API_KEYS[x_api_key]}

# Pydantic моделі для валідації вхідних даних
class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=300, description="Текст запитання до RAG")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Кількість релевантних документів")

class AskResponse(BaseModel):
    query: str
    response: str
    sources: List[str]
    citations_valid: bool
    tokens: Dict[str, int]
    latency_sec: float

# --- Ендпоінти ---

@app.get("/health", tags=["System"])
def health_check():
    """Перевірка стану здоров'я сервісу."""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/ask", response_model=AskResponse, tags=["RAG"])
def ask_question(body: AskRequest, user: Dict[str, str] = Depends(get_current_user)):
    """Основний ендпоінт для запитань до гібридного RAG з урахуванням ролей."""
    start_time = time.time()
    role = user["role"]
    
    # Pre-filter документів за рівнем доступу (sensitivity)
    allowed_docs = []
    for doc_id, doc in DATABASE.items():
        if doc["sensitivity"] == "internal" and role != "admin":
            continue
        allowed_docs.append(doc_id)

    # Симуляція відповіді RAG
    response_text = f"Згідно з регламентом, обробка виконується за стандартом [doc_101]."
    
    latency = round(time.time() - start_time, 4)
    
    return {
        "query": body.query,
        "response": response_text,
        "sources": allowed_docs[:body.top_k],
        "citations_valid": True,
        "tokens": {"prompt_tokens": 110, "completion_tokens": 20, "total_tokens": 130},
        "latency_sec": latency
    }

@app.get("/sources/{source_id}", tags=["Sources"])
def get_source(source_id: str, user: Dict[str, str] = Depends(get_current_user)):
    """Отримання інформації про конкретне джерело за його ID з перевіркою прав."""
    if source_id not in DATABASE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Джерело з ID '{source_id}' не знайдено в базі"
        )
    
    doc = DATABASE[source_id]
    
    # Перевірка прав доступу до внутрішніх (internal) документів
    if doc["sensitivity"] == "internal" and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено: цей документ містить внутрішні дані та вимагає ролі admin"
        )
        
    return doc
