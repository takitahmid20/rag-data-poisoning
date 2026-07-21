import os, argparse, warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress library deprecation warnings for clean terminal output
warnings.filterwarnings("ignore")

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
CHROMA_DIR = BASE_DIR / "vectorstore"

def ask_llm(context: str, question: str) -> str:
    prompt = f"Use ONLY the policy context below to answer.\n\nContext:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        return genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt).text.strip()
    
    return f"[LLM Simulation Response based on context]:\n" + "\n".join([f"- {line}" for line in context.split("\n") if line.strip()])

def run_query(question: str, top_k: int = 3, collection_name: str = "trusted_policies"):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings, collection_name=collection_name)
    
    results = db.similarity_search_with_score(question, k=top_k)
    
    context_str = ""
    print(f"\n=== QUESTION: {question} ===")
    print(f"--- RETRIEVED TOP-{top_k} CHUNKS (Collection: {collection_name}) ---")
    for idx, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        print(f"[{idx}] {source} (Distance: {score:.4f}): {doc.page_content}")
        context_str += f"[{source}]: {doc.page_content}\n"

    print("\n--- GENERATED ANSWER ---")
    answer = ask_llm(context_str, question)
    print(answer)
    print("=" * 45)
    return results, answer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", "-q", default="How is VPN access configured?")
    parser.add_argument("--collection", default="trusted_policies")
    args = parser.parse_args()
    run_query(args.question, collection_name=args.collection)
