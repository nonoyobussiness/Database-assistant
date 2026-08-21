import ollama
from chromadb.utils.embedding_functions import EmbeddingFunction
from config import EMBEDDING_MODEL


class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model=EMBEDDING_MODEL):
        self.model = model

    def __call__(self, input):
        return [
            ollama.embeddings(model=self.model, prompt=text)["embedding"]
            for text in input
        ]
