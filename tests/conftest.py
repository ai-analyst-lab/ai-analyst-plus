"""
Shared pytest fixtures for AI Analyst test suite.

Provides deterministic synthetic data, temporary directory structures,
and reusable test infrastructure for all test modules.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import yaml

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Pytest configuration & custom markers
# ---------------------------------------------------------------------------

def pytest_configure(config):
    """Register custom markers used across the test suite."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with -m 'not slow')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "statistical: marks tests as statistical tests")
    config.addinivalue_line("markers", "e2e: marks local end-to-end smoke tests")
    config.addinivalue_line("markers", "external: marks tests requiring external services or credentials")


# ---------------------------------------------------------------------------
# Synthetic data fixtures -- deterministic (seeded) for reproducibility
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_users():
    """100-row synthetic user DataFrame with deterministic data.

    Columns: user_id, signup_date, device, country, acquisition_channel, is_active
    Seed: 42
    """
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "user_id": range(1, n + 1),
        "signup_date": pd.date_range("2024-01-01", periods=n, freq="D"),
        "device": np.random.choice(
            ["desktop", "mobile", "tablet"], n, p=[0.5, 0.35, 0.15]
        ),
        "country": np.random.choice(
            ["US", "UK", "DE", "FR", "JP"], n, p=[0.4, 0.2, 0.15, 0.15, 0.1]
        ),
        "acquisition_channel": np.random.choice(
            ["organic", "paid", "referral", "social"], n, p=[0.3, 0.3, 0.2, 0.2]
        ),
        "is_active": np.random.choice([True, False], n, p=[0.7, 0.3]),
    })


@pytest.fixture
def synthetic_orders():
    """500-row synthetic order DataFrame with deterministic data.

    Columns: order_id, user_id, order_date, amount, status, category
    Seed: 42
    """
    np.random.seed(42)
    n = 500
    return pd.DataFrame({
        "order_id": range(1, n + 1),
        "user_id": np.random.randint(1, 101, n),
        "order_date": pd.date_range("2024-01-01", periods=n, freq="4h"),
        "amount": np.round(np.random.lognormal(3.5, 1.0, n), 2),
        "status": np.random.choice(
            ["completed", "cancelled", "pending", "refunded"],
            n,
            p=[0.7, 0.1, 0.15, 0.05],
        ),
        "category": np.random.choice(
            ["electronics", "clothing", "food", "home", "books"], n
        ),
    })


@pytest.fixture
def synthetic_products():
    """20-row synthetic product DataFrame.

    Columns: product_id, name, category, price, is_active
    """
    return pd.DataFrame({
        "product_id": range(1, 21),
        "name": [f"Product {i}" for i in range(1, 21)],
        "category": (
            ["electronics"] * 4
            + ["clothing"] * 4
            + ["food"] * 4
            + ["home"] * 4
            + ["books"] * 4
        ),
        "price": [
            29.99, 49.99, 99.99, 199.99,
            19.99, 39.99, 59.99, 79.99,
            5.99, 9.99, 14.99, 24.99,
            34.99, 54.99, 74.99, 94.99,
            12.99, 17.99, 22.99, 27.99,
        ],
        "is_active": [True] * 18 + [False] * 2,
    })


# ---------------------------------------------------------------------------
# Data-quality edge-case fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def dirty_orders():
    """100-row DataFrame with known data quality issues for testing validators.

    Issues present:
    - 5 duplicate order_ids (rows 96-100 duplicate IDs 95-99)
    - 10% null user_ids
    - 10 null order_dates
    - Negative amount (-10.0), zero amount, extreme outlier (1e7), 2 null amounts
    """
    np.random.seed(99)
    n = 100
    df = pd.DataFrame({
        "order_id": list(range(1, 96)) + [95, 96, 97, 98, 99],  # 5 duplicate IDs
        "user_id": list(range(1, 91)) + [None] * 10,  # 10% null user_ids
        "order_date": (
            list(pd.date_range("2024-01-01", periods=90, freq="D")) + [None] * 10
        ),
        "amount": (
            list(np.round(np.random.lognormal(3.5, 1.0, 95), 2))
            + [-10.0, 0.0, 1e7, None, None]
        ),
        "status": np.random.choice(["completed", "cancelled", "pending"], n),
        "category": np.random.choice(["electronics", "clothing", "food"], n),
    })
    return df


# ---------------------------------------------------------------------------
# Simpson's Paradox fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simpsons_paradox_data():
    """DataFrame exhibiting Simpson's Paradox (UC Berkeley admissions pattern).

    Overall: Group B has higher admission rate (61.3% vs 50.0%).
    Per department: Group A has higher admission rate in every department.

    Dept A (easy): A=80/100 (80.0%), B=46/60 (76.7%)  -> A > B
    Dept B (hard): A=20/100 (20.0%), B=3/20  (15.0%)  -> A > B

    The paradox arises because Group A disproportionately applies to the
    hard department (100 of 200 in Dept B), while Group B mostly applies
    to the easy department (60 of 80 in Dept A).
    """
    data = []
    # Dept A: easy to get in
    data.extend([{"group": "A", "department": "A", "admitted": 1}] * 80)
    data.extend([{"group": "A", "department": "A", "admitted": 0}] * 20)
    data.extend([{"group": "B", "department": "A", "admitted": 1}] * 46)
    data.extend([{"group": "B", "department": "A", "admitted": 0}] * 14)
    # Dept B: hard to get in
    data.extend([{"group": "A", "department": "B", "admitted": 1}] * 20)
    data.extend([{"group": "A", "department": "B", "admitted": 0}] * 80)
    data.extend([{"group": "B", "department": "B", "admitted": 1}] * 3)
    data.extend([{"group": "B", "department": "B", "admitted": 0}] * 17)
    return pd.DataFrame(data)


