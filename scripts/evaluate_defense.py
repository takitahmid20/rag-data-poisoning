import argparse
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

from embedding_config import embedding_model_name
from ingest import run_ingestion


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "vectorstore"


def contamination_rate(collection_name: str, questions: list[str], top_k: int) -> float:
    embeddings = SentenceTransformerEmbeddings(model_name=embedding_model_name())
    db = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    contaminated = 0
    for question in questions:
        results = db.similarity_search(question, k=top_k)
        if any(document.metadata.get("source") == "outdated_vpn_policy.pdf" for document in results):
            contaminated += 1
    return contaminated / len(questions)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    questions = [
        "How do employees reset passwords?",
        "How is VPN access configured?",
    ]
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    run_ingestion(include_untrusted=True, collection_name="mixed_policies")
    mixed_rate = contamination_rate("mixed_policies", questions, args.top_k)
    run_ingestion(
        include_untrusted=True,
        collection_name="defended_policies",
        defend=True,
    )
    defended_rate = contamination_rate("defended_policies", questions, args.top_k)

    print(f"embedding_model={embedding_model_name()}")
    print(f"mixed_contamination_rate={mixed_rate:.2%}")
    print(f"defended_contamination_rate={defended_rate:.2%}")
    print(f"absolute_reduction={(mixed_rate - defended_rate):.2%}")


if __name__ == "__main__":
    main()