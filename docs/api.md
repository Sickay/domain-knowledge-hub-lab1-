# Документація REST API (Domain Knowledge Hub)

Сервер реалізовано на базі **FastAPI**. Після запуску сервісу інтерактивна документація OpenAPI доступна за адресами:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Автентифікація та ролі
Для доступу до захищених ендпоінтів (`/ask`, `/sources/{id}`) необхідно передавати у заголовках запиту дійсний API-ключ:
- `X-API-Key: secret_user_token` (роль звичайного користувача `user`)
- `X-API-Key: secret_admin_token` (роль адміністратора `admin`)

---

## Приклади запитів (cURL)

### 1. Перевірка стану (Health Check) — без автентифікації
```bash
curl -X GET "http://localhost:8000/health
2. Запит до RAG (POST /ask) з роллю користувача
Bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: secret_user_token" \
     -d '{"query": "Який термін обробки замовлень?", "top_k": 3}'
3. Запит внутрішнього документа (GET /sources/doc_103) з роллю user (повинно повернути помилку 403)
Bash
curl -i -X GET "http://localhost:8000/sources/doc_103" \
     -H "X-API-Key: secret_user_token"
4. Запит внутрішнього документа (GET /sources/doc_103) з роллю admin (успішно)
Bash
curl -i -X GET "http://localhost:8000/sources/doc_103" \
     -H "X-API-Key: secret_admin_token"
