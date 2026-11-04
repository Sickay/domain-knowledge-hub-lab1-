import json

def chunk_fixed_size(text, chunk_size=100, overlap=20):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def chunk_by_structure(document_text):
    # Стратегія 2: Розбиття за розділами або структурою документа
    sections = document_text.split("Розділ")
    chunks = [s.strip() for s in sections if s.strip()]
    return chunks

def chunk_semantic_blocks(document_text, max_length=150):
    # Стратегія 3: Ієрархічне/семантичне групування за реченнями
    sentences = document_text.split(". ")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

if __name__ == "__main__":
    print("Модуль стратегій chunking успішно завантажено!")
