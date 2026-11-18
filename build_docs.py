"""Fill the official ACM interim-layout.docx template with the extended abstract and the 2-page paper."""
import copy, re, sys, zipfile, shutil
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEMPLATE, OUTDIR = sys.argv[1], sys.argv[2]
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

TITLE = "Citation Verification and Hallucination Reduction of Large Language Models in a Civil-Law Legal Environment"
AUTHORS = [
    ("Arsenii", "Leno", "FIIT",
     "Slovak University of Technology", "xlenoa@stuba.sk"),
    ("Richard", "Marko", "FIIT",
     "Slovak University of Technology", "richard.marko@stuba.sk"),
]

ABSTRACT = (
    "Large language models (LLMs) used for legal research cite non-existent, repealed or overridden provisions; commercial RAG tools hallucinate on 17–33% of a deliberately hard question set [1]. "
    "Civil-law statutes carry official identifiers, dated versions and a formal rank, so whether a cited version exists, "
    "is in force on the facts date, belongs to an applicable jurisdiction and is not overridden is decidable by lookup "
    "in an official corpus; whether it supports the claim is not. We state this split as a three-type error taxonomy and "
    "design time- and rank-aware retrieval followed by a deterministic, version-level verifier with reason codes. A "
    "10-case synthetic example illustrates, but does not measure, which errors each component removes.")

KEYWORDS = "legal AI, hallucination, citation verification, RAG, civil law, temporal validity"

