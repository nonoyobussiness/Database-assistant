# Central configuration — change model names, DB credentials, and paths here

# Database
DB_HOST = "localhost"
DB_NAME = "university_db"
DB_USER = "postgres"
DB_PASSWORD = "161279"

# Embedding model (Ollama)
EMBEDDING_MODEL = "hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest"

# LLM model (Ollama)
# Swapped to a smaller local model. Pull it first:
#   ollama pull qwen2.5:0.5b
# Alternative (smaller, but weaker at structured SQL generation):
#   ollama pull hf.co/HuggingFaceTB/SmolLM2-360M-Instruct-GGUF:latest
#   LLM_MODEL = "hf.co/HuggingFaceTB/SmolLM2-360M-Instruct-GGUF:latest"
LLM_MODEL = "phi4-mini:latest"

# ChromaDB
CHROMA_PATH = "./rag_db"
CHROMA_COLLECTION = "schema"