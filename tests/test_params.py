"""Tests for project-level reproducibility parameters."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from bank_marketing.modeling import (  # noqa: E402
    FINAL_BUSINESS_THRESHOLD,
    FINAL_REFIT_STRATEGY,
    RANDOM_STATE,
    SELECTED_TUNING_MODEL_NAME,
    VALIDATION_BUDGET_FRACTION,
)
from bank_marketing.preprocessing import (  # noqa: E402
    EXPECTED_SILVER_ROWS,
    TRAIN_FRACTION,
    VALIDATION_FRACTION,
)


def load_params() -> dict[str, object]:
    with (PROJECT_ROOT / "params.yaml").open("r", encoding="utf-8") as params_file:
        return yaml.safe_load(params_file)


def load_manifest() -> dict[str, object]:
    with (PROJECT_ROOT / "data" / "dataset_manifest.json").open(
        "r",
        encoding="utf-8",
    ) as manifest_file:
        return json.load(manifest_file)


def test_params_dataset_values_match_manifest() -> None:
    params = load_params()
    manifest = load_manifest()
    dataset = params["dataset"]

    assert dataset["raw_path"] == f"data/raw/{manifest['variant']}"
    assert dataset["expected_sha256"] == manifest["sha256"]
    assert dataset["expected_file_size_bytes"] == manifest["file_size_bytes"]
    assert dataset["expected_raw_rows"] == manifest["expected_rows"]
    assert dataset["expected_raw_columns"] == manifest["expected_columns"]
    assert dataset["target_column"] == manifest["target_column"]
    assert dataset["positive_class"] == manifest["positive_class"]
    assert dataset["expected_silver_rows"] == EXPECTED_SILVER_ROWS


def test_params_model_values_match_frozen_constants() -> None:
    params = load_params()
    model = params["model"]
    business = params["business"]
    splits = params["splits"]

    assert model["random_state"] == RANDOM_STATE
    assert model["selected_model"] == SELECTED_TUNING_MODEL_NAME
    assert model["final_refit_strategy"] == FINAL_REFIT_STRATEGY
    assert model["final_business_threshold"] == pytest.approx(
        FINAL_BUSINESS_THRESHOLD
    )
    assert business["top_budget_fraction"] == pytest.approx(
        VALIDATION_BUDGET_FRACTION
    )
    assert splits["train_fraction"] == pytest.approx(TRAIN_FRACTION)
    assert splits["validation_fraction"] == pytest.approx(VALIDATION_FRACTION)
    assert (
        splits["train_fraction"]
        + splits["validation_fraction"]
        + splits["test_fraction"]
    ) == pytest.approx(1.0)
