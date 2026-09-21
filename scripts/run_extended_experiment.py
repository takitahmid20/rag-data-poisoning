"""Extended poisoning experiment: 15 trusted + 17 poisoned PDFs, 25 queries, 3 knowledge bases.

Phase 1  trusted-only KB            -> baseline retrieval accuracy
Phase 2  trusted + poisoned KB      -> how often poison reaches the top-k context
Phase 3  mixed KB after a content scanner at ingestion (defense) -> what still gets through

Outputs: outputs/extended_{log,results}_<model>.{txt,csv,md}
"""
import csv, os, re, shutil, sys, warnings
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))
from extended_dataset import TRUSTED, POISONED, QUERIES
from query import ask_llm
from embedding_config import embedding_model_name

DATA_DIR = BASE_DIR / "data" / "extended"
TRUSTED_DIR, POISON_DIR = DATA_DIR / "trusted", DATA_DIR / "poisoned"
OUT_DIR = BASE_DIR / "outputs"
TOP_K = 3
EMBEDDING_MODEL = embedding_model_name()
TAG = EMBEDDING_MODEL.split("/")[-1]
CHROMA_DIR = BASE_DIR / f"vectorstore_extended_{TAG}"
USE_LLM = bool(os.getenv("GEMINI_API_KEY")) and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"

POISON_TYPE = {name: atype for name, atype, *_ in POISONED}
POISON_MARKER = {name: marker for name, _, _, _, marker in POISONED}


# ---------- corpus ----------
def write_pdf(path: Path, title: str, lines: list[str]):
    c = canvas.Canvas(str(path))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, title)
    c.setFont("Helvetica", 10)
    y = 720
    for line in lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()


def generate_corpus():
    for d in (TRUSTED_DIR, POISON_DIR):
        d.mkdir(parents=True, exist_ok=True)
    for name, title, lines in TRUSTED:
        write_pdf(TRUSTED_DIR / f"{name}.pdf", title, lines)
    for name, _, title, lines, _ in POISONED:
        write_pdf(POISON_DIR / f"{name}.pdf", title, lines)
    print(f"[+] Generated {len(TRUSTED)} trusted PDFs in {TRUSTED_DIR.relative_to(BASE_DIR)}")
    print(f"[+] Generated {len(POISONED)} poisoned PDFs in {POISON_DIR.relative_to(BASE_DIR)}")


def load_docs(folder: Path, label: str) -> list[Document]:
    docs = []
    for pdf in sorted(folder.glob("*.pdf")):
        text = "\n".join(p.page_content for p in PyPDFLoader(str(pdf)).load())
        docs.append(Document(page_content=text, metadata={"source": pdf.stem, "label": label}))
    return docs


# ---------- defense: ingestion-time content scanner ----------
SCAN_RULES = {
    "prompt_injection": r"ignore (all )?previous|disregard|\[system\]|system note|assistant instruction",
    "authority_claim": r"supersedes|overrides|replaces all previous|is retired",
    "insecure_http": r"http://",
    "security_weakening": r"does not require|without mfa|mfa has been removed|plain text|not encrypted|"
                          r"unencrypted|no approval|no receipts|are now approved|public links",
}
DOMAIN_RE = re.compile(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|co|io|help)\b", re.I)
ALLOWED_DOMAIN = ("securecorp.com",)


def scan(text: str) -> list[str]:
    hits = [rule for rule, pat in SCAN_RULES.items() if re.search(pat, text, re.I)]
    external = [m.group(0) for m in DOMAIN_RE.finditer(text) if not m.group(0).lower().endswith(ALLOWED_DOMAIN)]
    if external:
        hits.append("external_domain")
    return hits


# ---------- retrieval ----------
def build_kb(name: str, docs: list[Document], emb) -> Chroma:
    return Chroma.from_documents(docs, emb, persist_directory=str(CHROMA_DIR), collection_name=name)


