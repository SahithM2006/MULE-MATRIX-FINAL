# MULE MATRIX — Unified Financial Investigation Platform

### Unified Financial Investigation · Eight Algorithmic Engines · Original UI · End-to-End Evidence

MULE MATRIX is an independent, production-grade financial crime investigation and mule detection platform built entirely from scratch. It unifies synthetic multi-bank transaction normalization, bidirectional time-constrained BFS flow reconstruction, SHA-256 cryptographic e₹ token lineage verification, eight complementary algorithmic engines, explainable risk aggregation, held-out benchmark evaluation, incident response case management, and cryptographic audit logging into a cohesive Swiss Editorial Intelligence workspace.

---

## 1. Key Architectural Pillars

### Internal Investigation Flow
```
SELECT ACTIVITY → OBSERVE → TRACE → DETECT → RESPOND → PRESERVE EVIDENCE
```

1. **Observe**:
   - `Sentinel Command Radar`: Executive metrics, active alert stream, real transaction counts, and rapid scenario injection.
   - `Threat Stream`: Searchable, filterable real-time transaction ledger across multi-bank rails (UPI, IMPS, NEFT, RTGS).

2. **Trace**:
   - `Attack Graph`: Interactive Cytoscape.js directed multigraph with forward, backward, and bidirectional BFS traversals, chronological path validation, and explicit stop reasons (`OFF_RAMP_REACHED`, `MAX_HOPS_REACHED`, `LOOKBACK_OR_LOOKAHEAD_WINDOW_EXCEEDED`, `NO_ELIGIBLE_INCOMING_OR_OUTGOING_TRANSACTIONS`, `SEARCH_BUDGET_EXHAUSTED`).
   - `Token Forensics`: Cryptographic SHA-256 e₹ token lineage verification with RFC 8785 canonical JSON serialization, recursive hash chaining, and interactive tampering detection simulation.

3. **Detect**:
   - `Detection Lab`: 0–100 composite risk score, radar visualization, plain-English factual narrative synthesis, and full deep-dives into all eight algorithmic engines.
   - `Model Observatory`: Held-out synthetic benchmark evaluations, confusion matrices, latency metrics, and real model training statuses (`READY` / `NOT_TRAINED`).

4. **Respond**:
   - `Incident Response`: Case tracking, status workflows (`NEW` → `IN_REVIEW` → `ESCALATED` → `FROZEN` → `CLOSED`), investigator notes, and mandatory status change reasons.
   - `Evidence Vault`: Standalone downloadable HTML forensic dossiers and companion JSON packages with SHA-256 content verification hashes.
   - `Audit Ledger`: Cryptographically chained immutable ledger of all investigator actions with SHA-256 recursive verification.

5. **Utilities**:
   - `Scenario Simulator`: Explicit deterministic scenario generator (Rapid Pass-Through, Smurfing Fan-In, Mule Rings, Multi-Hop Layering, Cross-Bank Split-Merge).
   - `Investigation Replay`: Step-by-step chronological transaction playback.
   - `Rules & Limits`: Documented thresholds, units, and aggregation weights.
   - `System Health`: Backend, database, and engine operational telemetry.

---

## 2. All Eight Algorithmic Engines

