![Vanguard](https://img.shields.io/badge/Vanguard-ESG%20Compliance%20Auditor-059669?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1c1c1c?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=flat-square&logo=pandas)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**ESG compliance auditor — map legacy ERP ledgers to GHG Protocol Scope 1/2/3 emissions.**

---

## 🏗️ Pipeline

```mermaid
graph LR
    subgraph Input
        ERP[Legacy ERP<br/>Ledger Data]
        RULES[GHG Protocol<br/>Ruleset]
    end
    subgraph LangGraph Pipeline
        EXTRACT[Extract<br/>Activity Data]
        MAP[Map<br/>Emission Factors]
        CALC[Calculate<br/>Scope 1/2/3]
        AUDIT[Audit<br/>Discrepancies]
        REPORT[Generate<br/>Report]
    end
    subgraph Output
        RPT[Compliance<br/>Report]
        EMISSIONS[Emissions<br/>Summary]
    end
    ERP --> EXTRACT
    RULES --> MAP
    EXTRACT --> MAP
    MAP --> CALC
    CALC --> AUDIT
    AUDIT --> REPORT
    REPORT --> RPT
    REPORT --> EMISSIONS
```

---

## ✨ Features

- **ERP extraction** — read legacy ledger formats (CSV, Excel, DB)
- **Emission factor mapping** — match activities to GHG Protocol factors
- **Scope 1/2/3 calculation** — comprehensive emissions accounting
- **Discrepancy detection** — flag missing or inconsistent data
- **Compliance reporting** — structured reports with methodology notes

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python -m vanguard.audit --ledger emissions_2024.csv --rules ghg_protocol.json
```

---

## 📁 Project Structure

```
Vanguard/
├── vanguard/
│   ├── graph.py           # LangGraph pipeline
│   ├── extract.py         # ERP data extraction
│   ├── mapper.py          # Emission factor mapping
│   ├── calculator.py      # Scope 1/2/3 math
│   ├── audit.py           # Discrepancy detection
│   └── reporter.py        # Compliance report generation
├── tests/
└── README.md
```

---

## 📄 License

MIT © Md Sadman Bin Masud
