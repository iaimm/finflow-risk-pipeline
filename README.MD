# FinFlow Risk Pipeline

A financial transaction data pipeline built with Python.

## Current Features

- Structured domain models for customers, accounts, and transactions
- Deterministic mock-data generation
- CSV output for subsequent ETL processing
- Automated data consistency tests

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

Generate Mock Data
bash
python -m finflow.pipelines.generate_mock_data --transactions 100
Run Tests
bash
pytest -q
