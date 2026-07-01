"""Tests des transformations déterministes Bronze vers Silver."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from bank_marketing.data_contract import (  # noqa: E402
    EXPECTED_COLUMNS,
    LEAKAGE_COLUMNS,
)
from bank_marketing.preprocessing import (  # noqa: E402
    DEPLOYMENT_CATEGORICAL_FEATURES,
    DEPLOYMENT_FEATURES,
    DEPLOYMENT_NUMERIC_FEATURES,
    SILVER_CATEGORICAL_FEATURES,
    SILVER_NUMERIC_FEATURES,
    SOURCE_ROW_COLUMN,
    SPLIT_COLUMN,
    TRAIN_END_ROW,
    VALIDATION_END_ROW,
    chronological_split,
    prepare_silver_frame,
)


def business_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "age": 40,
        "job": "unknown",
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
        "pdays": 999,
        "previous": 0,
        "poutcome": "nonexistent",
        "emp.var.rate": 1.1,
        "cons.price.idx": 93.994,
        "cons.conf.idx": -36.4,
        "euribor3m": 4.857,
        "nr.employed": 5191.0,
        "y": "no",
    }
    row.update(overrides)
    return row


def bronze_frame() -> pd.DataFrame:
    first = business_row()
    duplicate = first.copy()
    positive = business_row(age=55, pdays=5, previous=1, y="yes")
    frame = pd.DataFrame([first, duplicate, positive], columns=EXPECTED_COLUMNS)
    frame[SOURCE_ROW_COLUMN] = [0, 1, TRAIN_END_ROW]
    frame["_source_file"] = "bank-additional-full.csv"
    frame["_source_sha256"] = "abc"
    frame["_ingested_at_utc"] = pd.Timestamp("2026-07-01", tz="UTC")
    return frame


def test_chronological_split_boundaries() -> None:
    assert chronological_split(0) == "train"
    assert chronological_split(TRAIN_END_ROW - 1) == "train"
    assert chronological_split(TRAIN_END_ROW) == "validation"
    assert chronological_split(VALIDATION_END_ROW - 1) == "validation"
    assert chronological_split(VALIDATION_END_ROW) == "test"


@pytest.mark.parametrize("value", [-1, 41_188])
def test_chronological_split_rejects_out_of_range(value: int) -> None:
    with pytest.raises(ValueError, match="compris"):
        chronological_split(value)


def test_deployment_features_exclude_duration_and_cover_groups() -> None:
    assert LEAKAGE_COLUMNS == ("duration",)
    assert "duration" in SILVER_NUMERIC_FEATURES
    assert "duration" not in DEPLOYMENT_NUMERIC_FEATURES
    assert "duration" not in DEPLOYMENT_FEATURES
    assert set(DEPLOYMENT_FEATURES) == set(DEPLOYMENT_NUMERIC_FEATURES) | set(
        DEPLOYMENT_CATEGORICAL_FEATURES
    )
    assert set(SILVER_CATEGORICAL_FEATURES) == set(DEPLOYMENT_CATEGORICAL_FEATURES)


def test_prepare_silver_frame_applies_deterministic_rules() -> None:
    silver, report = prepare_silver_frame(
        bronze_frame(),
        validate_reference_counts=False,
    )

    assert report.input_rows == 3
    assert report.output_rows == 2
    assert report.duplicates_removed == 1
    assert report.target_counts == {0: 1, 1: 1}
    assert report.split_counts == {"train": 1, "validation": 1}

    assert silver[SOURCE_ROW_COLUMN].tolist() == [0, TRAIN_END_ROW]
    assert silver["target"].tolist() == [0, 1]
    assert silver["previously_contacted"].tolist() == [0, 1]
    assert silver["days_since_previous_contact"].tolist() == [0, 5]
    assert silver[SPLIT_COLUMN].tolist() == ["train", "validation"]
    assert silver["job"].tolist()[0] == "unknown"
    assert "pdays" not in silver.columns
    assert "emp.var.rate" not in silver.columns
    assert "emp_var_rate" in silver.columns


def test_prepare_silver_frame_rejects_missing_metadata() -> None:
    frame = bronze_frame().drop(columns=[SOURCE_ROW_COLUMN])
    with pytest.raises(ValueError, match="Métadonnées Bronze manquantes"):
        prepare_silver_frame(frame, validate_reference_counts=False)


def test_prepare_silver_frame_rejects_invalid_target() -> None:
    frame = bronze_frame()
    frame.loc[2, "y"] = "maybe"
    with pytest.raises(ValueError, match="Valeurs de cible invalides"):
        prepare_silver_frame(frame, validate_reference_counts=False)


def test_prepare_silver_frame_rejects_fractional_source_position() -> None:
    frame = bronze_frame()
    frame[SOURCE_ROW_COLUMN] = frame[SOURCE_ROW_COLUMN].astype("float64")
    frame.loc[2, SOURCE_ROW_COLUMN] = 2.5
    with pytest.raises(ValueError, match="doit contenir des entiers"):
        prepare_silver_frame(frame, validate_reference_counts=False)
