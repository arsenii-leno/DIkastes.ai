# ⚖️ DIkastes.ai — LegalTech Statutory & Case Law Assistant

**Status:** 🧪 Research / Bachelor Prototype | **Domain:** Legal Informatics | **Stack:** Python + LLMs

An AI-driven assistant combining Large Language Models with domain-specific legal knowledge retrieval (RAG) to assist law students and practitioners in statutory cross-referencing and precedent analysis.

---

## 🎯 Architectural Pipeline

┌─────────────────────────────────────────────────────────┐
│                 Natural Language Legal Query             │
├─────────────────────────────────────────────────────────┤
│            Embeddings & Vector Retrieval Pipeline       │
│  ├── Legal Document Ingestion (Statutes & Court Records)│
│  └── Semantic Chunking & Relevance Scoring              │
├─────────────────────────────────────────────────────────┤
│            LLM Context Assembly & Strict Prompting       │
│  └── Citation-backed response generation                │
└─────────────────────────────────────────────────────────┘


---

## 🚀 Key Objectives

- **Grounded Legal Retrieval:** Reduces model hallucinations by injecting direct citations and statutory articles into the context window.
- **Multi-Jurisdiction Alignment:** Structured for comparative analysis across domestic and European legal frameworks.
- **Dual Domain Synergy:** Engineered at the intersection of Computer Science (FIIT STU) and Jurisprudence (UzhNU).

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI / LangChain
- **Embeddings & LLMs:** OpenAI / Local HuggingFace embeddings
- **Data Stores:** SQLite / Vector Store (FAISS/Chroma)

---

## 📄 License
Academic & Research Project © 2026 Arsenii Leno