def evaluate(kb_name: str, db: Chroma, rows: list, log):
    log(f"\n{'=' * 70}\n  KNOWLEDGE BASE: {kb_name}\n{'=' * 70}")
    for question, expected, targets in QUERIES:
        results = db.similarity_search_with_score(question, k=TOP_K)
        sources = [d.metadata["source"] for d, _ in results]
        labels = [d.metadata["label"] for d, _ in results]
        poison_ranks = [i + 1 for i, l in enumerate(labels) if l == "poisoned"]
        context = "".join(f"[{d.metadata['source']}]: {d.page_content}\n" for d, _ in results)

        answer_poisoned = ""
        if USE_LLM:
            answer = ask_llm(context, question)
            answer_poisoned = any(POISON_MARKER[s].lower() in answer.lower() for s in sources if s in POISON_MARKER)
        log(f"\nQ: {question}")
        for i, (d, score) in enumerate(results, 1):
            tag = "POISON" if d.metadata["label"] == "poisoned" else "trusted"
            log(f"   [{i}] {tag:7} {d.metadata['source']:28} dist={score:.4f}")
        if USE_LLM:
            log(f"   LLM answer used poisoned info: {answer_poisoned}")
            log(f"   A: {answer[:300]}")

        rows.append({
            "kb": kb_name,
            "question": question,
            "expected_trusted": expected,
            "targeted_by": ";".join(targets),
            "top_sources": ";".join(sources),
            "trusted_at_rank1": sources[0] == expected,
            "trusted_in_topk": expected in sources,
            "poison_in_topk": bool(poison_ranks),
            "poison_at_rank1": 1 in poison_ranks,
            "poison_types": ";".join(sorted({POISON_TYPE[s] for s in sources if s in POISON_TYPE})),
            "answer_poisoned": answer_poisoned if USE_LLM else "n/a",
        })


# ---------- reporting ----------
def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "-"


