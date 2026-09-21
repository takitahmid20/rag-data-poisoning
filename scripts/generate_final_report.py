"""Build final_rag_security_report.pdf with the extended benchmark results and figures.

Run after run_extended_experiment.py (both models) and make_charts.py.
"""
import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

BASE_DIR = Path(__file__).resolve().parent.parent
FIG = BASE_DIR / "outputs" / "figures"
PDF_PATH = BASE_DIR / "final_rag_security_report.pdf"
S = json.loads((FIG / "summary.json").read_text())

PRIMARY = colors.HexColor("#1c5cab")
INK = colors.HexColor("#1a202c")
MUTED = colors.HexColor("#52514e")
LINE = colors.HexColor("#cbd5e0")
BG = colors.HexColor("#f4f7fb")

ss = getSampleStyleSheet()
title = ParagraphStyle("t", parent=ss["Title"], fontSize=17, leading=21, textColor=PRIMARY, spaceAfter=2)
subtitle = ParagraphStyle("st", parent=ss["Normal"], fontSize=10, leading=13, alignment=1, textColor=MUTED)
h1 = ParagraphStyle("h1", parent=ss["Heading2"], fontSize=12.5, leading=15, textColor=PRIMARY, spaceBefore=8, spaceAfter=3, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=ss["Heading3"], fontSize=10.5, leading=13, textColor=INK, spaceBefore=5, spaceAfter=2)
body = ParagraphStyle("b", parent=ss["Normal"], fontSize=9, leading=12.2, textColor=INK, spaceAfter=4, alignment=4)
cell = ParagraphStyle("c", parent=body, fontSize=8, leading=10, spaceAfter=0, alignment=0)
head = ParagraphStyle("hd", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
cap = ParagraphStyle("cap", parent=body, fontSize=7.8, leading=10, textColor=MUTED, alignment=1, spaceAfter=6)
code = ParagraphStyle("code", parent=body, fontName="Courier", fontSize=7.8, leading=10, alignment=0, backColor=BG,
                      borderPadding=4, spaceBefore=2, spaceAfter=6)


def table(rows, widths, highlight_rows=()):
    data = [[Paragraph(str(c), head) for c in rows[0]]] + [[Paragraph(str(c), cell) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), PRIMARY), ("GRID", (0, 0), (-1, -1), 0.4, LINE),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2.5),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG])]
    for r in highlight_rows:
        style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fdebe3")))
    t.setStyle(TableStyle(style))
    return t


def figure(name, caption, width=165, heading=None):
    path = FIG / f"{name}.png"
    pw, ph = PILImage.open(path).size
    img = Image(str(path), width=width * mm, height=width * mm * ph / pw)
    return KeepTogether(([heading] if heading else []) + [img, Paragraph(caption, cap)])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "CSE 4531 | Group 06 | Summer 2026")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def pct(v):
    return f"{v:.0f}%"