@pytest.fixture
def no_paradox_data():
    """DataFrame with consistent direction across all segments.

    Group X has ~70% rate, Group Y has ~30% rate in every department.
    No Simpson's Paradox present -- direction is consistent.
    """
    np.random.seed(42)
    data = []
    for dept in ["A", "B", "C"]:
        for group in ["X", "Y"]:
            n = 50
            rate = 0.7 if group == "X" else 0.3
            admitted = np.random.binomial(1, rate, n)
            for a in admitted:
                data.append({
                    "group": group,
                    "department": dept,
                    "admitted": int(a),
                })
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Temporary directory fixtures for .knowledge/ structure
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_knowledge_dir(tmp_path):
    """Create a temporary .knowledge directory structure for testing.

    Structure created:
        .knowledge/
            active.yaml
            datasets/
            corrections/
            learnings/
            query-archaeology/
            analyses/
            global/

    Returns the Path to the .knowledge directory.
    """
    knowledge = tmp_path / ".knowledge"
    knowledge.mkdir()

    (knowledge / "active.yaml").write_text(
        "active_dataset: test-dataset\nactive_organization: test-org\n"
    )
    (knowledge / "datasets").mkdir()
    (knowledge / "corrections").mkdir()
    (knowledge / "learnings").mkdir()
    (knowledge / "query-archaeology").mkdir()
    (knowledge / "analyses").mkdir()
    (knowledge / "global").mkdir()

    return knowledge


@pytest.fixture
def tmp_org_dir(tmp_knowledge_dir):
    """Create a temporary organization directory with entity index for testing.

    Builds on tmp_knowledge_dir. Creates:
        .knowledge/organizations/test-org/
            entities/entity-index.yaml   (10 aliases, 5 entities, relationships)
            business/glossary/terms.yaml

    Returns the Path to the organization directory.
    """
    org_dir = tmp_knowledge_dir.parent / ".knowledge" / "organizations" / "test-org"
    org_dir.mkdir(parents=True)

    # -- Entity index --
    entities_dir = org_dir / "entities"
    entities_dir.mkdir()

    entity_index = {
        "schema_version": 1,
        "aliases": {
            "conversion rate": {"entity": "conversion_rate", "type": "metric"},
            "cvr": {"entity": "conversion_rate", "type": "metric"},
            "conv rate": {"entity": "conversion_rate", "type": "metric"},
            "daily active users": {"entity": "dau", "type": "metric"},
            "dau": {"entity": "dau", "type": "metric"},
            "marketplace": {"entity": "marketplace", "type": "product"},
            "mp": {"entity": "marketplace", "type": "product"},
            "payments": {"entity": "payments", "type": "product"},
            "gmv": {"entity": "gmv", "type": "metric"},
            "gross merchandise value": {"entity": "gmv", "type": "metric"},
        },
        "entities": {
            "conversion_rate": {
                "type": "metric",
                "display_name": "Conversion Rate",
                "definition": "Orders / Sessions",
                "tables": ["events", "orders"],
            },
            "dau": {
                "type": "metric",
                "display_name": "Daily Active Users",
                "definition": "COUNT(DISTINCT user_id) per day",
                "tables": ["events"],
            },
            "marketplace": {
                "type": "product",
                "display_name": "Marketplace",
                "tables": ["orders", "products", "sessions"],
                "team": "commerce",
            },
            "payments": {
                "type": "product",
                "display_name": "Payments",
                "tables": ["transactions"],
                "team": "fintech",
            },
            "gmv": {
                "type": "metric",
                "display_name": "GMV",
                "definition": "SUM(order_total)",
                "tables": ["orders"],
                "product": "marketplace",
            },
        },
        "relationships": {
            "marketplace": {"metrics": ["conversion_rate", "gmv"], "team": "commerce"},
            "payments": {"metrics": [], "team": "fintech"},
            "conversion_rate": {"product": "marketplace"},
            "gmv": {"product": "marketplace"},
            "dau": {},
        },
    }

    with open(entities_dir / "entity-index.yaml", "w") as f:
        yaml.dump(entity_index, f, default_flow_style=False)

    # -- Business context / glossary --
    business_dir = org_dir / "business"
    business_dir.mkdir()
    (business_dir / "glossary").mkdir()

    glossary = {
        "terms": [
            {
                "term": "GMV",
                "definition": "Gross Merchandise Value",
                "aliases": ["gross merchandise value"],
            },
            {
                "term": "Take Rate",
                "definition": "Revenue / GMV",
                "aliases": ["commission rate"],
            },
        ]
    }

    with open(business_dir / "glossary" / "terms.yaml", "w") as f:
        yaml.dump(glossary, f, default_flow_style=False)

    return org_dir


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def fixture_dir():
    """Return path to the test fixtures directory."""
    return FIXTURES_DIR
