# AMLynx
A deep learning-powered anti-money laundering engine combining adaptive rules and anomaly detection for banking systems.
AMLynx/
│── pyproject.toml
│── README.md
│── src/
│    ├── amlynx/
│    │    ├── __init__.py
│    │    ├── rules/
│    │    │    ├── __init__.py
│    │    │    ├── base.py
│    │    │    ├── amount_rule.py
│    │    │    ├── velocity_rule.py
│    │    │    └── country_rule.py
│    │    ├── anomaly/
│    │    │    ├── __init__.py
│    │    │    ├── detector.py
│    │    │    └── feature_engineering.py
│    │    ├── data/
│    │    │    ├── loader.py
│    │    │    └── preprocessing.py
│    │    ├── pipeline.py
│    │    └── utils.py
│── tests/
│    ├── test_rules.py
│    ├── test_anomaly.py
│    └── test_pipeline.py
