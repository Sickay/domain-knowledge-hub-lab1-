import os
import time
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi

class HybridSearchEngine:
    def __init__(self, embedding_model_name, reranker_model_name):
        print(f"[INFO] Завантаження моделей...")
        self.encoder = SentenceTransformer(embedding_model_name)
        # Крос-енкодер для reranking
        self.reranker = CrossEncoder(reranker_model_name)
        self.documents = []
        self.tokenized_corpus = []
        self.bm25 = None
        self.index = None

    def build_indexes(self, corpus_path):
        print(f"[INFO] Читання корпусу з {corpus_path}...")
        self.documents = []
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.documents.append(json.loads(line))
        
        texts = [doc["text"] for doc in self.documents]
        
        # 1. Підготовка для BM25 (тократизація за пробілами)
        print("[INFO] Індексація BM25...")
        self.tokenized_corpus = [doc.lower().split() for doc in texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        
        # 2. Побудова FAISS індексу
        print("[INFO] Генерація ембедингів та побудова FAISS індексу...")
        embeddings = self.encoder.encode(texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexHNSWFlat(dimension, 32)
        self.index.hnsw.efSearch = 64
        self.index.add(embeddings)
        print("[INFO] Гібридні індекси успішно побудовано!")

    def search(self, query, top_k=5, rrf_k=60):
        t0 = time.time()
        
        # Семантичний пошук (FAISS)
        q_vec = self.encoder.encode([query]).astype("float32")
        distances, faiss_indices = self.index.search(q_vec, top_k * 2)
        
        faiss_ranking = {}
        for rank, idx in enumerate(faiss_indices[0]):
            if idx != -1:
                faiss_ranking[idx] = rank + 1

        # Лексичний пошук (BM25)
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_sorted_indices = np.argsort(bm25_scores)[::-1][:top_k * 2]
        
        bm25_ranking = {}
        for rank, idx in enumerate(bm25_sorted_indices):
            bm25_ranking[idx] = rank + 1

        # Комбінування через RRF (Reciprocal Rank Fusion)
        rrf_scores = {}
        all_indices = set(list(faiss_ranking.keys()) + list(bm25_ranking.keys()))
        
        for idx in all_indices:
            score = 0.0
            if idx in faiss_ranking:
                score += 1.0 / (rrf_k + faiss_ranking[idx])
            if idx in bm25_ranking:
                score += 1.0 / (rrf_k + bm25_ranking[idx])
            rrf_scores[idx] = score

        # Сортування за RRF скором
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        candidate_indices = [item[0] for item in sorted_rrf]
        
        # Reranking (Крос-енкодер)
        pairs = [[query, self.documents[idx]["text"]] for idx in candidate_indices]
        rerank_scores = self.reranker.predict(pairs)
        
        reranked_results = []
        for i, idx in enumerate(candidate_indices):
            reranked_results.append({
                "fragment_id": self.documents[idx]["fragment_id"],
                "text": self.documents[idx]["text"],
                "rrf_score": rrf_scores[idx],
                "rerank_score": float(rerank_scores[i])
            })
            
        # Фінальне сортування за оцінкою reranker
        reranked_results = sorted(reranked_results, key=lambda x: x["rerank_score"], reverse=True)
        
        latency = (time.time() - t0) * 1000
        return reranked_results, latency

if __name__ == "__main__":
    os.makedirs("src", exist_ok=True)
    
    # Ініціалізація рушія (використовуємо мультимовну модель та легкий крос-енкодер)
    engine = HybridSearchEngine(
        embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        reranker_model_name="BAAI/bge-reranker-base"
    )
    
    engine.build_indexes("data/corpus.jsonl")
    
    test_queries = [
        "вимоги до верстатів ЧПК та шпинделя",
        "безпека роботи програмованих контролерів ПЛК",
        "стандарти електрообладнання машин IEC"
    ]
    
    print("\n" + "="*80)
    print(f"{'Тестовий запит':<40} | {'Метод':<15} | {'Затримка (мс)':<15}")
    print("="*80)
    
    for q in test_queries:
        results, latency = engine.search(q, top_k=3)
        print(f"{q[:38]:<40} | {'Hybrid + Rerank':<15} | {latency:<15.2f}")
        print("--- Топ-1 результат: [{results[0]['fragment_id']}] (score: {results[0]['rerank_score']:.4f}) ---")
    print("="*80)