REFS = {
    "magesh": "Varun Magesh, Faiz Surani, Matthew Dahl, Mirac Suzgun, Christopher D. Manning, and Daniel E. Ho. 2025. "
              "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools. *Journal of Empirical "
              "Legal Studies* 22, 2 (2025), 216–242. https://doi.org/10.1111/jels.12413",
    "liu": "Patty Liu, Dominik Stammbach, and Peter Henderson. 2026. Who Checks the Citations? Benchmarking Legal "
           "Hallucination Detection. *arXiv preprint* arXiv:2606.21155.",
    "prior": "Max Prior, Andreas Schultz, and Matthias Grabmair. 2026. Asking For An Old Friend: Diagnosing and Mitigating "
             "Temporal Failure Modes in LLM-based Statutory Question Answering. In *Proceedings of the International "
             "Conference on Artificial Intelligence and Law (ICAIL 2026)*. arXiv:2605.23497.",
    "calrk": "JiHyeok Jung, Taeyoung Yoon, and Hyunsouk Cho. 2026. CALRK-Bench: Evaluating Context-Aware Legal Reasoning "
             "in Korean Law. *arXiv preprint* arXiv:2603.26332.",
    "demartim": "Hudson de Martim. 2025. An Ontology-Driven Graph RAG for Legal Norms: A Hierarchical, Temporal, and "
                "Deterministic Approach. In *Legal Knowledge and Information Systems (JURIX 2025)* (Frontiers in Artificial "
                "Intelligence and Applications, Vol. 416). IOS Press, 282–287. "
                "https://doi.org/10.3233/FAIA251598",
    "piccioli": "Giovanni Piccioli, Alessia Fidelangeli, Piera Santin, and Pierpaolo Vivo. 2026. From Judgments to Issues: "
                "Structured Extraction of Legal Reasoning with Citation-Hallucination Control. *arXiv preprint* "
                "arXiv:2607.03325.",
    "wallat": "Jonas Wallat, Maria Heuss, Maarten de Rijke, and Avishek Anand. 2025. Correctness is not Faithfulness in "
              "Retrieval Augmented Generation Attributions. In *Proceedings of the 2025 International ACM SIGIR "
              "Conference on Innovative Concepts and Theories in Information Retrieval (ICTIR '25)*. ACM, 22–32. "
              "https://doi.org/10.1145/3731120.3744592",
    "deusser": "Tobias Deußer, Abhishek Pillai, Aurelio F. Bariviera, Dhananjay Bhardwaj, Lorenz Sparrenberg, David "
               "Berghaus, Christian Bauckhage, and Rafet Sifa. 2026. Automated Regulatory Compliance Question Answering "
               "in Financial Services with Domain-Adapted Retrieval-Augmented Generation. *arXiv preprint* "
               "arXiv:2609.30009.",
    "rirag": "Tuba Gokhan, Kexin Wang, Iryna Gurevych, and Ted Briscoe. 2025. Shared Task RIRAG-2025: Regulatory "
             "Information Retrieval and Answer Generation. In *Proceedings of the 1st Regulatory NLP Workshop "
             "(RegNLP 2025)*. ACL, 1–4.",
    "lexam": "Yu Fan, Jingwei Ni, Jakob Merane, et al. 2026. LEXam: Benchmarking Legal Reasoning on 340 Law Exams. In "
             "*Proceedings of the International Conference on Learning Representations (ICLR 2026)*. arXiv:2505.12864.",
    "du": "Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, and Igor Mordatch. 2024. Improving Factuality and "
          "Reasoning in Language Models through Multiagent Debate. In *Proceedings of the 41st International Conference "
          "on Machine Learning (ICML 2024)* (PMLR, Vol. 235).",
    "zhang": "Hangfan Zhang, Zhiyao Cui, Jianhao Chen, Xinrun Wang, Qiaosheng Zhang, Zhen Wang, Dinghao Wu, and Shuyue Hu. "
             "2025. Stop Overvaluing Multi-Agent Debate: We Must Rethink Evaluation and Embrace Model Heterogeneity. "
             "*arXiv preprint* arXiv:2502.08788.",
    "clerc": "Abe Bohan Hou, Orion Weller, Guanghui Qin, Eugene Yang, Dawn Lawrie, Nils Holzenberger, Andrew Blair-Stanek, "
             "and Benjamin Van Durme. 2025. CLERC: A Dataset for U.S. Legal Case Retrieval and Retrieval-Augmented "
             "Analysis Generation. In *Findings of the Association for Computational Linguistics: NAACL 2025*. ACL, "
             "7913–7928. https://doi.org/10.18653/v1/2025.findings-naacl.441",
    "taranukhin": "Maksym Taranukhin and Vered Shwartz. 2026. Legal LLM Hallucination Should Be Evaluated as Failure of "
                  "Legal Warrant. *arXiv preprint* arXiv:2609.17546.",
    "ovcharov": "Volodymyr Ovcharov. 2026. Citation Grounding Measures the Oracle: Graph Coverage Determines Reported LLM "
                "Hallucination Rates in Law. *arXiv preprint* arXiv:2606.00898.",
}

STATUTE = ("§ 2(3) of Act No. 241/1993 Z. z. as amended by Act No. 261/2025 Z. z.; consolidated versions on "
           "slov-lex.sk")

