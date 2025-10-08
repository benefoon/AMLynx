# 🦊 AMLynx

> **AMLynx** is an advanced **Anti-Money Laundering (AML) intelligence framework** for detecting suspicious financial activities using a **hybrid approach** that blends **rule-based systems** with **machine-learning anomaly detection**.

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](#license)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#requirements)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](#api)
[![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)]()

---

## 📘 Table of Contents

* [Overview](#overview)
* [Key Features](#key-features)
* [Architecture](#architecture)
* [Folder Structure](#folder-structure)
* [Quick Start (Docker)](#quick-start-docker)
* [Development Setup](#development-setup)
* [Configuration](#configuration)
* [Data Pipeline](#data-pipeline)
* [Rule Engine](#rule-engine)
* [Anomaly Detection](#anomaly-detection)
* [Hybrid Scoring](#hybrid-scoring)
* [API](#api)
* [Logging & Monitoring](#logging--monitoring)
* [Testing](#testing)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)

---

## 🧠 Overview

**AMLynx** provides a modular, production-ready foundation for **automated AML screening** in financial systems.
It unifies:

* **Business rules** (expert knowledge)
* **Anomaly detection models** (data-driven insight)
* **Hybrid scoring** for explainable and tunable alerts

Built with **FastAPI**, **SQLAlchemy**, and **modern ML libraries**, AMLynx is designed for **banks, fintechs, and regulators** who need transparency, extensibility, and auditability in their AML workflows.

---

## ✨ Key Features

✅ **Modular Architecture** – Independent, pluggable modules for rules, models, features, and scoring
✅ **Hybrid Risk Scoring** – Combine ML anomaly scores and rule-based logic
✅ **FastAPI REST Interface** – Production-ready API with OpenAPI documentation
✅ **Pydantic Schemas** – Type-safe validation for all inputs/outputs
✅ **Batch & Streaming ETL** – Supports both batch ingestion and near-real-time pipelines
✅ **SQLAlchemy ORM** – Database-agnostic (PostgreSQL, SQLite, etc.)
✅ **Unified Logging** – Centralized JSON logging for analytics and compliance
✅ **Containerized Deployment** – Ship and scale with Docker Compose or Kubernetes
✅ **Extensible** – Add new anomaly models, rules, or scoring logic with minimal coupling

---

## 🧩 Architecture

AMLynx follows a **layered architecture**:

```
                ┌─────────────────────────────┐
                │         API Layer           │
                │ (FastAPI REST + Schemas)    │
                └──────────────┬──────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │       Pipeline Layer      │
                 │ (ETL → Features → Rules → │
                 │  Anomaly → Hybrid Scoring)│
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │        Data Layer         │
                 │ (DB Models + Storage)     │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │   Common & Core Utilities │
                 │ (Config, Logging, Helpers)│
                 └───────────────────────────┘
```

---

## 📁 Folder Structure

| Directory         | Description                                                                 |
| ----------------- | --------------------------------------------------------------------------- |
| **aml/**          | Core AML intelligence logic — primary anomaly model(s) and risk aggregation |
| **anomaly/**      | Low-level detectors (Isolation Forest, LOF, etc.) and explainers            |
| **api/**          | FastAPI app exposing endpoints for scoring, transactions, and health checks |
| **common/**       | Logging setup, configuration management, and shared utilities               |
| **data/**         | ETL batch scripts for data cleaning, transformation, and ingestion          |
| **db/**           | SQLAlchemy ORM models and session management                                |
| **features/**     | Feature extraction and feature-store logic                                  |
| **pipeline/**     | Orchestrates end-to-end scoring workflow                                    |
| **rules_engine/** | Business rule registration and evaluation engine                            |
| **schemas/**      | Pydantic models for input/output validation                                 |
| **scoring/**      | Hybrid logic combining rule and anomaly scores                              |

---

## ⚡ Quick Start (Docker)

```bash
git clone https://github.com/benefoon/AMLynx.git
cd AMLynx

# 1️⃣ Configure environment
cp .env.example .env

# 2️⃣ Launch services
docker compose up --build

# 3️⃣ (Optional) Seed demo data
docker compose exec api python scripts/seed_data.py

# 4️⃣ Access API docs
http://localhost:8000/docs
```

---

## 💻 Development Setup

### Requirements

* Python 3.10+
* FastAPI, SQLAlchemy, scikit-learn, pandas
* Docker (optional for deployment)

### Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.api.app:app --reload --port 8000
```

Run tests:

```bash
pytest -q
```

---

## ⚙️ Configuration

Defined in `.env` or system environment variables.
Common entries:

```ini
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/amlynx
MODEL_PATH=./models/isolation_forest.pkl
ENABLE_RULES=true
ENABLE_GRPC=false
API_PORT=8000
LOG_LEVEL=INFO
```

---

## 🧬 Data Pipeline

1. **ETL Stage** (`data/etl_batch.py`)

   * Cleans and normalizes incoming transaction data.
   * Handles missing fields, currency conversion, and schema validation.

2. **Feature Extraction** (`features/store.py`)

   * Generates statistical or behavioral features (velocity, frequency, deviation).
   * Maintains feature cache for repeated scoring.

3. **Rule Evaluation** (`rules_engine/engine.py`)

   * Evaluates deterministic business rules.

4. **Anomaly Detection** (`aml/anomaly.py`, `anomaly/detector.py`)

   * Runs machine-learning models on feature vectors.

5. **Hybrid Scoring** (`scoring/hybrid.py`)

   * Combines ML and rule outputs into unified risk score.

---

## 🧾 Rule Engine

Rules are defined in JSON/YAML or Python DSL format and evaluated in `rules_engine/engine.py`.

Example:

```yaml
id: R001
name: High-Value Offshore
condition: transaction.amount_usd > 10000 and transaction.country in ["KY", "PA", "VG"]
action:
  score: +50
  reason: "Large transaction to offshore jurisdiction"
```

Each rule returns:

```json
{
  "rule_id": "R001",
  "triggered": true,
  "score": 50,
  "reason": "Large transaction to offshore jurisdiction"
}
```

---

## 🤖 Anomaly Detection

Defined in:

* `aml/anomaly.py`
* `anomaly/detector.py`

Supports:

* **Isolation Forest**
* **Local Outlier Factor**
* **Autoencoder (planned)**

Each detector exposes:

```python
predict(X) -> np.ndarray
score(X) -> List[float]
explain(X) -> Dict[str, float]
```

Example usage:

```python
from aml.anomaly import AnomalyModel
model = AnomalyModel.load("models/isolation_forest.pkl")
scores = model.score(batch_features)
```

---

## ⚖️ Hybrid Scoring

Combines rule-based and model-based results:

```python
final_score = 0.6 * anomaly_score + 0.4 * rule_score
alert = final_score > threshold
```

Configurable weights are set in `.env` or `common/config.py`.
Returns risk levels (Low / Medium / High) with explainability.

---
## 🌐 API

| Method | Endpoint              | Description                         |
| ------ | --------------------- | ----------------------------------- |
| `POST` | `/transactions/score` | Score one or more transactions      |
| `GET`  | `/rules`              | List all active rules               |
| `POST` | `/rules/test`         | Test a new rule against sample data |
| `GET`  | `/healthz`            | Health check                        |

OpenAPI docs: **`/docs`**
ReDoc: **`/redoc`**

---

