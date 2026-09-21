"""Build report/paper figures from outputs/extended_results_<model>.csv.

Writes PNG (300 dpi) + PDF to outputs/figures/ and a summary JSON used by the reports.
Run after run_extended_experiment.py (one or both embedding models).
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts"))
from extended_dataset import POISONED, TRUSTED
from run_extended_experiment import scan, load_docs, TRUSTED_DIR, POISON_DIR

OUT = BASE_DIR / "outputs"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# validated categorical order (dataviz reference palette, light mode)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
MODELS = {"bge-m3": "BGE-M3", "all-MiniLM-L6-v2": "MiniLM-L6-v2"}
POISON_TYPE = {n: t for n, t, *_ in POISONED}
TYPE_LABEL = {"injection": "Prompt\ninjection", "contradiction": "Contradiction", "query_mirror": "Query\nmirroring",
              "authority": "Authority\nspoofing", "outdated": "Outdated\npolicy"}
TYPES = list(TYPE_LABEL)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
})


def load(tag):
    p = OUT / f"extended_results_{tag}.csv"
    if not p.exists():
        return None
    rows = list(csv.DictReader(open(p)))
    for r in rows:
        for k in ("trusted_at_rank1", "trusted_in_topk", "poison_in_topk", "poison_at_rank1"):
            r[k] = r[k] == "True"
    return rows


def rate(rows, kb, key):
    rs = [r for r in rows if r["kb"] == kb]
    return 100 * sum(r[key] for r in rs) / len(rs)


def attack_stats(rows):
    s = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        if r["kb"] != "2_mixed":
            continue
        top = r["top_sources"].split(";")
        for t in filter(None, r["targeted_by"].split(";")):
            x = s[POISON_TYPE[t]]
            x[0] += 1
            x[1] += t in top
            x[2] += top[0] == t
    return {t: {"pairs": n, "top3": 100 * k / n, "rank1": 100 * r1 / n} for t, (n, k, r1) in s.items()}


def label_bars(ax, bars, fmt="{:.0f}%"):
    for b in bars:
        ax.annotate(fmt.format(b.get_height()), (b.get_x() + b.get_width() / 2, b.get_height()),
                    xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8, color=INK)


def grouped(ax, groups, series, colors, width=0.26):
    """series: list of (label, values). 2px surface gap between adjacent bars."""
    n = len(series)
    for i, ((lab, vals), c) in enumerate(zip(series, colors)):
        xs = [g + (i - (n - 1) / 2) * width for g in range(len(groups))]
        bars = ax.bar(xs, vals, width * 0.92, color=c, label=lab, edgecolor="white", linewidth=1)
        label_bars(ax, bars)
    ax.set_xticks(range(len(groups)), groups)
    ax.set_ylim(0, 115)
    ax.set_yticks(range(0, 101, 25), [f"{v}%" for v in range(0, 101, 25)])


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=300)
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


def main():
    data = {tag: rows for tag in MODELS if (rows := load(tag))}
    if not data:
        sys.exit("No extended_results_<model>.csv found - run run_extended_experiment.py first.")
    primary = "bge-m3" if "bge-m3" in data else next(iter(data))
    rows = data[primary]
    summary = {"primary_model": MODELS[primary], "models": {}}

    for tag, rs in data.items():
        summary["models"][MODELS[tag]] = {
            kb: {k: round(rate(rs, kb, k), 1) for k in ("trusted_at_rank1", "trusted_in_topk", "poison_in_topk", "poison_at_rank1")}
            for kb in ("1_trusted_only", "2_mixed", "3_mixed_plus_scanner")
        }
        summary["models"][MODELS[tag]]["attack_types"] = attack_stats(rs)

    # Fig 1 - defense comparison (primary model)
    configs = [("No defense (mixed KB)", "2_mixed"), ("Content scanner", "3_mixed_plus_scanner"),
               ("Provenance gate", "1_trusted_only")]
    metrics = [("Correct doc\nranked #1", "trusted_at_rank1"), ("Poison in\ntop-3", "poison_in_topk"),
               ("Poison\nranked #1", "poison_at_rank1")]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    grouped(ax, [m for m, _ in metrics], [(c, [rate(rows, kb, k) for _, k in metrics]) for c, kb in configs],
            [ORANGE, AQUA, BLUE])
    ax.set_ylabel("Share of 25 questions")
    ax.set_title(f"Defense comparison ({MODELS[primary]}, top-3)", loc="left", fontsize=10, color=INK)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=8)
    save(fig, "fig1_defense_comparison")

    # Fig 2 - attack success by type
    st = attack_stats(rows)
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    grouped(ax, [TYPE_LABEL[t] for t in TYPES],
            [("Reached top-3", [st[t]["top3"] for t in TYPES]), ("Ranked #1", [st[t]["rank1"] for t in TYPES])],
            [BLUE, ORANGE], width=0.36)
    ax.set_ylabel("Targeted question pairs")
    ax.set_title(f"Attack success by poisoning type (no defense, {MODELS[primary]})", loc="left", fontsize=10, color=INK)
    ax.legend(frameon=False, ncol=2, loc="upper right", fontsize=8)
    save(fig, "fig2_attack_types")

    # Fig 3 - scanner detection by type (+ false positives on trusted docs)
    docs = load_docs(TRUSTED_DIR, "trusted") + load_docs(POISON_DIR, "poisoned")
    flagged = {d.metadata["source"]: bool(scan(d.page_content)) for d in docs}
    det = {t: [sum(flagged[n] for n in POISON_TYPE if POISON_TYPE[n] == t), sum(1 for n in POISON_TYPE if POISON_TYPE[n] == t)]
           for t in TYPES}
    fp = sum(flagged[n] for n, *_ in TRUSTED)
    labels = [TYPE_LABEL[t] for t in TYPES] + ["Trusted docs\n(false alarm)"]
    vals = [100 * a / b for a, b in det.values()] + [100 * fp / len(TRUSTED)]
    counts = [f"{a}/{b}" for a, b in det.values()] + [f"{fp}/{len(TRUSTED)}"]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    bars = ax.bar(range(len(vals)), vals, 0.55, color=[BLUE] * len(TYPES) + [MUTED], edgecolor="white")
    for b, v, c in zip(bars, vals, counts):
        ax.annotate(f"{v:.0f}%  ({c})", (b.get_x() + b.get_width() / 2, v), xytext=(0, 2),
                    textcoords="offset points", ha="center", fontsize=8, color=INK)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylim(0, 115)
    ax.set_yticks(range(0, 101, 25), [f"{v}%" for v in range(0, 101, 25)])
    ax.set_ylabel("Documents flagged")
    tot = sum(a for a, _ in det.values())
    ax.set_title(f"Content scanner: {tot}/{len(POISONED)} poisoned docs blocked, {fp} false alarms",
                 loc="left", fontsize=10, color=INK)
    save(fig, "fig3_scanner_detection")
    summary["scanner"] = {"blocked": tot, "poisoned": len(POISONED), "false_positives": fp, "trusted": len(TRUSTED),
                          "by_type": {t: f"{a}/{b}" for t, (a, b) in det.items()}}

    # Fig 4 - embedding model comparison (mixed KB)
    if len(data) > 1:
        fig, ax = plt.subplots(figsize=(6.4, 3.2))
        tags = [t for t in MODELS if t in data]
        grouped(ax, [m for m, _ in metrics], [(MODELS[t], [rate(data[t], "2_mixed", k) for _, k in metrics]) for t in tags],
                [BLUE, ORANGE], width=0.36)
        ax.set_ylabel("Share of 25 questions")
        ax.set_title("Embedding model comparison (no defense, mixed KB)", loc="left", fontsize=10, color=INK)
        ax.legend(frameon=False, ncol=2, loc="upper right", fontsize=8)
        save(fig, "fig4_model_comparison")

    # Fig 5 - benchmark progression: poison-in-top-3 rate as the test set grew
    pilot = 100.0  # original 2-question pilot: outdated_vpn_policy.pdf in top-3 for both queries (experiment_log.txt)
    ten_case = 40.0  # 10-question BGE-M3 suite, 1 untrusted doc (paper repo expanded_evaluation.txt)
    ext = rate(rows, "2_mixed", "poison_in_topk")
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    names = ["Pilot\n6 docs, 2 questions", "10-case suite\n6 docs, 10 questions",
             f"Extended suite\n32 docs, 25 questions"]
    bars = ax.bar(range(3), [pilot, ten_case, ext], 0.5, color=[MUTED, MUTED, BLUE], edgecolor="white")
    label_bars(ax, bars)
    ax.set_xticks(range(3), names)
    ax.set_ylim(0, 115)
    ax.set_yticks(range(0, 101, 25), [f"{v}%" for v in range(0, 101, 25)])
    ax.set_ylabel("Questions with poison in top-3")
    ax.set_title("Contamination as the benchmark grew (1 bad doc -> 17 bad docs)", loc="left", fontsize=10, color=INK)
    save(fig, "fig5_benchmark_progression")
    summary["progression"] = {"pilot": pilot, "ten_case": ten_case, "extended": round(ext, 1)}

    (OUT / "figures" / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"[+] Figures written to {FIG.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