# ---------------- paper body ----------------
PAPER_BODY = [
    ("h", "1", "Introduction"),
    ("p", "Fabricated citations have reached over 1,000 court filings [{liu}]. Commercial legal RAG "
          "tools hallucinate on 17–33% of a question set built to be hard, not to estimate a population rate, often by "
          "citing real but inapplicable authority [{magesh}]. Time is a recurring failure: models apply superseded "
          "statutes unless validity is a hard constraint [{prior}], and on Korean law accuracy where the pre-change norm "
          "governs is about 39 points below post-change cases (our means: 27.7% vs 66.5%) "
          "[{calrk}]. Such stale law is an error all models share. Debate drops facts agents are uncertain of [{du}]; "
          "heterogeneous agents fix only questions some model solves, while those all fail stay unsolved [{zhang}]. A "
          "norm memorised before its amendment needs an external oracle, not more agents. Recent work names the dimensions of legal warrant (existence, jurisdiction, temporal currency, status, "
          "support) as a position and benchmark agenda [{taranukhin}]. A lookup check of Ukrainian answers against a "
          "court-decision citation graph showed that reported rates follow oracle coverage (grounding 0.79–0.86 on a "
          "sparse vs 0.99–1.00 on a dense graph, same answers) [{ovcharov}]. In common law, checking a "
          "precedent needs agentic search (GPT-5: 15.3 steps per excerpt) [{liu}]. We contribute (i) a "
          "decidability split: what lookup in an official, versioned corpus settles and what it cannot, (ii) version- "
          "and rank-aware retrieval and verification, and (iii) a 10-case illustration."),
    ("h", "2", "Failure Taxonomy"),
    ("p", "A corpus holds provision versions *v* = (*w*, *s*, *e*, *j*, *r*): work, validity [*s*, *e*), jurisdiction, "
          "rank. For a version-level citation at facts date *t*, **Type I** errors are decidable by lookup, relative to "
          "the corpus: the work does not exist, no version has *s* ≤ *t* < *e*, the jurisdiction does not apply, or a "
          "recorded conflict lets a higher rank override *v* (a precedent's standing depends on later courts). **Type II** errors need interpretation: an unrecorded conflict, or a valid citation that does not "
          "support the claim (misgrounding [{magesh}]). **Type III** errors are unfaithful: a source is attached after "
          "answering from memory, as for up to 57% of injected relevant documents [{wallat}]. "
          "*Example:* 17 November is a Slovak state holiday (§ 1 f) of Act 241/1993 Z. z.), and since 1 November 2025 "
          "§ 2(3), amended by Act 261/2025 Z. z. (kept by Act 256/2026 Z. z.), excludes it from days of rest. § 2(3) "
          "exists and is in force on every date; only its content changed. Citing the pre-amendment "
          "version is Type I (NOT_IN_FORCE); a free-text \u201c§ 2(3)\u201d resolves to the version in force at *t*, "
          "and whether the claim follows from it is Type II."),
    ("h", "3", "Proposed Architecture"),
    ("p", "**A** is similarity-only RAG over all versions. **B** filters before ranking (jurisdiction, validity at *t*, "
          "recorded overrides) over a work/version model of norms [{demartim}]. **C** passes B's "
          "answer to a deterministic verifier *V* that resolves each citation to a version identifier and returns VALID "
          "or a flag: NONEXISTENT, NOT_IN_FORCE, WRONG_JURISDICTION, OVERRIDDEN, or UNVERIFIABLE when the norm lies outside the "
          "corpus; **A+V** applies V to A's answer without B's filters. Absent is not fabricated: a weak checker flagged 65.9% of valid but unlisted "
          "citations [{liu}]. Flags are shown, not dropped "
          "[{magesh}]. Identifier matching cut hallucinated citations in Italian judgments from 11.7% to 0.9% (against "
          "the judgment's own text, without time or rank) [{piccioli}]. For Type II we plan a diverse, "
          "independent LLM jury validated against human experts, like LEXam's minimum-score ensemble [{lexam}]. The 10 "
          "synthetic cases cover controls, fabricated premises, repealed versions (one mirrors 17 "
          "November), a Czech near-twin, lex superior conflicts with and without a recorded edge, and misgrounding; a "
          "deterministic generator cites the top retrieved version and echoes premise citations; answers are scored accurate, incomplete or "
          "hallucinated [{magesh}]. The script was written with an AI coding assistant and reviewed by the authors."),
    ("h", "4", "Illustrative Evaluation"),
    ("fig",),
    ("p", "A (2 of 10 accurate) retrieves repealed, foreign and lower-ranked versions and echoes fabrications. A+V "
          "flags every Type I citation but leaves four answers unsupported. B (6) fixes repealed, foreign and "
          "recorded-conflict cases; C (8) fails only on the two Type II cases. Type I outcomes are correct by "
          "construction (corpus and verifier share records): Figure 1 illustrates the split, not model accuracy."),
    ("h", "5", "Limits and Future Work"),
    ("p", "V is exact only relative to its corpus (consolidated texts are informative, the promulgated text binding; a "
          "conflicting lower norm stays in force until the Constitutional Court decides, so V flags, not voids it) and "
          "checks correctness, not faithfulness [{wallat}]. Text metrics mislead: CLERC's highest-ROUGE model "
          "hallucinates most [{clerc}], an identity-function generator topped RIRAG (0.973 RePASs) [{rirag}], and a "
          "closed-book model came within 0.011 of full RAG [{deusser}]. Next: Slov-Lex data and real LLMs."),
]
PAPER_REFS = ["magesh", "liu", "prior", "calrk", "du", "zhang", "taranukhin", "ovcharov", "wallat", "demartim", "piccioli", "lexam", "clerc", "rirag", "deusser"]

