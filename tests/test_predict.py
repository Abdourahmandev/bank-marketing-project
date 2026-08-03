"""Tests for prediction helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from bank_marketing.predict import (  # noqa: E402
    PREDICTED_LABEL_COLUMN,
    PREDICTED_TARGET_COLUMN,
    RANK_COLUMN,
    SCORE_COLUMN,
    load_pipeline,
    prediction_schema,
    prepare_prediction_features,
    save_pipeline,
    score_customers,
    top_recommendations,
)
from bank_marketing.preprocessing import DEPLOYMENT_FEATURES  # noqa: E402


class FakeProbabilityPipeline:
    classes_ = np.array([0, 1])

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        scores = features["age"].astype(float).clip(0, 100).to_numpy() / 100.0
        return np.column_stack([1.0 - scores, scores])


def prediction_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "age": 40,
        "campaign": 1,
        "days_since_previous_contact": 0,
        "previously_contacted": 0,
        "previous": 0,
        "emp_var_rate": 1.1,
        "cons_price_idx": 93.994,
        "cons_conf_idx": -36.4,
        "euribor3m": 4.857,
        "nr_employed": 5191.0,
        "job": "admin.",
        "marital": "married",
        "education": "university.degree",
        "default": "no",
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "month": "may",
        "day_of_week": "mon",
        "poutcome": "nonexistent",
    }
    row.update(overrides)
    return row


def test_prediction_schema_documents_deployable_features() -> None:
    schema = prediction_schema()

    assert schema["required_features"] == list(DEPLOYMENT_FEATURES)
    assert schema["excluded_features"] == ["duration"]


def test_prepare_prediction_features_selects_deployment_columns() -> None:
    frame = pd.DataFrame([prediction_row(duration=300)])

    features = prepare_prediction_features(frame)

    assert list(features.columns) == list(DEPLOYMENT_FEATURES)
    assert "duration" not in features.columns


def test_prepare_prediction_features_rejects_missing_column() -> None:
    frame = pd.DataFrame([prediction_row()]).drop(columns=["job"])

    with pytest.raises(ValueError, match="Colonnes de prediction manquantes"):
        prepare_prediction_features(frame)


def test_prepare_prediction_features_rejects_invalid_numeric_value() -> None:
    frame = pd.DataFrame([prediction_row(campaign="many")])

    with pytest.raises(ValueError, match="Colonnes numeriques invalides"):
        prepare_prediction_features(frame)


def test_score_customers_applies_threshold_and_ranks() -> None:
    frame = pd.DataFrame(
        [
            prediction_row(age=20),
            prediction_row(age=70),
            prediction_row(age=55),
        ]
    )

    scored = score_customers(
        FakeProbabilityPipeline(),
        frame,
        threshold=0.5,
        include_input_columns=True,
    )

    assert scored[SCORE_COLUMN].tolist() == [0.2, 0.7, 0.55]
    assert scored[PREDICTED_TARGET_COLUMN].tolist() == [0, 1, 1]
    assert scored[PREDICTED_LABEL_COLUMN].tolist() == ["no", "yes", "yes"]
    assert scored[RANK_COLUMN].tolist() == [3, 1, 2]
    assert "age" in scored.columns


def test_top_recommendations_returns_highest_scores() -> None:
    frame = pd.DataFrame([prediction_row(age=20), prediction_row(age=70)])
    scored = score_customers(FakeProbabilityPipeline(), frame, threshold=0.5)

    top = top_recommendations(scored, count=1)

    assert top.iloc[0][SCORE_COLUMN] == 0.7
    assert top.iloc[0][RANK_COLUMN] == 1


def test_save_and_load_pipeline_roundtrip(tmp_path: Path) -> None:
    pytest.importorskip("joblib")

    path = save_pipeline(FakeProbabilityPipeline(), tmp_path / "pipeline.joblib")
    loaded = load_pipeline(path)
    frame = pd.DataFrame([prediction_row(age=80)])
    scored = score_customers(loaded, frame, threshold=0.5)

    assert path.is_file()
    assert scored.iloc[0][SCORE_COLUMN] == 0.8