def summarize(rows, scan_report, log) -> str:
    md = ["# Extended Poisoning Experiment Results", "",
          f"- Corpus: **{len(TRUSTED)} trusted** + **{len(POISONED)} poisoned** PDFs",
          f"- Queries: **{len(QUERIES)}** ({sum(1 for q in QUERIES if q[2])} targeted, "
          f"{sum(1 for q in QUERIES if not q[2])} control)",
          f"- Retrieval: {EMBEDDING_MODEL}, ChromaDB, top-k = {TOP_K}",
          f"- LLM answer check: {'Gemini' if USE_LLM else 'not run (no GEMINI_API_KEY) - retrieval-level metrics only'}",
          "", "## 1. Retrieval metrics per knowledge base", "",
          "| Knowledge base | Trusted doc rank 1 | Trusted doc in top-3 | Poison in top-3 | Poison at rank 1 |",
          "|---|---|---|---|---|"]
    for kb in dict.fromkeys(r["kb"] for r in rows):
        rs = [r for r in rows if r["kb"] == kb]
        n = len(rs)
        md.append(f"| {kb} | {pct(sum(r['trusted_at_rank1'] for r in rs), n)} | "
                  f"{pct(sum(r['trusted_in_topk'] for r in rs), n)} | "
                  f"{pct(sum(r['poison_in_topk'] for r in rs), n)} | "
                  f"{pct(sum(r['poison_at_rank1'] for r in rs), n)} |")
    if USE_LLM:
        md += ["", "| Knowledge base | LLM answer repeated poisoned info |", "|---|---|"]
        for kb in dict.fromkeys(r["kb"] for r in rows):
            rs = [r for r in rows if r["kb"] == kb]
            md.append(f"| {kb} | {pct(sum(r['answer_poisoned'] is True for r in rs), len(rs))} |")

    # success per attack type (mixed KB): did the targeting poison doc reach top-3 / rank 1?
    md += ["", "## 2. Attack success by type (mixed KB, per targeted query)", "",
           "| Attack type | Targeted query pairs | Reached top-3 | Reached rank 1 |", "|---|---|---|---|"]
    stats = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r["kb"] != "2_mixed":
            continue
        top = r["top_sources"].split(";")
        for t in filter(None, r["targeted_by"].split(";")):
            s = stats[POISON_TYPE[t]]
            s[0] += 1
            s[1] += t in top
            s[2] += top[0] == t
    for atype, (n, k, r1) in sorted(stats.items(), key=lambda x: -x[1][1] / x[1][0]):
        md.append(f"| {atype} | {n} | {pct(k, n)} | {pct(r1, n)} |")

    # scanner
    tp = sum(1 for s in scan_report if s["label"] == "poisoned" and s["flags"])
    fn = sum(1 for s in scan_report if s["label"] == "poisoned" and not s["flags"])
    fp = sum(1 for s in scan_report if s["label"] == "trusted" and s["flags"])
    md += ["", "## 3. Defense: ingestion-time content scanner", "",
           f"- Poisoned docs blocked (recall): **{tp}/{tp + fn} = {pct(tp, tp + fn)}**",
           f"- Trusted docs wrongly blocked (false positives): **{fp}/{len(TRUSTED)}**",
           f"- Precision: **{pct(tp, tp + fp)}**", "",
           "| Document | Truth | Attack type | Scanner flags |", "|---|---|---|---|"]
    for s in scan_report:
        md.append(f"| {s['source']} | {s['label']} | {POISON_TYPE.get(s['source'], '-')} | "
                  f"{', '.join(s['flags']) or 'passed'} |")
    missed = [s["source"] for s in scan_report if s["label"] == "poisoned" and not s["flags"]]
    md += ["", f"Poison that evaded the scanner: {', '.join(missed) or 'none'}. "
           "These are fact-level contradictions with no suspicious keywords, URLs or instructions - "
           "keyword/regex defenses cannot catch them; provenance (trusted-source) filtering or "
           "cross-document consistency checking is needed."]

    md += ["", "## 4. Per-query detail (mixed KB)", "",
           "| Question | Top-3 sources | Poison in top-3 | Poison rank 1 |", "|---|---|---|---|"]
    for r in rows:
        if r["kb"] == "2_mixed":
            md.append(f"| {r['question']} | {r['top_sources'].replace(';', ', ')} | "
                      f"{'YES' if r['poison_in_topk'] else 'no'} | {'YES' if r['poison_at_rank1'] else 'no'} |")
    text = "\n".join(md) + "\n"
    log("\n" + text)
    return text


def main():
    OUT_DIR.mkdir(exist_ok=True)
    log_file = open(OUT_DIR / f"extended_log_{TAG}.txt", "w")

    def log(msg=""):
        print(msg)
        log_file.write(msg + "\n")

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    generate_corpus()
    trusted = load_docs(TRUSTED_DIR, "trusted")
    poisoned = load_docs(POISON_DIR, "poisoned")
    emb = SentenceTransformerEmbeddings(model_name=EMBEDDING_MODEL)

    scan_report = [{"source": d.metadata["source"], "label": d.metadata["label"], "flags": scan(d.page_content)}
                   for d in trusted + poisoned]
    defended = [d for d, s in zip(trusted + poisoned, scan_report) if not s["flags"]]

    rows = []
    evaluate("1_trusted_only", build_kb("ext_trusted", trusted, emb), rows, log)
    evaluate("2_mixed", build_kb("ext_mixed", trusted + poisoned, emb), rows, log)
    evaluate("3_mixed_plus_scanner", build_kb("ext_defended", defended, emb), rows, log)

    with open(OUT_DIR / f"extended_results_{TAG}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (OUT_DIR / f"extended_results_{TAG}.md").write_text(summarize(rows, scan_report, log))
    log(f"[+] Saved outputs/extended_log_{TAG}.txt, extended_results_{TAG}.csv, extended_results_{TAG}.md")
    log_file.close()


if __name__ == "__main__":
    main()
