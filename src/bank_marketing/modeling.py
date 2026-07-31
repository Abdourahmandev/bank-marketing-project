"""Outils communs pour les premieres experiences de classification."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .preprocessing import (
    DEPLOYMENT_CATEGORICAL_FEATURES,
    DEPLOYMENT_FEATURES,
    DEPLOYMENT_NUMERIC_FEATURES,
    SILVER_TARGET_COLUMN,
    SOURCE_ROW_COLUMN,
    SPLIT_COLUMN,
    SPLIT_LABELS,
)

RANDOM_STATE = 42
VALIDATION_BUDGET_FRACTION = 0.10


@dataclass(frozen=True)
class ModelingSplits:
    """Jeux prets pour scikit-learn, separes selon le split chronologique."""

    X_train: pd.DataFrame
    y_train: pd.Series
    X_validation: pd.DataFrame
    y_validation: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series
    split_summary: pd.DataFrame


@dataclass(frozen=True)
class ModelSpec:
    """Definition reproductible d'un modele de premiere iteration."""

    name: str
    estimator: Any
    description: str


def required_modeling_columns() -> tuple[str, ...]:
    """Colonnes minimales attendues dans Silver pour la modelisation."""

    return DEPLOYMENT_FEATURES + (
        SILVER_TARGET_COLUMN,
        SOURCE_ROW_COLUMN,
        SPLIT_COLUMN,
    )


def validate_modeling_frame(frame: pd.DataFrame) -> None:
    """Valide que Silver contient les colonnes necessaires au notebook 04."""

    missing_columns = [
        column for column in required_modeling_columns() if column not in frame.columns
    ]
    if missing_columns:
        raise ValueError(f"Colonnes Silver manquantes: {missing_columns}")

    if "duration" in DEPLOYMENT_FEATURES:
        raise AssertionError("duration ne doit jamais etre une variable deployable.")

    invalid_targets = set(frame[SILVER_TARGET_COLUMN].dropna().unique()) - {0, 1}
    if invalid_targets or frame[SILVER_TARGET_COLUMN].isna().any():
        raise ValueError(f"Valeurs de cible invalides: {sorted(invalid_targets)}")

    observed_splits = set(frame[SPLIT_COLUMN].dropna().unique())
    missing_splits = set(SPLIT_LABELS) - observed_splits
    if missing_splits:
        raise ValueError(f"Splits Silver manquants: {sorted(missing_splits)}")

    if frame[SOURCE_ROW_COLUMN].isna().any():
        raise ValueError(f"{SOURCE_ROW_COLUMN} contient une valeur manquante.")
    if frame[SOURCE_ROW_COLUMN].duplicated().any():
        raise ValueError(f"{SOURCE_ROW_COLUMN} doit etre unique dans Silver.")


def split_silver_frame(frame: pd.DataFrame) -> ModelingSplits:
    """Trie Silver et prepare les matrices X/y sans inclure de fuite."""

    validate_modeling_frame(frame)
    ordered = frame.sort_values(SOURCE_ROW_COLUMN, kind="stable").copy()
    feature_columns = list(DEPLOYMENT_FEATURES)

    split_summary = (
        ordered.groupby(SPLIT_COLUMN)
        .agg(
            observations=(SILVER_TARGET_COLUMN, "size"),
            positives=(SILVER_TARGET_COLUMN, "sum"),
            positive_rate=(SILVER_TARGET_COLUMN, "mean"),
            first_source_row=(SOURCE_ROW_COLUMN, "min"),
            last_source_row=(SOURCE_ROW_COLUMN, "max"),
        )
        .reindex(SPLIT_LABELS)
        .reset_index()
    )
    split_summary["positive_rate"] = split_summary["positive_rate"].round(4)

    def split_part(label: str) -> tuple[pd.DataFrame, pd.Series]:
        part = ordered.loc[ordered[SPLIT_COLUMN] == label]
        return (
            part.loc[:, feature_columns].reset_index(drop=True),
            part.loc[:, SILVER_TARGET_COLUMN].astype("int8").reset_index(drop=True),
        )

    X_train, y_train = split_part("train")
    X_validation, y_validation = split_part("validation")
    X_test, y_test = split_part("test")

    return ModelingSplits(
        X_train=X_train,
        y_train=y_train,
        X_validation=X_validation,
        y_validation=y_validation,
        X_test=X_test,
        y_test=y_test,
        split_summary=split_summary,
    )


def build_preprocessor() -> Any:
    """Construit le ColumnTransformer ajuste uniquement sur train."""

    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, list(DEPLOYMENT_NUMERIC_FEATURES)),
            (
                "categorical",
                categorical_transformer,
                list(DEPLOYMENT_CATEGORICAL_FEATURES),
            ),
        ],
        remainder="drop",
    )


