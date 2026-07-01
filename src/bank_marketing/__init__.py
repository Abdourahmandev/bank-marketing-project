"""Outils réutilisables du projet Bank Marketing."""

from .data_contract import (
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    LEAKAGE_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    validate_columns,
    validate_pandas_frame,
)

__all__ = [
    "CATEGORICAL_FEATURES",
    "EXPECTED_COLUMNS",
    "LEAKAGE_COLUMNS",
    "NUMERIC_FEATURES",
    "TARGET_COLUMN",
    "validate_columns",
    "validate_pandas_frame",
]
