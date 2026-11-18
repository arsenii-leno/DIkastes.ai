"""Illustrative 10-case PoC for the VYBSEM paper.

Four pipelines over a tiny synthetic civil-law corpus:
  A    similarity-only retrieval
  A+V  A followed by the deterministic verifier V
  B    hierarchy- and time-aware retrieval (jurisdiction, validity, rank filters)
  C    B followed by V
Each answer is scored accurate / incomplete / hallucinated (Magesh et al., 2025).
Run:  python3 poc_sim.py   -> prints Table 1 data and writes fig1.png
"""
from datetime import date

# ---------- corpus: one record per provision VERSION ----------
# id, work, jurisdiction, rank (1 = highest), valid_from, valid_to (exclusive), text
CORPUS = [
    # Topic 1: late-payment interest (act v1 -> v2 amended 2023-01-01)
    ("SK-A1-v1", "SK-A1", "SK", 2, date(2010, 1, 1), date(2023, 1, 1), "late payment interest rate eight percent per year"),
    ("SK-A1-v2", "SK-A1", "SK", 2, date(2023, 1, 1), None, "late payment interest rate is the base rate plus five points"),
    # Topic 2: public holidays (mirrors Act 241/1993, amended 2025-11-01)
    ("SK-H2-v1", "SK-H2", "SK", 2, date(2016, 1, 1), date(2025, 11, 1), "17 november state holiday is a day of rest"),
    ("SK-H2-v2", "SK-H2", "SK", 2, date(2025, 11, 1), None, "17 november state holiday is not a day of rest"),
    # Topic 3: consumer withdrawal; Czech near-twin
    ("SK-C3", "SK-C3", "SK", 2, date(2015, 1, 1), None, "consumer may withdraw from distance contract within 14 days"),
    ("CZ-C3", "CZ-C3", "CZ", 2, date(2014, 1, 1), None, "consumer may withdraw from a distance contract within fourteen days"),
    # Topic 4: lease deposit; government regulation contradicts the act (conflict edge known)
    ("SK-L4", "SK-L4", "SK", 2, date(2014, 1, 1), None, "lease deposit at most three months rent"),
    ("SK-L4-NV", "SK-L4-NV", "SK", 3, date(2020, 1, 1), None, "deposit for flat lease may be six months rent"),
    # Topic 5: warranty period; regulation contradicts the act (conflict edge MISSING)
    ("SK-W5", "SK-W5", "SK", 2, date(2014, 1, 1), None, "warranty period for goods is 24 months"),
    ("SK-W5-NV", "SK-W5-NV", "SK", 3, date(2021, 1, 1), None, "goods warranty period twelve months for used goods"),
    # Topic 6: limitation period; a same-act neighbour that does not state the rule
    ("SK-P6-1", "SK-P6-1", "SK", 2, date(2000, 1, 1), None, "general limitation period is three years"),
    ("SK-P6-2", "SK-P6-2", "SK", 2, date(2000, 1, 1), None, "limitation period for claims on unjust enrichment starts"),
]
BY_ID = {r[0]: r for r in CORPUS}
CONFLICTS = {("SK-L4-NV", "SK-L4")}            # (lower, higher); SK-W5 edge deliberately absent
APPLICABLE = {"SK": {"SK", "EU"}}
COVERED = {"SK", "CZ"}                         # namespaces the toy corpus covers completely

# ---------- 10 cases ----------
# id, trap, question, facts date, gold ids, premise citation (fabricated) or None
CASES = [
    ("V1", "valid", "late payment interest rate base rate", date(2024, 3, 1), {"SK-A1-v2"}, None),
    ("V2", "valid", "consumer withdraw distance contract 14 days", date(2024, 3, 1), {"SK-C3"}, None),
    ("F1", "fabricated", "late payment interest rate base rate under SK-A1a", date(2024, 3, 1), {"SK-A1-v2"}, "SK-A1a"),
    ("F2", "fabricated", "lease deposit three months rent under SK-L4b", date(2024, 3, 1), {"SK-L4"}, "SK-L4b"),
    ("R1", "repealed", "late payment interest rate eight percent", date(2024, 3, 1), {"SK-A1-v2"}, None),
    ("R2", "repealed", "is 17 november a day of rest", date(2026, 11, 17), {"SK-H2-v2"}, None),
    ("J1", "jurisdiction", "consumer withdraw from a distance contract within fourteen days", date(2024, 3, 1), {"SK-C3"}, None),
    ("S1", "superior", "deposit for flat lease six months rent", date(2024, 3, 1), {"SK-L4"}, None),
    ("S2", "superior_no_edge", "goods warranty period twelve months used goods", date(2024, 3, 1), {"SK-W5"}, None),
    ("M1", "misgrounded", "limitation period for claims starts", date(2024, 3, 1), {"SK-P6-1"}, None),
]


def sim(q, text):
    """Token-overlap (Jaccard) similarity: the 'semantic' baseline in miniature."""
    a, b = set(q.lower().split()), set(text.lower().split())
    return len(a & b) / len(a | b)


def in_force(r, t):
    return r[4] <= t and (r[5] is None or t < r[5])


