# Research Gap Analysis: Security & Data Poisoning in RAG Systems

**Course:** BSc Computer Security (CSE 4531) - Preliminary Literature Evaluation  
**Submission Date:** 21 July 2026  
**Focus Area:** Defensive Evaluation of Document Inconsistency, Poisoning, and Trust in Retrieval-Augmented Generation

---

## 1. Literature Review & Current State of Research

Recent literature (2023–2026) highlights that Retrieval-Augmented Generation (RAG) architectures significantly expand the attack surface of Large Language Models (LLMs):

- **PoisonedRAG (Zou et al., 2024):** Demonstrates that injecting a tiny fraction of adversarial text chunks into a knowledge base can deterministically manipulate LLM outputs across targeted queries without modifying model weights.
- **CorruptRAG & Knowledge Poisoning (2024–2025):** Explores how document conflicts, outdated policies, and indirect prompt injections degrade retrieval quality, leading to hallucination, credential theft, and unauthorized command execution.
- **Indirect Prompt Injection (Greshake et al., 2023; Liu et al., 2025):** Documents how adversarial instructions embedded within retrieved context hijack LLM control flow.

---

## 2. Existing Defensive Approaches & Limitations

| Defense Category | Mechanism & Technique | Current Limitations |
| :--- | :--- | :--- |
| **Document Provenance** | Cryptographic hashing, digital signatures, and ACLs on source documents. | Hard to maintain across dynamic enterprise data lakes. |
| **Metadata Validation** | Filtering chunks by version tags or timestamp attributes during query. | Vulnerable to metadata spoofing or ingestion pipeline bypass. |
| **Trust Scoring** | Assigning numerical trust coefficients to document repositories prior to ranking. | Static scores fail to catch subtle semantic contradictions in mixed files. |
| **Retrieval Filtering** | Top-K similarity thresholds and anomaly detection on vector distributions. | High false-positive rate; fails when untrusted chunks match query closely. |
| **Content Sanitization** | Heuristic regex matching for prompt injection tokens (e.g. `Ignore instructions`). | Easily bypassed by paraphrasing and encoding variations. |
| **Semantic Validation** | Using secondary LLMs or cross-encoders to verify context consistency. | High latency ($>1.5\text{s}$) and computational cost. |

---

## 3. Remaining Open Research Challenges

1. **Multilingual RAG Defenses:** Existing filters target English; translated or code-switched adversarial text bypasses rule-based checks.
2. **Obfuscated Manipulation:** Paraphrased or zero-width text evasions preserve high vector similarity while avoiding heuristic blocks.
3. **Dynamic Unsigned Sources:** Enterprise workflows ingest unsigned web scrapes, PDF conversions, and user uploads where cryptographically verified provenance is unavailable.
4. **Computational Efficiency:** Heavy runtime validation adds impractically high latency to interactive QA systems.

---

## 4. Proposed Future Direction

To bridge the gap between fragile heuristic filtering and high-latency LLM verification, this preliminary evaluation points toward:

> **"A lightweight document trust evaluation and sanitization layer before vector database indexing."**

### Pre-Indexing Defense Concept:
```
[ Untrusted Document Corpus ] ──► [ Pre-Indexing Sanitization Layer ] ──► [ Chroma Vector DB ] ──► [ LLM ]
                                  • Structural & Version Verification
                                  • Conflict & Deprecation Filtering
                                  • Provenance Tagging
```
Operating **pre-indexing** ensures untrusted or outdated chunks are flagged or filtered before entering the persistent vector database, protecting RAG retrieval without adding runtime query latency.
