"""Tests des utilitaires de modelisation scikit-learn."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from bank_marketing.modeling import (  # noqa: E402
    UNKNOWN_CATEGORY_STRATEGY,
    UNKNOWN_MISSING_STRATEGY,
    build_model_pipeline,
    controlled_tuning_specs,
    evaluate_binary_predictions,
    predictions_from_threshold,
    replace_unknown_with_missing,
    split_silver_frame,
    threshold_for_top_budget,
)
from bank_marketing.preprocessing import (  # noqa: E402
    DEPLOYMENT_FEATURES,
    SILVER_TARGET_COLUMN,
    SOURCE_ROW_COLUMN,
    SPLIT_COLUMN,
)


def silver_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "age": 40,
        "job": "admin.",
        "marital": "married",
        "education": "university.degree",
        "default": "no",
        "housing": "yes",
        "loan": "no",
        "contact": "cellular",
        "month": "may",
        "day_of_week": "mon",
        "duration": 100,
        "campaign": 1,
        "days_since_previous_contact": 0,
        "previously_contacted": 0,
        "previous": 0,
        "poutcome": "nonexistent",
        "emp_var_rate": 1.1,
        "cons_price_idx": 93.994,
        "cons_conf_idx": -36.4,
        "euribor3m": 4.857,
        "nr_employed": 5191.0,
        SILVER_TARGET_COLUMN: 0,
        SOURCE_ROW_COLUMN: 0,
        SPLIT_COLUMN: "train",
    }
    row.update(overrides)
    return row


def small_silver_frame() -> pd.DataFrame:
    rows = [
        silver_row(age=30, **{SOURCE_ROW_COLUMN: 2, SPLIT_COLUMN: "validation"}),
        silver_row(age=45, **{SOURCE_ROW_COLUMN: 0, SPLIT_COLUMN: "train"}),
        silver_row(
            age=55,
            previously_contacted=1,
            days_since_previous_contact=5,
            target=1,
            **{SOURCE_ROW_COLUMN: 1, SPLIT_COLUMN: "train"},
        ),
        silver_row(
            age=60,
            target=1,
            **{SOURCE_ROW_COLUMN: 3, SPLIT_COLUMN: "test"},
        ),
    ]
    return pd.DataFrame(rows)


def test_split_silver_frame_orders_rows_and_excludes_duration() -> None:
    splits = split_silver_frame(small_silver_frame())

    assert list(splits.X_train.columns) == list(DEPLOYMENT_FEATURES)
    assert "duration" not in splits.X_train.columns
    assert splits.X_train["age"].tolist() == [45, 55]
    assert splits.y_train.tolist() == [0, 1]
    assert splits.X_validation["age"].tolist() == [30]
    assert splits.X_test["age"].tolist() == [60]


def test_split_silver_frame_rejects_missing_split() -> None:
    frame = small_silver_frame()
    frame = frame.loc[frame[SPLIT_COLUMN] != "test"].copy()

    with pytest.raises(ValueError, match="Splits Silver manquants"):
        split_silver_frame(frame)


def test_evaluate_binary_predictions_includes_ranking_metrics() -> None:
    pytest.importorskip("sklearn")

    metrics = evaluate_binary_predictions(
        y_true=pd.Series([0, 1, 0, 1]),
        y_pred=pd.Series([0, 1, 0, 0]),
        y_score=pd.Series([0.1, 0.9, 0.2, 0.8]),
        budget_fraction=0.5,
    )

    assert metrics["tp"] == 1
    assert metrics["fn"] == 1
    assert metrics["precision_yes"] == 1.0
    assert metrics["recall_yes"] == 0.5
    assert metrics["top_10_percent_count"] == 2
    assert metrics["top_10_percent_precision"] == 1.0
    assert metrics["top_10_percent_recall"] == 1.0


def test_replace_unknown_with_missing_preserves_shape() -> None:
    frame = pd.DataFrame(
        {
            "job": ["admin.", "unknown"],
            "housing": ["unknown", "yes"],
        }
    )

    transformed = replace_unknown_with_missing(frame)

    assert transformed.shape == frame.shape
    assert transformed.isna().sum().to_dict() == {"job": 1, "housing": 1}
    assert transformed.loc[0, "job"] == "admin."


def test_threshold_for_top_budget_selects_high_score_cutoff() -> None:
    scores = pd.Series([0.1, 0.9, 0.8, 0.2])

    threshold = threshold_for_top_budget(scores, budget_fraction=0.5)
    predictions = predictions_from_threshold(scores, threshold)

    assert threshold == 0.8
    assert predictions.tolist() == [0, 1, 1, 0]


def test_controlled_tuning_specs_are_unique_and_compare_unknown_strategies() -> None:
    pytest.importorskip("sklearn")

    specs = controlled_tuning_specs()
    names = [spec.name for spec in specs]
    strategies = {spec.unknown_strategy for spec in specs}

    assert len(names) == len(set(names))
    assert UNKNOWN_CATEGORY_STRATEGY in strategies
    assert UNKNOWN_MISSING_STRATEGY in strategies


def test_build_model_pipeline_clones_estimator_instances() -> None:
    pytest.importorskip("sklearn")

    spec = controlled_tuning_specs()[0]
    first_pipeline = build_model_pipeline(spec)
    second_pipeline = build_model_pipeline(spec)

    assert first_pipeline.named_steps["model"] is not spec.estimator
    assert second_pipeline.named_steps["model"] is not spec.estimator
    assert first_pipeline.named_steps["model"] is not second_pipeline.named_steps["model"]
