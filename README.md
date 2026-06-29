# DIkastes.ai

Multi-agent AI orchestration system designed to analyze legal cases, evaluate evidence based on Ukrainian legislation, and generate structured judicial decisions across three distinct scenarios (Lenient, Standard, Strict).

---

## 🎯 Project Vision & Core Goal
To build a modular, high-precision Python framework that leverages LLMs with long context windows (e.g., Gemini Pro) to completely eliminate hallucinations in legal analysis using isolated agent roles and structured state management(RAG).

---

## 🤖 Multi-Agent Swarm Architecture

The core architecture follows an **Orchestrator-Workers (Swarm)** pattern. Agents do not share prompts; 
they share a synchronized global state (`DikastesState`) to prevent context drift and performance degradation (Lost in the Middle).

[ Raw Case Materials / Factum ]
                                 │
                                 ▼
                ┌─────────────────────────────────┐
                │      1. Registrar Agent         │
                │  (Fact Extraction & De-noising) │
                └────────────────┬────────────────┘
                                 │
              Updates State.extracted_facts
                                 │
                                 ▼
         ┌───────────────────────┴───────────────────────┐
         ▼                                               ▼
┌───────────────────────────┐                   ┌───────────────────────────┐
│    2. Prosecutor Agent    │                   │      3. Advocate Agent    │
│ (Aggravating / Strict)    │                   │   (Mitigating / Lenient)  │
└────────────┬──────────────┘                   └────────────┬──────────────┘
             │                                               │
 Updates State.prosecution                       Updates State.defense
             │                                               │
             └───────────────────────┬───────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │        4. Judge Agent           │
                    │ (Weighs Arguments & Synthesizes)│
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                      [ Final Verdict: 3 Scenarios ]

## ⚙️ Architectural Specifications

### 1. Global State Management (`DikastesState`)
Every agent accepts the state object, executes its internal logic, and mutates only its designated key within the state.
* **`raw_case`**: Original unformatted narrative or case files.
* **`extracted_facts`**: Chronology, legally significant actions, identified entities.
* **`prosecution_analysis`**: Articles violated, maximum statutory penalties, aggravating factors.
* **`defense_analysis`**: Mitigating circumstances, procedural errors, minimum sanctions.
* **`final_verdicts`**: Synthesized output containing 3 distinct branches (Soft, Standard, Heavy).

### 2. Output Scenarios
* **⚖️ Lenient:** Minimum fine, acquittal pathways, probation options, or lowest statutory boundary.
* **⚖️ Standard:** Established judicial practice average, typical balanced sentencing.
* **⚖️ Strict:** Maximum penalty under the specific article, comprehensive qualification of all offenses.

### 3. Anti-Hallucination & RAG Guardrails
* **Strict Source Grounding:** Every legal reference must cite real articles of Ukrainian Codes (CCU, CPCU, CCV, etc.).
* **Zero-Imagination Policy:** If the context lacks data for a specific legal element, the agent must write `"Insufficient data in context"`.

---

## 🛠️ Tech Stack & Concepts to Implement
* **Language:** Python 3.11+
* **AI Core:** Google Gemini Pro API (Utilizing up to 1-2M token context window for loading entire codes).
* **Paradigms:** Agentic orchestration, RAG (Retrieval-Augmented Generation), Backpropagation & weights intuition, System infrastructure optimization.

---

## 📝 Instructions for AI Coding Assistants (Vibe Coding Mode)
1. **Maintain Context:** Read the entire `DikastesState` implementation before editing any agent logic.
2. **Role Isolation:** When writing prompts or logic for the Prosecutor, do NOT include defensive arguments, and vice versa. Keep the roles pure.
3. **No Code Bloat:** Prefer modular, testable Python classes. Avoid massive single-prompt scripts.