def retrieve(q, t, aware):
    pool = CORPUS
    if aware:                                        # System B filters
        pool = [r for r in pool if r[2] in APPLICABLE["SK"] and in_force(r, t)]
        ids = {r[0] for r in pool}
        pool = [r for r in pool if not any(lo == r[0] and hi in ids for lo, hi in CONFLICTS)]
    return max(pool, key=lambda r: sim(q, r[6]))[0]


def generate(case, aware):
    """Reference generator: cites the top retrieved provision and echoes a premise citation."""
    cites = [retrieve(case[2], case[3], aware)]
    if case[5]:
        cites.append(case[5])
    return cites


def verify(cite, t):
    """Deterministic verifier V: returns VALID or a reason code."""
    if cite not in BY_ID:
        # absent != fabricated: only a namespace the corpus fully covers proves non-existence
        return "NONEXISTENT" if cite.split("-")[0] in COVERED else "UNVERIFIABLE"
    r = BY_ID[cite]
    if not in_force(r, t):
        return "NOT_IN_FORCE"
    if r[2] not in APPLICABLE["SK"]:
        return "WRONG_JURISDICTION"
    if any(lo == cite and in_force(BY_ID[hi], t) for lo, hi in CONFLICTS):
        return "OVERRIDDEN"
    return "VALID"


def score(cites, gold):
    if not cites:
        return "I"                                   # incomplete: nothing left to cite
    return "A" if set(cites) <= gold else "H"


def run(system):
    aware, verified = system in ("B", "C"), system in ("A+V", "C")
    out = {}
    for case in CASES:
        cites = generate(case, aware)
        if verified:
            cites = [c for c in cites if verify(c, case[3]) == "VALID"]   # invalid ones are FLAGGED, not hidden
        out[case[0]] = score(cites, case[4])
    return out


if __name__ == "__main__":
    systems = ["A", "A+V", "B", "C"]
    results = {s: run(s) for s in systems}
    print("case  " + "  ".join(f"{s:>4}" for s in systems))
    for c in CASES:
        print(f"{c[0]:<5} " + "  ".join(f"{results[s][c[0]]:>4}" for s in systems))
    totals = {s: {k: list(results[s].values()).count(k) for k in "AIH"} for s in systems}
    print(totals)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7})
    colors = {"A": "#0ca30c", "I": "#fab219", "H": "#d03b3b"}
    names = {"A": "accurate", "I": "incomplete", "H": "hallucinated"}
    fig, ax = plt.subplots(figsize=(3.3, 0.95), dpi=300)
    for y, s in enumerate(reversed(systems)):
        left = 0
        for k in "AIH":
            n = totals[s][k]
            if n:
                ax.barh(y, n, left=left, color=colors[k], height=0.62, edgecolor="white", linewidth=1)
                ax.text(left + n / 2, y, str(n), ha="center", va="center",
                        color="#0b0b0b" if k == "I" else "white", fontsize=7, fontweight="bold")
            left += n
    ax.set_yticks(range(len(systems)), list(reversed(systems)))
    ax.set_xlim(0, 10)
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#c3c2b7")
    ax.spines["bottom"].set_color("#c3c2b7")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[k]) for k in "AIH"]
    ax.legend(handles, [names[k] for k in "AIH"], ncol=3, frameon=False, fontsize=6.5,
              loc="lower center", bbox_to_anchor=(0.45, 1.0), handlelength=1, columnspacing=1)
    fig.tight_layout(pad=0.2)
    fig.savefig("fig1.png")


# ---------- per-case table for the repository (results.md) ----------
EXPECTED = {"valid": "VALID", "fabricated": "NONEXISTENT", "repealed": "NOT_IN_FORCE",
            "jurisdiction": "WRONG_JURISDICTION", "superior": "OVERRIDDEN",
            "superior_no_edge": "VALID (Type II, invisible to V)", "misgrounded": "VALID (Type II, invisible to V)"}
TRAP_NAME = {"valid": "Valid control", "fabricated": "Fabricated premise", "repealed": "Repealed version",
             "jurisdiction": "Wrong jurisdiction (Czech twin)", "superior": "Lex superior, conflict recorded",
             "superior_no_edge": "Lex superior, conflict not recorded", "misgrounded": "Misgrounding"}


def write_results_md(path="results.md"):
    res = {s: run(s) for s in ["A", "A+V", "B", "C"]}
    rows = ["| ID | Case | Error type | Expected V code | V on A's answer | A | A+V | B | C |",
            "|---|---|---|---|---|---|---|---|---|"]
    for n, case in enumerate(CASES, 1):
        codes = ", ".join(f"{c}: {verify(c, case[3])}" for c in generate(case, aware=False))
        rows.append(f"| T{n:02d} | {case[0]} | {TRAP_NAME[case[1]]} | {EXPECTED[case[1]]} | {codes} | "
                    + " | ".join(res[s][case[0]] for s in ["A", "A+V", "B", "C"]) + " |")
    tot = {s: {k: list(res[s].values()).count(k) for k in "AIH"} for s in res}
    rows.append("| | **Total** | | | | " + " | ".join(f"{tot[s]['A']}A/{tot[s]['I']}I/{tot[s]['H']}H" for s in res) + " |")
    open(path, "w").write("\n".join(rows) + "\n\nA = accurate, I = incomplete, H = hallucinated (Magesh et al., 2025). "
                          "A+V applies the verifier V to A's answer, without B's jurisdiction, validity and rank filters.\n")


if __name__ == "__main__":
    write_results_md()
