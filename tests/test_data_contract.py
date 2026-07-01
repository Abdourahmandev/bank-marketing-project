"""Tests rapides du contrat Bank Marketing, sans dépendre de Databricks."""

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
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    LEAKAGE_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    validate_columns,
    validate_pandas_frame,
)


def one_valid_row() -> dict[str, object]:
    """Construit une ligne minimale contenant chaque colonne officielle."""

    return {
        column: (
            0
            if column in NUMERIC_FEATURES
            else "no"
            if column == TARGET_COLUMN
            else "unknown"
        )
        for column in EXPECTED_COLUMNS
    }


def test_feature_groups_cover_all_predictors_once() -> None:
    predictors = set(NUMERIC_FEATURES) | set(CATEGORICAL_FEATURES)
    assert predictors == set(EXPECTED_COLUMNS) - {TARGET_COLUMN}
    assert set(NUMERIC_FEATURES).isdisjoint(CATEGORICAL_FEATURES)


def test_duration_is_explicitly_marked_as_leakage() -> None:
    assert LEAKAGE_COLUMNS == ("duration",)


def test_validate_columns_accepts_official_order() -> None:
    validate_columns(EXPECTED_COLUMNS)


def test_validate_columns_rejects_missing_column() -> None:
    with pytest.raises(ValueError, match="colonnes manquantes"):
        validate_columns(EXPECTED_COLUMNS[:-1])


def test_validate_columns_rejects_different_order() -> None:
    reordered = list(EXPECTED_COLUMNS)
    reordered[0], reordered[1] = reordered[1], reordered[0]
    with pytest.raises(ValueError, match="ordre différent"):
        validate_columns(reordered)


def test_validate_small_frame_without_reference_counts() -> None:
    frame = pd.DataFrame([one_valid_row()], columns=EXPECTED_COLUMNS)
    validate_pandas_frame(frame, validate_counts=False)