# ---------------- extended abstract body ----------------
EA_ABSTRACT = (
    "We propose verifying the citations in legal answers of large language models (LLMs) against the official, "
    "versioned statute corpus of a civil-law system. Whether a cited provision exists, was in force on the date of "
    "the facts, belongs to an applicable jurisdiction and is not overridden is decidable by lookup, not by another model.")
EA_BODY = [
    ("h", "1", "Motivation"),
    ("p", "LLM legal tools cite non-existent or repealed provisions: commercial RAG tools hallucinate "
          "in 17–33% of queries [{magesh}], and over 1,000 court filings with fabricated citations are documented [{liu}]. "
          "Existing checkers target common law, where verifying a precedent needs agentic search [{liu}]."),
    ("h", "2", "Idea"),
    ("p", "Since 1 November 2025, 17 November is a state holiday in Slovakia but no longer a day of rest (" + STATUTE
          + "). The provision number is unchanged, so a model trained on older text answers wrongly, yet the version in "
          "force on any date is published by the state."),
    ("h", "3", "Design"),
    ("p", "**Type I** errors are decidable by lookup (non-existent, not in force, wrong jurisdiction); **Type II** need "
          "interpretation (unrecorded norm conflicts, citations not supporting the claim); **Type III** are unfaithful "
          "citations added after answering from memory [{wallat}]. We compare similarity-only RAG (**A**), RAG with "
          "jurisdiction, validity and rank filters over a work/version model of norms (**B**) [{demartim}], and B with a "
          "deterministic verifier that returns reason codes and flags invalid citations (**C**)."),
    ("h", "4", "Preliminary Results and Plan"),
    ("p", "In a 10-case illustrative proof of concept on a synthetic corpus, A answers 2 cases accurately, B 6 and C 8; "
          "the two remaining errors are Type II. The final paper reports this evaluation; a bachelor thesis will extend "
          "it to Slov-Lex and EUR-Lex data and real LLMs."),
]
EA_REFS = ["magesh", "liu", "demartim", "wallat"]

TABLE = [  # Table 1 (from poc_sim.py output)
    ["Sys.", "Ctrl", "Fab", "Rep", "Jur", "Sup1", "Sup2", "Mis"],
    ["A", "2A", "2H", "2H", "H", "H", "H", "H"],
    ["A+V", "2A", "2A", "2I", "I", "I", "H", "H"],
    ["B", "2A", "2H", "2A", "A", "A", "H", "H"],
    ["C", "2A", "2A", "2A", "A", "A", "H", "H"],
]


# ---------------- helpers ----------------
def clear(p):
    for child in list(p._p):
        if child.tag != qn('w:pPr'):
            p._p.remove(child)


def add_rich(p, text, size=None):
    for part in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text):
        if not part:
            continue
        if part.startswith('**'):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith('*'):
            r = p.add_run(part[1:-1]); r.italic = True
        else:
            r = p.add_run(part)
        if size:
            r.font.size = Pt(size)


def remove(p):
    p._p.getparent().remove(p._p)


