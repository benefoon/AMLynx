# AMLynx

> A deep learning–powered anti-money-laundering (AML) engine that blends adaptive rules with anomaly detection to surface suspicious activity in financial transactions. ([GitHub][1])

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](#license)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](#requirements)
[![API](https://img.shields.io/badge/API-FastAPI-009688.svg)](#api)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](#roadmap)

AMLynx is built as a set of lightweight services for **ingestion**, **scoring**, and **explanation**, exposing **REST** endpoints (and optional **gRPC**) for integration with ba# AMLynx

> A deep learning–powered anti-money-laundering (AML) engine that blends adaptive rules with anomaly detection to surface suspicious activity in financial transactions. ([GitHub][1])

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](#license)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](#requirements)
[![API](https://img.shields.io/badge/API-FastAPI-009688.svg)](#api)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](#roadmap)

AMLynx is built as a set of lightweight services for **ingestion**, **scoring**, and **explanation**, exposing **REST** endpoints (and optional **gRPC**) for integration with banking systems and case-management tools.

---
## Table of Contents

* [Why AMLynx?](#why-amlynx)
* [Features](#features)
* [Architecture](#architecture)
* [Quickstart (Docker)](#quickstart-docker)
* [Local Development](#local-development)
* [Configuration](#configuration)
* [Data Flow](#data-flow)
* [Rules Engine](#rules-engine)
* [Anomaly Detection](#anomaly-detection)
* [API](#api)
* [Testing](#testing)
* [Performance & Scaling](#performance--scaling)
* [Security & Compliance](#security--compliance)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)

---
## Why AMLynx?

Most AML stacks are either rigid **rule systems** (high false positives) or opaque **ML models** (hard to explain). AMLynx fuses both:

* **Rules** for deterministic business policy
* **Unsupervised models** to catch **unknown-unknowns**
* **Explainability** so analysts can trust and tune the system

---
## Features

* **Microservices** with FastAPI (REST) and optional gRPC gateway for low-latency scoring. ([GitHub][1])
* **Modular rules engine** with CRUD for rules and real-time evaluation. ([GitHub][1])
* **Anomaly detection** pipeline for transaction-level and customer-level monitoring.
* **ETL utilities** to clean/normalize raw feeds before scoring. ([GitHub][1])
* **SQLAlchemy models** and DB session management for portability. ([GitHub][1])
* **Seed data** script to bootstrap a demo environment. ([GitHub][1])
* **Docker** support for one-command spin-up. (Repo ships a `docker-compose.yml`.) ([GitHub][2])
* **Tests** to keep behavior stable while you iterate. ([GitHub][1])

---

## Architecture

```
AMLynx/
├── pyproject.toml                # Project deps & tooling
├── docker-compose.yml            # Dev stack (API + DB + extras)
├── .env.example                  # Config template
├── scripts/
│   └── seed_data.py              # Load demo fixtures
├── src/
│   ├── api/                      # Service layer (REST + gRPC)
│   │   ├── gateway/              # Auth, routing, gateway config
│   │   ├── transactions/         # Ingestion & scoring endpoints
│   │   └── rules_engine/         # Rule CRUD + evaluation endpoints
│   ├── common/
│   │   └── config.py             # Settings & env parsing
│   ├── db/
│   │   ├── models.py             # SQLAlchemy ORM models
│   │   └── session.py            # Session/engine management
│   ├── data/
│   │   └── etl.py                # Transforms & validators
│   └── rules_engine/
│       └── engine.py             # Rule registration & execution
└── tests/                        # Unit/integration tests
```

*The folders and service split are taken from the repo layout.* ([GitHub][1])

---