def main():
    m = S["models"]
    bge, mini = m.get("BGE-M3"), m.get("MiniLM-L6-v2")
    p = m[S["primary_model"]]
    sc = S["scanner"]
    at = p["attack_types"]
    kb_t, kb_m, kb_s = p["1_trusted_only"], p["2_mixed"], p["3_mixed_plus_scanner"]
    recall = 100 * sc["blocked"] / sc["poisoned"]

    st = []
    st += [Paragraph("Comprehensive RAG Security Evaluation Report", title),
           Paragraph("Document Poisoning, Indirect Prompt Injection, and Pre-Index Defenses &mdash; "
                     "with an Extended 32-Document Multi-Attack Benchmark", subtitle), Spacer(1, 4),
           Paragraph("Taki Tahmid (011222172) | Jakaria Molla (011222245) | Easmin Akter Tule (011222177) | "
                     "Pranto Shahriar Bishal (011222285)<br/>CSE 4531 Computer Security, Section C | "
                     "United International University | Group 06", subtitle), Spacer(1, 8)]

    exec_box = Table([[Paragraph(
        f"<b>Executive result.</b> We extended the benchmark from 6 documents to <b>{sc['trusted']} trusted + "
        f"{sc['poisoned']} poisoned PDFs</b> (5 attack types) and <b>25 questions</b>. Without defense, poisoned text "
        f"reached the top-3 for <b>{pct(kb_m['poison_in_topk'])}</b> of questions and ranked first for "
        f"<b>{pct(kb_m['poison_at_rank1'])}</b> ({S['primary_model']}); the correct policy ranked first only "
        f"<b>{pct(kb_m['trusted_at_rank1'])}</b> of the time vs <b>{pct(kb_t['trusted_at_rank1'])}</b> on the clean corpus. "
        f"A content-only scanner blocked <b>{sc['blocked']}/{sc['poisoned']}</b> poisoned docs with "
        f"<b>{sc['false_positives']}</b> false alarms but still left <b>{pct(kb_s['poison_in_topk'])}</b> of questions "
        f"contaminated. Only the provenance (trusted-source) gate brought contamination to <b>0%</b>. "
        f"The earlier 10-question gate result (40% &rarr; 0%) is retained in Section 5. All results are retrieval-level "
        f"and synthetic, not a universal security guarantee.", body)]], colWidths=[174 * mm])
    exec_box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BG), ("BOX", (0, 0), (-1, -1), 0.8, PRIMARY),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                                  ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    st += [exec_box]

    st += [Paragraph("1. Objectives and Research Questions", h1), Paragraph(
        "The project (1) models RAG document-contamination threats, (2) defends the ingestion boundary with a "
        "lightweight pre-index gate, (3) isolates suspicious documents in quarantine instead of deleting them, and "
        "(4) measures contamination and trade-offs. The research questions are: <b>RQ1</b> can an untrusted document "
        "enter the top-3 context? <b>RQ2</b> does a pre-index gate prevent it? <b>RQ3</b> with many poisoned documents of "
        "different types, how often does poison reach the top-3 or rank first, and which types are strongest? "
        "<b>RQ4</b> how much can a content-only scanner remove compared with a provenance rule, and at what "
        "false-positive cost?", body)]

    st += [Paragraph("2. Threat Model: What Is Measured", h1), table([
        ["Track", "Meaning", "Status"],
        ["A: contamination", "Outdated or contradictory policy competes with trusted policy in dense retrieval.",
         "Measured: 10-case suite and extended suite (outdated + contradiction + authority types)."],
        ["B: indirect injection", "Retrieved text contains instructions aimed at the LLM.",
         "Measured at retrieval level: 3 injection documents in the extended suite."],
        ["C: optimized poisoning", "Passages crafted to win retrieval for target questions (PoisonedRAG).",
         "Heuristic proxy only: 4 query-mirroring documents. No optimization; answer-level effect not measured."],
    ], [32, 70, 72])]

    st += [Paragraph("3. System Flow", h1), Paragraph(
        "Upload &rarr; PyPDF extraction &rarr; <b>trust gate</b> &rarr; accepted text split into 300-character chunks "
        "(30 overlap) &rarr; embedding (BAAI/bge-m3, 1024-d; MiniLM-L6-v2 as comparison) &rarr; ChromaDB &rarr; top-3 "
        "similarity search &rarr; optional Gemini synthesis. Rejected documents go to quarantine with their reasons. "
        "Because the gate runs before chunking and embedding, a rejected file contributes no vector to the index.", body)]

    st += [Paragraph("4. Extended Dataset: Good and Poisoned Files", h1), Paragraph(
        "Every poisoned file contains a unique wrong value or URL so its presence can be traced. Trusted files hold the "
        "correct company policy for 15 topics (passwords, VPN, MFA, leave, phishing, Wi-Fi, data classification, backup, "
        "software, incidents, laptop encryption, USB, cloud storage, expenses, general guidelines).", body),
        table([
            ["Attack type", "Docs", "Example of wrong content", "How it tries to win"],
            ["Outdated policy", "3", "\"Passwords must be at least 6 characters\" (2015)", "Same topic, older rules"],
            ["Contradiction", "4", "\"35 days paid leave\", \"SMS codes are preferred\"", "Copies official title, changes one fact"],
            ["Authority spoofing", "3", "\"v4.0 SUPERSEDES v3.0 ... MFA has been removed\"", "Claims to be the newest official version"],
            ["Prompt injection", "3", "\"Ignore all previous instructions ... reset at http://...\"", "Instruction aimed at the LLM"],
            ["Query mirroring", "4", "Repeats \"How is VPN access configured?\" then wrong answer", "Copies the question to maximize similarity"],
        ], [30, 12, 72, 60])]

    st += [KeepTogether([Paragraph("5. Earlier Result: 10-Question Gate Evaluation (BGE-M3)", h1), Paragraph(
        "With 5 trusted PDFs and 1 untrusted legacy VPN PDF, the untrusted file entered the top-3 for 4 of 10 questions "
        "(password_reset rank 2, vpn_setup rank 2, vpn_mfa rank 3, mfa_methods rank 2). The pre-index gate quarantined it "
        "and contamination fell to 0 of 10, with 100% expected-topic retrieval in both modes.", body),
        KeepTogether(table([["Configuration", "Indexed PDFs", "Contaminated", "Rate"],
               ["Mixed baseline", "6", "4 / 10", "40%"], ["Pre-index gate", "5", "0 / 10", "0%"]], [60, 35, 40, 39]))])]

    st += [Paragraph("6. Extended Results: Defense Comparison", h1), Paragraph(
        "Each of the 25 questions was run against three knowledge bases built with the same embedding model and k=3. "
        "\"Provenance gate\" is the trusted-only index: every poisoned file lies outside the trusted folder, so the source "
        "rule quarantines all 17 (0% by construction). \"Content scanner\" is a content-only check (no folder rule) "
        "that flags injection phrases, authority claims, http:// links, security-weakening phrases and non-corporate "
        "domains.", body)]
    rows = [["Configuration", "Correct doc #1", "Correct doc in top-3", "Poison in top-3", "Poison #1"]]
    names = {"1_trusted_only": "Provenance gate (trusted only)", "2_mixed": "No defense (mixed)",
             "3_mixed_plus_scanner": "Content scanner"}
    for kb in ("2_mixed", "3_mixed_plus_scanner", "1_trusted_only"):
        cells = []
        for k in ("trusted_at_rank1", "trusted_in_topk", "poison_in_topk", "poison_at_rank1"):
            vals = [pct(x[kb][k]) for x in (bge, mini) if x]
            cells.append(" / ".join(vals))
        rows.append([names[kb]] + cells)
    st += [table(rows, [50, 31, 33, 30, 30], highlight_rows=(1,)),
           Paragraph("Table 1: Extended results, 25 questions, top-3. Values: BGE-M3 / MiniLM-L6-v2.", cap),
           figure("fig1_defense_comparison",
                  f"Figure 1: Defense comparison ({S['primary_model']}). Poison fills the top-3 for every question without "
                  f"defense; the scanner cuts first-rank poisoning from {pct(kb_m['poison_at_rank1'])} to "
                  f"{pct(kb_s['poison_at_rank1'])}; only provenance reaches 0%.")]

    st += [Paragraph("7. Which Attack Works Best", h1)]
    order = sorted(at, key=lambda t: (-at[t]["top3"], -at[t]["rank1"]))
    st += [table([["Attack type", "Targeted pairs", "Reached top-3", "Ranked #1"]] +
                 [[t.replace("_", " "), at[t]["pairs"], pct(at[t]["top3"]), pct(at[t]["rank1"])] for t in order],
                 [50, 40, 42, 42]),
           Paragraph(f"Table 2: Attack success per targeted question-document pair, no defense ({S['primary_model']}).", cap),
           figure("fig2_attack_types", "Figure 2: Attack success by poisoning type. Query mirroring most reliably takes "
                  "first place; authority spoofing rarely does, because its 'official update' wording is less similar to "
                  "user questions."),
           Paragraph(
               f"Prompt injection and contradiction reached the top-3 in every targeted case "
               f"({pct(at['injection']['rank1'])} and {pct(at['contradiction']['rank1'])} at rank 1). Query mirroring took "
               f"rank 1 in {pct(at['query_mirror']['rank1'])} of cases, the same retrieval weakness that PoisonedRAG "
               f"optimizes. Poison also appeared in the top-3 for the control question, which no poisoned document "
               f"targeted: with 17 of 32 documents poisoned, a small top-k leaks unrelated poison too.", body)]

    st += [Paragraph("8. Content Scanner: What It Catches and Misses", h1),
           figure("fig3_scanner_detection",
                  f"Figure 3: Scanner detection by type. Recall {sc['blocked']}/{sc['poisoned']} ({recall:.0f}%), "
                  f"precision 100%, false alarms {sc['false_positives']}/{sc['trusted']}."),
           Paragraph(
               "The scanner caught every injection and authority document, since they carry trigger phrases or unapproved "
               "domains. It caught only 1 of 4 contradictions. The five misses (contra_leave, contra_mfa, contra_incident, "
               "mirror_wifi, outdated_password) state wrong facts in normal policy language with no URL, instruction or "
               "keyword. <b>A keyword or regex filter cannot detect a wrong number or a wrong rule;</b> that needs "
               "provenance checks or cross-document consistency checking. The scanner rules were written with knowledge of "
               "these documents, so real-world recall would be lower.", body)]

    st += [figure("fig4_model_comparison", "Figure 4: Embedding model comparison, mixed corpus, no defense. The multilingual "
                  "1024-d BGE-M3 was not more resistant than the 384-d MiniLM.", width=150,
                  heading=Paragraph("9. Comparisons", h1)),
           figure("fig5_benchmark_progression", "Figure 5: Top-3 contamination across the three benchmarks. The corpora differ, "
                  "so this is not a controlled comparison: with 1 bad doc the rate depends on which questions are asked; "
                  "with 17 it reaches every question.", width=150),
           table([["Benchmark", "Docs (good + bad)", "Questions", "Attack types", "Poison in top-3", "With defense"],
                  ["Pilot (MiniLM)", "5 + 1", "2", "1", "100%", "not tested"],
                  ["10-case suite (BGE-M3)", "5 + 1", "10", "1", "40%", "0% (gate)"],
                  ["Extended (BGE-M3)", f"{sc['trusted']} + {sc['poisoned']}", "25", "5",
                   pct(kb_m["poison_in_topk"]), f"{pct(kb_s['poison_in_topk'])} scanner / 0% provenance"]],
                 [38, 27, 20, 22, 27, 40]),
           Paragraph("Table 3: Benchmark comparison.", cap)]

    st += [Paragraph("10. Limitations and Honest Claims", h1), Paragraph(
        "All documents and questions are synthetic and written by the authors (32 PDFs, 25 questions), so the percentages "
        "do not generalize statistically. No Gemini key was used, so every metric is retrieval-level: whether the LLM "
        "repeats the poisoned content was not measured. Query mirroring is a heuristic, not an optimized PoisonedRAG "
        "attack. The provenance result is 0% by construction because every poisoned file sits outside the trusted "
        "folder; a poisoned file placed inside a trusted path would bypass it. No Bangla documents, obfuscated or Unicode "
        "injections, latency, or repeated-trial confidence intervals were measured.", body),
        Paragraph("<b>Defensible claim:</b> on this synthetic benchmark, dense retrieval placed poisoned content in the "
                  "top-3 for every question; a content-only scanner removed the obvious attacks but not fact-level "
                  "contradictions; the pre-index provenance gate removed all of it. <b>Not defensible:</b> that the gate "
                  "prevents all poisoning or prompt injection.", body)]

    st += [Paragraph("11. Next Steps", h1), Paragraph(
        "(1) Run with GEMINI_API_KEY to measure answer-level attack success. (2) Add Bangla and mixed-language poisoned "
        "documents. (3) Add obfuscated injections (Unicode, invisible text, paraphrase). (4) Add a semantic contradiction "
        "check that compares new documents with existing trusted policies, targeting the misses in Section 8. "
        "(5) Report latency and repeated-run confidence intervals.", body)]

    st += [Paragraph("12. Reproduction", h1), Paragraph(
        "python3 scripts/run_extended_experiment.py<br/>"
        "RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2 python3 scripts/run_extended_experiment.py<br/>"
        "python3 scripts/make_charts.py<br/>python3 scripts/generate_final_report.py", code),
        Paragraph("Outputs: outputs/extended_results_&lt;model&gt;.md/.csv, outputs/extended_log_&lt;model&gt;.txt, "
                  "outputs/figures/. Source: https://github.com/takitahmid20/rag-data-poisoning. "
                  "Paper: https://github.com/takitahmid20/rag-data-poisoning-paper.", body)]

    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm,
                            bottomMargin=17 * mm, title="Comprehensive RAG Security Evaluation Report",
                            author="Taki Tahmid and Group 06")
    doc.build(st, onFirstPage=footer, onLaterPages=footer)
    print(f"[+] Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
