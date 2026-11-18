| ID | Case | Error type | Expected V code | V on A's answer | A | A+V | B | C |
|---|---|---|---|---|---|---|---|---|
| T01 | V1 | Valid control | VALID | SK-A1-v2: VALID | A | A | A | A |
| T02 | V2 | Valid control | VALID | SK-C3: VALID | A | A | A | A |
| T03 | F1 | Fabricated premise | NONEXISTENT | SK-A1-v2: VALID, SK-A1a: NONEXISTENT | H | A | H | A |
| T04 | F2 | Fabricated premise | NONEXISTENT | SK-L4: VALID, SK-L4b: NONEXISTENT | H | A | H | A |
| T05 | R1 | Repealed version | NOT_IN_FORCE | SK-A1-v1: NOT_IN_FORCE | H | I | A | A |
| T06 | R2 | Repealed version | NOT_IN_FORCE | SK-H2-v1: NOT_IN_FORCE | H | I | A | A |
| T07 | J1 | Wrong jurisdiction (Czech twin) | WRONG_JURISDICTION | CZ-C3: WRONG_JURISDICTION | H | I | A | A |
| T08 | S1 | Lex superior, conflict recorded | OVERRIDDEN | SK-L4-NV: OVERRIDDEN | H | I | A | A |
| T09 | S2 | Lex superior, conflict not recorded | VALID (Type II, invisible to V) | SK-W5-NV: VALID | H | H | H | H |
| T10 | M1 | Misgrounding | VALID (Type II, invisible to V) | SK-P6-2: VALID | H | H | H | H |
| | **Total** | | | | 2A/0I/8H | 4A/4I/2H | 6A/0I/4H | 8A/0I/2H |

A = accurate, I = incomplete, H = hallucinated (Magesh et al., 2025). A+V applies the verifier V to A's answer, without B's jurisdiction, validity and rank filters.
