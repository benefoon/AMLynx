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