def baseline_model_specs(random_state: int = RANDOM_STATE) -> tuple[ModelSpec, ...]:
    """Retourne les modeles de reference et de premiere iteration."""

    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier

    return (
        ModelSpec(
            name="dummy_prior",
            estimator=DummyClassifier(strategy="prior"),
            description="Reference naive: predit toujours la classe majoritaire.",
        ),
        ModelSpec(
            name="logistic_regression",
            estimator=LogisticRegression(max_iter=1000, random_state=random_state),
            description="Modele lineaire interpretable, sans poids de classes.",
        ),
        ModelSpec(
            name="logistic_regression_balanced",
            estimator=LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=random_state,
            ),
            description="Regression logistique avec poids de classes.",
        ),
        ModelSpec(
            name="decision_tree_balanced",
            estimator=DecisionTreeClassifier(
                max_depth=6,
                min_samples_leaf=50,
                class_weight="balanced",
                random_state=random_state,
            ),
            description="Arbre contraint pour limiter le surapprentissage.",
        ),
        ModelSpec(
            name="random_forest_balanced",
            estimator=RandomForestClassifier(
                n_estimators=150,
                max_depth=12,
                min_samples_leaf=25,
                class_weight="balanced_subsample",
                n_jobs=-1,
                random_state=random_state,
            ),
            description="Ensemble d'arbres avec contraintes de regularisation.",
        ),
    )


def build_model_pipeline(model_spec: ModelSpec) -> Any:
    """Assemble le pretraitement et l'estimateur dans une pipeline sklearn."""

    from sklearn.pipeline import Pipeline

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("model", model_spec.estimator),
        ]
    )


def positive_class_scores(fitted_pipeline: Any, features: pd.DataFrame) -> np.ndarray:
    """Retourne le score de probabilite associe a la classe positive 1."""

    if hasattr(fitted_pipeline, "predict_proba"):
        probabilities = fitted_pipeline.predict_proba(features)
        classes = getattr(fitted_pipeline, "classes_", None)
        if classes is None and hasattr(fitted_pipeline, "named_steps"):
            classes = getattr(fitted_pipeline.named_steps["model"], "classes_", None)
        if classes is None or 1 not in classes:
            raise ValueError("La classe positive 1 est absente du modele ajuste.")
        positive_index = list(classes).index(1)
        return np.asarray(probabilities[:, positive_index], dtype=float)

    if hasattr(fitted_pipeline, "decision_function"):
        return np.asarray(fitted_pipeline.decision_function(features), dtype=float)

    raise TypeError("Le modele doit exposer predict_proba ou decision_function.")


def evaluate_binary_predictions(
    y_true: pd.Series | np.ndarray,
    y_pred: pd.Series | np.ndarray,
    y_score: pd.Series | np.ndarray,
    *,
    budget_fraction: float = VALIDATION_BUDGET_FRACTION,
) -> dict[str, float]:
    """Calcule les metriques utiles pour une classe positive rare."""

    from sklearn.metrics import (
        accuracy_score,
        average_precision_score,
        balanced_accuracy_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    y_true_array = np.asarray(y_true, dtype=int)
    y_pred_array = np.asarray(y_pred, dtype=int)
    y_score_array = np.asarray(y_score, dtype=float)

    tn, fp, fn, tp = confusion_matrix(
        y_true_array,
        y_pred_array,
        labels=[0, 1],
    ).ravel()

    positive_count = int(y_true_array.sum())
    k = max(1, int(math.ceil(len(y_true_array) * budget_fraction)))
    ranked_indices = np.lexsort((np.arange(len(y_score_array)), -y_score_array))
    selected_indices = ranked_indices[:k]
    selected_positives = int(y_true_array[selected_indices].sum())
    positive_rate = float(y_true_array.mean())
    top_precision = selected_positives / k
    top_recall = selected_positives / positive_count if positive_count else 0.0
    top_lift = top_precision / positive_rate if positive_rate else math.nan

    return {
        "accuracy": float(accuracy_score(y_true_array, y_pred_array)),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_true_array, y_pred_array)
        ),
        "precision_yes": float(
            precision_score(y_true_array, y_pred_array, zero_division=0)
        ),
        "recall_yes": float(recall_score(y_true_array, y_pred_array, zero_division=0)),
        "f1_yes": float(f1_score(y_true_array, y_pred_array, zero_division=0)),
        "average_precision": float(average_precision_score(y_true_array, y_score_array)),
        "roc_auc": float(roc_auc_score(y_true_array, y_score_array)),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
        "tp": float(tp),
        "top_10_percent_precision": float(top_precision),
        "top_10_percent_recall": float(top_recall),
        "top_10_percent_lift": float(top_lift),
        "top_10_percent_count": float(k),
    }


def fit_and_evaluate_baselines(
    splits: ModelingSplits,
    *,
    random_state: int = RANDOM_STATE,
    budget_fraction: float = VALIDATION_BUDGET_FRACTION,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Ajuste les modeles sur train et les evalue sur train/validation."""

    rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Any] = {}

    for model_spec in baseline_model_specs(random_state=random_state):
        pipeline = build_model_pipeline(model_spec)
        pipeline.fit(splits.X_train, splits.y_train)
        fitted_models[model_spec.name] = pipeline

        row: dict[str, Any] = {
            "model": model_spec.name,
            "description": model_spec.description,
        }
        for split_name, features, target in (
            ("train", splits.X_train, splits.y_train),
            ("validation", splits.X_validation, splits.y_validation),
        ):
            predictions = pipeline.predict(features)
            scores = positive_class_scores(pipeline, features)
            metrics = evaluate_binary_predictions(
                target,
                predictions,
                scores,
                budget_fraction=budget_fraction,
            )
            row.update({f"{split_name}_{key}": value for key, value in metrics.items()})

        rows.append(row)

    results = pd.DataFrame(rows).sort_values(
        by=["validation_average_precision", "validation_f1_yes"],
        ascending=False,
    )
    return results.reset_index(drop=True), fitted_models
