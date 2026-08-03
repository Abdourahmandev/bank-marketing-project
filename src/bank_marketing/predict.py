"""Prediction helpers for the final Bank Marketing pipeline."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .modeling import (
    FINAL_BUSINESS_THRESHOLD,
    positive_class_scores,
    predictions_from_threshold,
)
from .preprocessing import (
    DEPLOYMENT_CATEGORICAL_FEATURES,
    DEPLOYMENT_FEATURES,
    DEPLOYMENT_NUMERIC_FEATURES,
)

SCORE_COLUMN = "score_yes"
PREDICTED_TARGET_COLUMN = "predicted_target"
PREDICTED_LABEL_COLUMN = "predicted_label"
RANK_COLUMN = "rank_score"
THRESHOLD_COLUMN = "threshold"


def prediction_schema() -> dict[str, list[str]]:
    """Return the deployable feature schema expected by the final pipeline."""

    return {
        "numeric_features": list(DEPLOYMENT_NUMERIC_FEATURES),
        "categorical_features": list(DEPLOYMENT_CATEGORICAL_FEATURES),
        "required_features": list(DEPLOYMENT_FEATURES),
        "excluded_features": ["duration"],
    }


def prepare_prediction_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate and select the columns used by the deployable pipeline."""

    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame doit etre un pandas.DataFrame.")
    if frame.empty:
        raise ValueError("frame ne peut pas etre vide.")

    missing_columns = [
        column for column in DEPLOYMENT_FEATURES if column not in frame.columns
    ]
    if missing_columns:
        raise ValueError(f"Colonnes de prediction manquantes: {missing_columns}")

    features = frame.loc[:, list(DEPLOYMENT_FEATURES)].copy()

    invalid_numeric_columns: list[str] = []
    for column in DEPLOYMENT_NUMERIC_FEATURES:
        try:
            features[column] = pd.to_numeric(features[column], errors="raise")
        except (TypeError, ValueError):
            invalid_numeric_columns.append(column)

    if invalid_numeric_columns:
        raise ValueError(f"Colonnes numeriques invalides: {invalid_numeric_columns}")

    numeric_values = features.loc[:, list(DEPLOYMENT_NUMERIC_FEATURES)].to_numpy(
        dtype=float,
        na_value=np.nan,
    )
    infinite_columns = [
        column
        for index, column in enumerate(DEPLOYMENT_NUMERIC_FEATURES)
        if np.isinf(numeric_values[:, index]).any()
    ]
    if infinite_columns:
        raise ValueError(f"Colonnes numeriques non finies: {infinite_columns}")

    for column in DEPLOYMENT_CATEGORICAL_FEATURES:
        features[column] = features[column].astype("object")

    return features


def score_customers(
    fitted_pipeline: Any,
    frame: pd.DataFrame,
    *,
    threshold: float = FINAL_BUSINESS_THRESHOLD,
    include_input_columns: bool = False,
) -> pd.DataFrame:
    """Score customers, apply the frozen business threshold and rank them."""

    if not math.isfinite(float(threshold)):
        raise ValueError("threshold doit etre fini.")

    features = prepare_prediction_features(frame)
    scores = pd.Series(
        positive_class_scores(fitted_pipeline, features),
        index=features.index,
        name=SCORE_COLUMN,
    )
    if len(scores) != len(features):
        raise ValueError("Le modele a retourne un nombre de scores inattendu.")

    predictions = pd.Series(
        predictions_from_threshold(scores, threshold).astype("int8"),
        index=features.index,
        name=PREDICTED_TARGET_COLUMN,
    )

    scored = features.copy() if include_input_columns else pd.DataFrame(index=features.index)
    scored[SCORE_COLUMN] = scores
    scored[PREDICTED_TARGET_COLUMN] = predictions
    scored[PREDICTED_LABEL_COLUMN] = np.where(predictions == 1, "yes", "no")
    scored[RANK_COLUMN] = scores.rank(method="first", ascending=False).astype(int)
    scored[THRESHOLD_COLUMN] = float(threshold)
    return scored


def top_recommendations(scored_frame: pd.DataFrame, *, count: int = 10) -> pd.DataFrame:
    """Return the highest scoring customers from an already scored frame."""

    if count <= 0:
        raise ValueError("count doit etre strictement positif.")
    if SCORE_COLUMN not in scored_frame.columns:
        raise ValueError(f"{SCORE_COLUMN} est requis.")

    return (
        scored_frame.sort_values(SCORE_COLUMN, ascending=False, kind="stable")
        .head(count)
        .copy()
    )


def save_pipeline(fitted_pipeline: Any, path: str | Path) -> Path:
    """Serialize a fitted scikit-learn pipeline with joblib."""

    from joblib import dump

    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    dump(fitted_pipeline, target_path)
    return target_path


def load_pipeline(path: str | Path) -> Any:
    """Load a joblib-serialized pipeline."""

    from joblib import load

    return load(Path(path))
