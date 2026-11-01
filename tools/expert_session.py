import json
import os
import sys
from datetime import datetime
from pydantic import ValidationError
from schemas.claim import ExpertAnswer


def log_interaction(model_name, prompt_id, raw_output, parsed_output, retry_count):
    os.makedirs("llm_log", exist_ok=True)
    log_entry = {
        "date": datetime.now().isoformat(),
        "model": model_name,
        "params": {"temperature": 0.2, "seed": 42},
        "prompt_id": prompt_id,
        "retry_count": retry_count,
        "raw_output": raw_output,
        "parsed_output": parsed_output
    }
    filename = f"llm_log/{prompt_id}_{int(datetime.now().timestamp())}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
    print(f"[LOG] Успішно записано журнал у {filename}")


def run_session_with_retry(prompt_id, mock_raw_response, model_name="GPT-4o"):
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            raw_data = json.loads(mock_raw_response)
            validated = ExpertAnswer(**raw_data)
            print(f"[OK] Схема успішно валідована з спроби {attempt + 1}")
            log_interaction(model_name, prompt_id, mock_raw_response, validated.model_dump(), attempt)
            return validated
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"[WARN] Помилка валідації на спробі {attempt + 1}: {e}")
            if attempt == max_retries:
                print("[ERROR] Досягнуто ліміту повторів (2).")
                sys.exit(1)


if __name__ == "__main__":
    sample_json = '''{
      "session_id": "SESS-001",
      "model_name": "GPT-4o",
      "claims": [
        {
          "id": "CLM-001",
          "statement": "Рівень мастила в гідросистемі перевіряється щозміни.",
          "kind": "правило",
          "sources": ["ISO 4413"],
          "confidence": 0.95,
          "scope": "Верстати ЧПК",
          "condition": "Рівень нижче норми",
          "action": "Блокувати запуск"
        }
      ]
    }'''
    run_session_with_retry("01_glossary", sample_json)
