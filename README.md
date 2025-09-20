# AMLynx
A deep learning-powered anti-money laundering engine combining adaptive rules and anomaly detection for banking systems.

AMLynx/
├── pyproject.toml
├── docker-compose.yml
├── .env.example
├── README.md
├── scripts/
│   └── seed_data.py
├── src/
│   ├── api/                       # FastAPI microservices (REST + gRPC)
│   │   ├── gateway/               # auth, routing, API gateway config
│   │   ├── transactions/          # ingestion & scoring endpoints
│   │   └── rules_engine/          # rule CRUD + evaluation endpoints
│   ├── common/
│   │   └── config.py
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   ├── data/
│   │   └── etl.py
│   ├── rules_engine/
│   │   └── engine.py
