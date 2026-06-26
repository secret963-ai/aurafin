[README.md](https://github.com/user-attachments/files/29394956/README.md)
# AuraFin: Financial Resilience & Employment Accelerator

> *Replacing debt penalties with human potential.*

AuraFin is a multi-agent AI system built on Google ADK 2.0 that transforms non-performing debt into active labor assets through AI-driven skill matching, tokenized privacy referrals, and smart escrow settlement.

---

## The Problem

Defaulting borrowers are not worthless assets — they are skilled people with a temporary liquidity problem. The conventional collections system destroys value for everyone: lenders spend more on litigation than they recover, borrowers suffer lasting financial damage, and society loses productive workers.

AuraFin reframes the question: instead of *"How do we recover this debt?"* it asks *"How do we unlock the value already inside this person?"*

---

## Agent Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Workflow Coordinator               │
│                    (ADK 2.0 Core)                    │
└──────┬──────────┬──────────┬────────────┬────────────┘
       │          │          │            │
  Trigger    Mediation   Skill       Escrow    Oversight
   Agent      Agent     Matcher      Agent      Agent
              (ZKP)    (Gemini)    (MCP/SC)   (HITL)
```

| Agent | Role |
|---|---|
| **Trigger Agent** | Monitors installment ledger; fires on 2-installment delay |
| **Mediation Agent** | Generates tokenized referral; obtains consumer opt-in |
| **Skill Matcher Agent** | Semantic skill-to-role matching via Gemini 2.0 Flash |
| **Escrow Agent** | Activates smart contract; routes wages via MCP server |
| **Oversight Agent** | Human-in-the-loop escalation for edge cases |

---

## Tech Stack

- **Agent Framework:** Google ADK 2.0
- **LLM:** Gemini 2.0 Flash
- **MCP Server:** Custom SQLite-backed MCP server
- **Data Store:** SQLite (ledger, escrow state, referral tokens)
- **Privacy:** Tokenized Referral (ZKP-inspired anonymization)
- **Compliance:** GDPR-ready, Fair Wage Floor enforcement

---

## MCP Tools

| Tool | Description |
|---|---|
| `check_installment_status` | Query ledger for payment delays |
| `generate_referral_token` | Create anonymized consumer token |
| `query_job_market` | Fetch live job demand signals |
| `activate_escrow_contract` | Initialize smart escrow settlement |

---

## Decision Flow

```
2-Installment Delay
        │
        ▼
Consumer Unable to Pay?
   No ──────────────► Direct Automated Settlement
   Yes
        │
        ▼
Anonymized Referral to CSC
        │
        ▼
AI Skill Matching (Gemini)
        │
        ▼
Employer Match Found?
   No ──────────────► Oversight Agent (Human Review)
   Yes
        │
        ▼
Smart Escrow Activation
        │
        ▼
Debt Cleared / Job Secured ✓
```

---

## Setup

### Prerequisites
```bash
python >= 3.11
google-adk >= 2.0.0
```

### Install
```bash
git clone https://github.com/YOUR_USERNAME/aurafin
cd aurafin
pip install -r requirements.txt
```

### Configure
```bash
cp .env.example .env
# Add your GOOGLE_API_KEY
```

### Run
```bash
python main.py
```

---

## Ethical Design

- **Voluntary:** Consumer opt-in required at every stage
- **Private:** Employers never see financial history — only skills
- **Fair:** Algorithmic Fair Wage Floor prevents exploitation
- **Accountable:** Full audit trail; human escalation for edge cases

---

## Economic Impact

| Metric | Traditional | AuraFin |
|---|---|---|
| Recovery Cost | High (litigation) | Low (AI mediation) |
| Asset Status | Non-Performing | Labor-backed |
| Time to Recovery | 12–36 months | 3–9 months |
| Customer Relationship | Destroyed | Rehabilitated |

---

## Vision

Debt, unemployment, and inflation form a triangle. AuraFin breaks it — keeping people inside the productive economy at their moment of greatest vulnerability.

*Built with Google ADK 2.0 · Gemini 2.0 Flash · MCP Server · Smart Escrow*
