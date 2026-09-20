# Data Poisoning and Prompt Injection Risks in Retrieval-Augmented Generation (RAG) Systems: A Preliminary Security Evaluation

**Course:** BSc Computer Security (CSE 4531)  
**Milestone:** Preliminary Research Submission (21 July 2026)  
**Environment:** Defensive Security Laboratory Evaluation  

---

## 📌 Abstract & Research Overview

This repository contains a concise, reproducible Retrieval-Augmented Generation (RAG) security experiment built for undergraduate Computer Security research. The objective is to evaluate how dense vector retrieval engines (`ChromaDB` + `SentenceTransformers`) respond when a knowledge base contains inconsistent or untrusted corporate policies.

Through empirical evaluation, this project demonstrates that vector search engines retrieve content based strictly on semantic similarity without evaluating document authority or provenance. This vulnerability allows untrusted directives to pollute the LLM context window.

## Presentation

- `RAG-Security-ANIMATED.html` — updated presentation covering objectives, methodology, experimental evidence, limitations, planned improvements, and source code.
- `RAG-Security-Deck.pdf` — exported presentation deck.

## Threat Model Boundary

The current experiment uses one outdated or inconsistent policy document as a retrieval-contamination proxy. It demonstrates that similarity-based retrieval can promote an untrusted document into the Top-K context, but it is not yet a full adversarial PoisonedRAG-style passage-generation benchmark. Future work should evaluate crafted poisoning passages and indirect prompt-injection content separately, with explicit attack-success and false-positive metrics.

The implemented pre-index gate can be tested with `python3 scripts/ingest.py --include-untrusted --defend`. It quarantines non-trusted sources and documents containing suspicious instructions or unsafe links before embedding. Run `python3 scripts/evaluate_defense.py` for mixed-versus-defended Top-K contamination rates. The project now uses `BAAI/bge-m3` as its default multilingual embedding model.

---

## 📁 Repository Structure

```
data_poisoning/
├── data/
│   ├── trusted/             # 5 official policy PDFs (Password, VPN, MFA, Leave, Security)
│   └── untrusted/           # 1 inconsistent policy PDF (Legacy VPN)
├── scripts/
│   ├── generate_docs.py     # PDF generation script (~40 lines)
│   ├── ingest.py            # PDF loading & Chroma vector indexing (~40 lines)
│   ├── query.py             # Context retrieval & LLM response script (~45 lines)
│   └── run_experiment.py    # One-click automated lab runner (~45 lines)
├── outputs/
│   └── experiment_log.txt   # Automated execution log output
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
├── README.md                # Submission guide
├── experiment_result.md     # Comparative experimental results
└── gap_analysis.md          # One-page research gap analysis
```

---

## ⚙️ Quickstart & Execution Guide

### 1. Install Dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 2. Configure API Key (Optional)
Copy `.env.example` to `.env` and set your Gemini API key:
```bash
cp .env.example .env
```
*(If no API key is set, the script executes using a deterministic context synthesis fallback for offline testing).*

### 3. Run Automated Evaluation
Execute the entire lab experiment with a single command:
```bash
python3 scripts/run_experiment.py
```

---

## 🧪 Manual Phase-by-Phase Execution

If you prefer running individual pipeline steps manually:

```bash
# Step 1: Generate PDF corpus
python3 scripts/generate_docs.py

# Step 2: Phase 1 (Trusted Only)
python3 scripts/ingest.py
python3 scripts/query.py -q "How is VPN access configured?"

# Step 3: Phase 2 (Mixed Knowledge Base)
python3 scripts/ingest.py --include-untrusted
python3 scripts/query.py -q "How is VPN access configured?"
```

---

## 📝 Milestone Submission Deliverables

- [`experiment_result.md`](file:///Volumes/TakiTahmid/UIU/CS/data_poisoning/experiment_result.md): Empirical report with Phase 1 vs. Phase 2 retrieval tables and analysis.
- [`gap_analysis.md`](file:///Volumes/TakiTahmid/UIU/CS/data_poisoning/gap_analysis.md): One-page research gap analysis referencing *PoisonedRAG* (Zou et al. 2024), *CorruptRAG*, and pre-indexing defenses.
- [`outputs/experiment_log.txt`](file:///Volumes/TakiTahmid/UIU/CS/data_poisoning/outputs/experiment_log.txt): Execution log output.
