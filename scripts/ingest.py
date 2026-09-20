import argparse, warnings
from pathlib import Path

# Suppress library deprecation warnings for clean terminal output
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma

from embedding_config import embedding_model_name
from security_gate import evaluate_document

BASE_DIR = Path(__file__).resolve().parent.parent
TRUSTED_DIR = BASE_DIR / "data" / "trusted"
UNTRUSTED_DIR = BASE_DIR / "data" / "untrusted"
CHROMA_DIR = BASE_DIR / "vectorstore"

def run_ingestion(
    include_untrusted: bool = False,
    collection_name: str = None,
    defend: bool = False,
):
    if collection_name is None:
        collection_name = "mixed_policies" if include_untrusted else "trusted_policies"

    pdf_files = list(TRUSTED_DIR.glob("*.pdf"))
    if include_untrusted:
        pdf_files += list(UNTRUSTED_DIR.glob("*.pdf"))

    docs = []
    quarantined = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        loaded = loader.load()
        decision = evaluate_document(
            pdf_path, "\n".join(document.page_content for document in loaded)
        )
        if defend and not decision.accepted:
            quarantined.append((pdf_path.name, decision))
            continue
        for d in loaded:
            d.metadata["source"] = pdf_path.name
        docs.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_documents(docs)

    embeddings = SentenceTransformerEmbeddings(model_name=embedding_model_name())
    
    # Overwrite / create collection cleanly
    db = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings, collection_name=collection_name)
    
    # Reset collection contents if re-ingesting
    try:
        db.delete_collection()
    except Exception:
        pass

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=collection_name
    )
    print(
        f"[+] Ingested {len(pdf_files) - len(quarantined)} PDF(s) into Chroma collection "
        f"'{collection_name}' using {embedding_model_name()}."
    )
    for filename, decision in quarantined:
        print(f"[!] Quarantined {filename} (score={decision.score:.2f}): {'; '.join(decision.reasons)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-untrusted", action="store_true")
    parser.add_argument("--defend", action="store_true", help="quarantine risky documents before indexing")
    parser.add_argument("--collection", default=None)
    args = parser.parse_args()
    run_ingestion(
        include_untrusted=args.include_untrusted,
        collection_name=args.collection,
        defend=args.defend,
    )