| # | Algorithmic Engine | Implementation | Purpose & Capabilities |
|---|-------------------|----------------|------------------------|
| 1 | **Sliding-Window Temporal Velocity** | `VelocityEngine` | 10m, 1h, 24h rolling windows; burst detection (&ge;5 txs in 10m); pass-through ratio (&ge;85% in 1h); zero-division safe. |
| 2 | **SHA-256 Token-Lineage Verifier** | `LineageVerifier` | RFC 8785 canonical JSON serialization, recursive hash chaining, identifies first broken link under tampering. |
| 3 | **Time-Constrained BFS Tracer** | `BFSTracer` | Forward, backward, and bidirectional chronological graph traversals; cycle prevention; search budgets; precise stop reasons. |
| 4 | **Graph-Feature Extractor** | `FeatureExtractor` | 12 topological and flow features ($k_{in}, k_{out}, W_{in}, W_{out}$, fan-in, fan-out, degree ratio, clustering, component size, velocity, pass-through, burst); consistent across UI and ML models. |
| 5 | **Rule-Based Risk Engine** | `RuleEngine` | Explicit predicates with bounded contributions (R-101 to R-106); semantic lookalike guardrails for merchants and corporate payroll. |
| 6 | **Isolation Forest Anomaly Engine** | `IsolationForestEngine` | Unsupervised scikit-learn anomaly scoring with feature perturbation explainability; trained model persistence. |
| 7 | **Louvain Community Detection** | `LouvainCommunityEngine` | Projects multi-bank multigraph to weighted undirected graph; computes modularity and detects circular mule rings (&ge;75% internal density). |
| 8 | **Inductive GraphSAGE GNN** | `GraphSAGEEngine` | Genuine PyTorch 2-layer inductive neural network with Mean Aggregation; predicts calibrated mule probability on arbitrary subgraphs without retraining. |

---

## 3. Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Cytoscape.js, Recharts, Lucide React.
- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite (WAL mode).
- **Machine Learning & Graph**: PyTorch 2.14, NetworkX 3.5, scikit-learn 1.7, SciPy, Joblib.
- **Testing**: pytest, HTTPX, FastAPI TestClient.

---

## 4. Quick Start & Execution

### Prerequisites
- Python 3.10+ (Python 3.13 tested)
- Node.js 18+ & npm 9+

### Automated Launch
Run the provided launcher to start both services:
```powershell
# Windows PowerShell
.\start.ps1

# Or cross-platform Python
python start.py
```

### Manual Service Startup
1. **Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   - OpenAPI Docs: `http://127.0.0.1:8000/docs`

2. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   - Web Workspace: `http://localhost:5173`

---

## 5. Automated Testing & Verification

Run the comprehensive automated test suites:
```bash
cd backend

# 1. Test all 8 Algorithmic Engines
python -m pytest tests/test_algorithms.py -v

# 2. Test API Endpoints & Case Workflows
python -m pytest tests/test_api.py -v

# 3. Test Full 18-Point Acceptance Criteria
python -m pytest tests/test_e2e_acceptance.py -s -v
```

### Build Production Frontend:
```bash
cd frontend
npm run build
```

---

## 6. Project Structure

```
MULE MATRIX FINAL/
├── backend/
│   ├── app/
│   │   ├── algorithms/       # All 8 genuine algorithmic engines
│   │   │   ├── velocity_engine.py
│   │   │   ├── lineage_verifier.py
│   │   │   ├── bfs_tracer.py
│   │   │   ├── feature_extractor.py
│   │   │   ├── rule_engine.py
│   │   │   ├── isolation_forest.py
│   │   │   ├── louvain_engine.py
│   │   │   └── graphsage_engine.py
│   │   ├── models/           # SQLAlchemy 2.0 ORM schemas
│   │   ├── schemas/          # Pydantic v2 validation contracts
│   │   ├── services/         # Scenario generation, risk aggregation, case & audit services
│   │   ├── routers/          # API endpoints for Observe, Trace, Detect, Respond, Audit
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── saved_models/         # Persisted PyTorch GraphSAGE and scikit-learn artifacts
│   ├── tests/                # Automated pytest suites
│   ├── requirements.txt
│   └── seed_data.py          # Standalone dataset initialization & benchmark runner
├── frontend/
│   ├── src/
│   │   ├── components/       # Cytoscape directed canvas, RiskGauge, StatusBadge, Navbar
│   │   ├── pages/            # Sentinel, Threat Stream, Attack Graph, Token Forensics, etc.
│   │   ├── services/         # Typed API client
│   │   ├── types/            # TypeScript data contracts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── start.ps1                 # Windows PowerShell launcher
├── start.py                  # Cross-platform Python launcher
└── README.md
```

---

## 7. License & Integrity Guarantee
Built completely from scratch. No mock algorithm results, no hardcoded scores, and no ground-truth leakage into runtime inference.