def set_texts(p, mapping):
    """Assign new strings to the run texts of a template paragraph, in order; None deletes the run."""
    ts = [t for t in p._p.iter(W + 't')]
    for t, new in zip(ts, mapping):
        if new is None:
            r = t.getparent(); r.getparent().remove(r)
        else:
            t.text = new
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')


def unwrap_hyperlinks(p):
    for h in list(p._p.iter(W + 'hyperlink')):
        parent = h.getparent(); idx = parent.index(h)
        for r in list(h):
            parent.insert(idx, r); idx += 1
        parent.remove(h)


def cite(text, order):
    return re.sub(r'\{(\w+)\}', lambda m: str(order.index(m.group(1)) + 1), text)


def table_borders(tbl):
    tblPr = tbl._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side, sz in (('top', 8), ('bottom', 8), ('insideH', 0)):
        e = OxmlElement(f'w:{side}')
        e.set(qn('w:val'), 'single' if sz else 'nil'); e.set(qn('w:sz'), str(sz))
        e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000')
        b.append(e)
    tblPr.append(b)


def build(kind):
    d = docx.Document(TEMPLATE)
    ps = d.paragraphs
    order = PAPER_REFS if kind == 'paper' else EA_REFS

    # title / subtitle
    clear(ps[0]); ps[0].add_run(TITLE)
    clear(ps[1]); ps[1].add_run("Design and Proof of Concept" if kind == 'paper' else "Extended Abstract")
    # authors: two of three columns
    for p, a in zip((ps[3], ps[4]), AUTHORS):
        unwrap_hyperlinks(p)
        n = len(list(p._p.iter(W + 't')))
        base = [a[0], ' ', a[1]]
        if p is ps[3]:
            base.append(None)                      # drop the dagger
        rest = [' ' + a[2], ' ' + a[3], '', 'Bratislava,', ' ', '', '', 'Slovakia', ' ', a[4]]
        set_texts(p, base + rest[: n - len(base)])
    remove(ps[5])
    cols = ps[6]._p.find('.//' + W + 'cols')
    if cols is not None:
        cols.set(W + 'num', '2')

    # abstract
    clear(ps[10]); add_rich(ps[10], ABSTRACT if kind == 'paper' else EA_ABSTRACT)
    for i in (11, 12, 13, 14, 15, 19, 20, 21):
        remove(ps[i])
    if kind == 'paper':
        clear(ps[16]); ps[16].add_run("VYBSEM 2026 seminar paper, FIIT STU, Bratislava, Slovakia. Personal and classroom use is permitted.")
        remove(ps[17])
        clear(ps[18]); ps[18].add_run("© 2026 Copyright held by the owner/author(s).")
        clear(ps[23]); ps[23].add_run("• Applied computing → Law • Computing methodologies → Natural language generation")
        clear(ps[27]); ps[27].add_run("Arsenii Leno and Richard Marko. 2026. " + TITLE + ". In ")
        r = ps[27].add_run("VYBSEM 2026, FIIT STU, Bratislava, Slovakia"); r.italic = True
        ps[27].add_run(", 2 pages.")
    else:
        for i in (16, 17, 18, 22, 23, 26, 27):
            remove(ps[i])
    clear(ps[25]); ps[25].add_run(KEYWORDS)

    # body: delete template body and acknowledgments
    for i in range(28, 54):
        remove(ps[i])
    ref_head = ps[54]
    body = PAPER_BODY if kind == 'paper' else EA_BODY
    for item in body:
        if item[0] == 'h':
            p = ref_head.insert_paragraph_before('', style='Head1')
            r = p.add_run(item[1]); r.style = d.styles['Label']
            p.add_run(' ' + item[2])
        elif item[0] == 'p':
            p = ref_head.insert_paragraph_before('', style='Para')
            add_rich(p, cite(item[1], order))
        elif item[0] == 'fig':
            p = ref_head.insert_paragraph_before('', style='Image')
            p.add_run().add_picture('fig1.png', width=Inches(3.0))
            c = ref_head.insert_paragraph_before('', style='FigureCaption')
            add_rich(c, "**Figure 1: Outcomes on the 10 illustrative cases.**")
        elif item[0] == 'tab':
            c = ref_head.insert_paragraph_before('', style='TableCaption')
            c.paragraph_format.keep_with_next = True; add_rich(c, "**Table 1: Outcome per case type (A accurate, I incomplete, H hallucinated; Sup2: no conflict edge).**")
            t = d.add_table(rows=len(TABLE), cols=len(TABLE[0]))
            t.alignment = 1
            table_borders(t)
            for i, row in enumerate(TABLE):
                for j, val in enumerate(row):
                    cell = t.cell(i, j)
                    cell.width = Inches(0.4 if j == 0 else 0.4)
                    para = cell.paragraphs[0]
                    para.style = d.styles['Normal']
                    para.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                    pf = para.paragraph_format; pf.space_before = Pt(1); pf.space_after = Pt(1)
                    r = para.add_run(val); r.font.size = Pt(7.5); r.bold = (i == 0); pf.keep_with_next = i < len(TABLE) - 1
            if True:  # rule under the header row
                for cell in t.rows[0].cells:
                    tcPr = cell._tc.get_or_add_tcPr()
                    bd = OxmlElement('w:tcBorders'); e = OxmlElement('w:bottom')
                    e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4'); e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000')
                    bd.append(e); tcPr.append(bd)
            t.autofit = False
            widths = [0.4] + [0.38, 0.38, 0.38, 0.38, 0.42, 0.42, 0.38]
            for j, wd in enumerate(widths):
                t.columns[j].width = Inches(wd)
            tblPr = t._tbl.tblPr
            lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
            tw = tblPr.find(qn('w:tblW'))
            if tw is None:
                tw = OxmlElement('w:tblW'); tblPr.append(tw)
            tw.set(qn('w:w'), str(int(sum(widths) * 1440))); tw.set(qn('w:type'), 'dxa')
            for gc, wd in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), widths):
                gc.set(qn('w:w'), str(int(wd * 1440)))
            ref_head._p.addprevious(t._tbl)

    # references
    bibs = [p for p in d.paragraphs if p.style.name == 'Bib_entry']
    proto = bibs[0]._p
    for p in bibs:
        remove(p)
    anchor = ref_head._p
    for n, key in enumerate(order, 1):
        el = copy.deepcopy(proto)
        anchor.addnext(el); anchor = el
        p = docx.text.paragraph.Paragraph(el, ref_head._parent)
        clear(p)
        p.add_run(f'[{n}]'); p.add_run('\t')
        add_rich(p, REFS[key])
        p.paragraph_format.space_after = Pt(1)
    # metadata lines for the ACM tool
    for p in [p for p in d.paragraphs if p.style.name == 'MetadataHead']:
        remove(p)

    out = f'{OUTDIR}/{"VYBSEM_paper_Leno_Marko" if kind == "paper" else "VYBSEM_extended_abstract_Leno_Marko"}.docx'
    d.save(out)
    # running heads live in header XML
    tmp = out + '.tmp'
    with zipfile.ZipFile(out) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename.endswith('/'):
                continue
            data = zin.read(item.filename)
            if item.filename.startswith('word/header'):
                s = data.decode('utf8')
                s = s.replace('WOODSTOCK’18, June, 2018, El Paso, Texas USA', 'VYBSEM 2026, November 2026, Bratislava, Slovakia')
                s = s.replace('F. Surname et al.', 'A. Leno and R. Marko')
                s = s.replace('Insert Your Title Here', 'Citation Verification and Hallucination Reduction of LLMs')
                data = s.encode('utf8')
            zout.writestr(item, data)
    shutil.move(tmp, out)
    print('wrote', out)


for k in (sys.argv[3:] or ['abstract', 'paper']):
    build(k)
