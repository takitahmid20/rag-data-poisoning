# Research Gap Analysis: Security & Data Poisoning in RAG Systems

**Course:** BSc Computer Security (CSE 4531) - Preliminary Literature Evaluation  
**Submission Date:** 21 July 2026  
**Focus Area:** Defensive Evaluation of Document Inconsistency, Poisoning, and Trust in Retrieval-Augmented Generation

---

## 1. Literature Review & Current State of Research

Recent studies such as **PoisonedRAG** (Zou et al., 2024) and **CorruptRAG** (2024-2025) demonstrate that malicious or inconsistent documents can successfully manipulate RAG outputs. Existing defenses mainly rely on document validation, keyword matching, metadata verification, and trust-based retrieval filtering. While these approaches reduce the success rate of direct attacks, several important challenges remain unresolved:

| Defense Category | Mechanism & Technique | Current Limitations |
| :--- | :--- | :--- |
| **Document Validation & Provenance** | Cryptographic hashing, digital signatures, and ACLs on source documents. | Hard to maintain across dynamic enterprise data lakes and unsigned uploads. |
| **Metadata Verification** | Filtering chunks by version tags or timestamp attributes during query. | Vulnerable to metadata spoofing or misconfigured ingestion pipelines. |
| **Trust-Based Filtering** | Assigning numerical trust coefficients to document repositories prior to ranking. | Static scores fail to detect fine-grained semantic contradictions within mixed files. |
| **Keyword Matching & Sanitization** | Heuristic regex matching for prompt injection tokens (e.g., `Ignore instructions`). | Easily bypassed by paraphrasing, synonym substitution, and encoding tricks. |
| **LLM Semantic Validation** | Using secondary LLMs or cross-encoders to verify context consistency. | High computational cost and latency ($>1.5\text{s}$), impractical for real-time systems. |

---

## 2. Remaining Open Research Challenges

1. **Obfuscated Instructions vs. Explicit Injections:** Most existing systems focus on explicit prompt injection, where malicious instructions are written clearly in the document. They often struggle to identify obfuscated instructions, such as hidden prompts encoded through sentence initials, Unicode characters, invisible text, or indirect language.
2. **Multilingual & Low-Resource Environments:** Current defenses primarily evaluate English documents. Very limited work investigates multilingual environments, especially low-resource languages like Bangla.
3. **High Latency of Pre/Post-Query Verification:** Many proposed defenses require expensive LLM-based verification for every retrieved document, significantly increasing latency and deployment cost in interactive QA systems.

---

## 3. Proposed Research Direction

To address these limitations, this project proposes to investigate:

> **"A lightweight document trust evaluation and sanitization framework capable of detecting malicious documents before indexing them into the vector database while supporting multilingual content."**

### Pre-Indexing Defense Concept:
```
[ Untrusted Document Corpus ] ──► [ Pre-Indexing Sanitization Layer ] ──► [ Chroma Vector DB ] ──► [ LLM ]
  • Multilingual (Bangla/English)   • Obfuscation & Keyword Detection
  • Pre-Indexing Validation         • Low-Latency Risk Scoring
```

Operating **pre-indexing** ensures malicious or inconsistent chunks are detected and quarantined before entering the persistent vector database, protecting RAG retrieval efficiency without adding heavy runtime query latency.
