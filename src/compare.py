  import os
  import time
  import json
  import numpy as np
  import faiss
  from sentence_transformers import SentenceTransformer

  def benchmark_model(model_name, corpus_path, test_queries):
      print(f"\n[INFO] Тестування моделі: {model_name}...")
      
      # 1. Завантаження моделі
      start_load = time.time()
      encoder = SentenceTransformer(model_name)
      load_time = time.time() - start_load
      print(f"[INFO] Модель завантажено за {load_time:.2f} сек.")
      
      # 2. Читання корпусу
      documents = []
      with open(corpus_path, "r", encoding="utf-8") as f:
          for line in f:
              if line.strip():
                  documents.append(json.loads(line))
      texts = [doc["text"] for doc in documents]
      
      # 3. Побудова індексу та вимірювання часу
      print("[INFO] Генерація ембедингів та побудова FAISS індексу...")
      start_build = time.time()
      embeddings = encoder.encode(texts, show_progress_bar=False)
      embeddings = np.array(embeddings).astype("float32")
      
      dimension = embeddings.shape[1]
      index = faiss.IndexHNSWFlat(dimension, 32)
      index.hnsw.efSearch = 64
      index.add(embeddings)
      build_time = time.time() - start_build
      print(f"[RESULT] Індекс побудовано за {build_time:.4f} сек.")
      
      # 4. Вимірювання затримки пошуку (Latency) на тестових запитах
      latencies = []
      for q in test_queries:
          t0 = time.time()
          q_vec = encoder.encode([q]).astype("float32")
          index.search(q_vec, k=5)
          latency = (time.time() - t0) * 1000
          latencies.append(latency)
          
      avg_latency = sum(latencies) / len(latencies)
      
      return {
          "model": model_name,
          "build_time": build_time,
          "avg_latency": avg_latency
      }

  if __name__ == "__main__":
      os.makedirs("src", exist_ok=True)
      
      corpus_file = "data/corpus.jsonl"
      queries = [
          "вимоги до верстатів ЧПК",
          "частота обертання шпинделя",
          "параметри безпеки ПЛК",
          "робочі характеристики обладнання"
      ]
      
      models_to_test = [
          "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
          "sentence-transformers/all-MiniLM-L6-v2"
      ]
      
      results = []
      for m in models_to_test:
          res = benchmark_model(m, corpus_file, queries)
          results.append(res)
          
      # Виведення наочної таблиці результатів у консоль
      print("\n" + "="*85)
      print(f"{'Модель Embeddings':<55} | {'Час побудови (сек)':<18} | {'Сер. затримка (мс)':<18}")
      print("="*85)
      for r in results:
          print(f"{r['model']:<55} | {r['build_time']:<18.4f} | {r['avg_latency']:<18.2f}")
      print("="*85)
