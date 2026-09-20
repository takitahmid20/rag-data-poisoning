import argparse
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

from embedding_config import embedding_model_name
from ingest import run_ingestion
from evaluation_cases import EVALUATION_CASES


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "vectorstore"


def evaluate_collection(collection_name: str, top_k: int) -> list[dict]:
    embeddings = SentenceTransformerEmbeddings(model_name=embedding_model_name())
    db = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    evaluations = []
    for case in EVALUATION_CASES:
        results = db.similarity_search_with_score(case["question"], k=top_k)
        sources = [document.metadata.get("source") for document, _ in results]
        untrusted_rank = next((index + 1 for index, source in enumerate(sources) if source == "outdated_vpn_policy.pdf"), None)
        trusted_topic_hit = any(case["topic"] in (source or "") for source in sources)
        evaluations.append({
            **case,
            "contaminated": untrusted_rank is not None,
            "untrusted_rank": untrusted_rank,
            "trusted_topic_hit": trusted_topic_hit,
            "sources": sources,
        })
    return evaluations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    run_ingestion(include_untrusted=True, collection_name="mixed_policies")
    mixed_evaluations = evaluate_collection("mixed_policies", args.top_k)
    run_ingestion(
        include_untrusted=True,
        collection_name="defended_policies",
        defend=True,
    )
    defended_evaluations = evaluate_collection("defended_policies", args.top_k)

    mixed_rate = sum(case["contaminated"] for case in mixed_evaluations) / len(mixed_evaluations)
    defended_rate = sum(case["contaminated"] for case in defended_evaluations) / len(defended_evaluations)
    mixed_topic_hit = sum(case["trusted_topic_hit"] for case in mixed_evaluations) / len(mixed_evaluations)
    defended_topic_hit = sum(case["trusted_topic_hit"] for case in defended_evaluations) / len(defended_evaluations)

    print(f"embedding_model={embedding_model_name()}")
    print(f"mixed_contamination_rate={mixed_rate:.2%}")
    print(f"defended_contamination_rate={defended_rate:.2%}")
    print(f"absolute_reduction={(mixed_rate - defended_rate):.2%}")
    print(f"mixed_trusted_topic_hit={mixed_topic_hit:.2%}")
    print(f"defended_trusted_topic_hit={defended_topic_hit:.2%}")
    print("case_results:")
    for mixed, defended in zip(mixed_evaluations, defended_evaluations):
        print(
            f"  {mixed['id']}: mixed_contaminated={mixed['contaminated']} "
            f"mixed_untrusted_rank={mixed['untrusted_rank']} "
            f"defended_contaminated={defended['contaminated']}"
        )

    output_path = BASE_DIR / "outputs" / "expanded_evaluation.txt"
    output_path.write_text(
        "\n".join(
            [
                f"embedding_model={embedding_model_name()}",
                f"cases={len(mixed_evaluations)}",
                f"top_k={args.top_k}",
                f"mixed_contamination_rate={mixed_rate:.2%}",
                f"defended_contamination_rate={defended_rate:.2%}",
                f"absolute_reduction={(mixed_rate - defended_rate):.2%}",
                f"mixed_trusted_topic_hit={mixed_topic_hit:.2%}",
                f"defended_trusted_topic_hit={defended_topic_hit:.2%}",
            ]
            + [
                f"{case['id']}: mixed={case['contaminated']} rank={case['untrusted_rank']} defended={defended['contaminated']}"
                for case, defended in zip(mixed_evaluations, defended_evaluations)
            ]
        )
        + "\n"
    )


if __name__ == "__main__":
    main()