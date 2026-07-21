import sys, shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))

from generate_docs import write_pdf
from ingest import run_ingestion
from query import run_query

OUTPUT_LOG = BASE_DIR / "outputs" / "experiment_log.txt"
OUTPUT_LOG.parent.mkdir(parents=True, exist_ok=True)
CHROMA_DIR = BASE_DIR / "vectorstore"

class Tee:
    def __init__(self, filepath):
        self.file = open(filepath, "w")
        self.stdout = sys.stdout
    def write(self, data):
        self.stdout.write(data)
        self.file.write(data)
    def flush(self):
        self.stdout.flush()
        self.file.flush()

def main():
    # Clean vectorstore directory before starting test suite
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    sys.stdout = Tee(OUTPUT_LOG)
    print("=========================================================")
    print("  CSE 4531 RAG Security & Data Poisoning Lab Experiment  ")
    print("=========================================================\n")

    # Step 1: Generate documents
    print("[1] Generating PDF documents...")
    import generate_docs
    
    # Step 2: Phase 1 (Trusted Only)
    print("\n---------------------------------------------------------")
    print("  PHASE 1: Trusted Knowledge Base Evaluation")
    print("---------------------------------------------------------")
    run_ingestion(include_untrusted=False, collection_name="trusted_policies")
    run_query("How do employees reset passwords?", collection_name="trusted_policies")
    run_query("How is VPN access configured?", collection_name="trusted_policies")

    # Step 3: Phase 2 (Mixed Knowledge Base)
    print("\n---------------------------------------------------------")
    print("  PHASE 2: Mixed (Poisoned/Inconsistent) Evaluation")
    print("---------------------------------------------------------")
    run_ingestion(include_untrusted=True, collection_name="mixed_policies")
    run_query("How do employees reset passwords?", collection_name="mixed_policies")
    run_query("How is VPN access configured?", collection_name="mixed_policies")

    print("\n[✔] Experiment completed successfully! Log saved to outputs/experiment_log.txt")

if __name__ == "__main__":
    main()
