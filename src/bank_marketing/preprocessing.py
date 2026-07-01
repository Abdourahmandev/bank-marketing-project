"""Transformations déterministes entre les tables Bronze et Silver.

Ce module ne contient aucune opération apprise sur les données. L'imputation,
l'encodage one-hot et la normalisation seront ajustés plus tard uniquement sur
l'ensemble d'entraînement dans une pipeline scikit-learn.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .data_contract import (
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    EXPECTED_EXACT_DUPLICATES,
    EXPECTED_ROWS,
    LEAKAGE_COLUMNS,
    TARGET_COLUMN,
    validate_pandas_frame,
)

SOURCE_ROW_COLUMN = "_source_row_number"
SPLIT_COLUMN = "dataset_split"
SILVER_TARGET_COLUMN = "target"

TRAIN_FRACTION = 0.60
VALIDATION_FRACTION = 0.20
TRAIN_END_ROW = int(EXPECTED_ROWS * TRAIN_FRACTION)
VALIDATION_END_ROW = int(EXPECTED_ROWS * (TRAIN_FRACTION + VALIDATION_FRACTION))

SPLIT_LABELS: tuple[str, ...] = ("train", "validation", "test")

# Les points dans les noms sont pénibles à manipuler en Spark SQL. Silver les
# remplace par des noms simples sans modifier leur sens.
COLUMN_RENAME_MAP: dict[str, str] = {
    "emp.var.rate": "emp_var_rate",
    "cons.price.idx": "cons_price_idx",
    "cons.conf.idx": "cons_conf_idx",
    "nr.employed": "nr_employed",
}

SILVER_CATEGORICAL_FEATURES: tuple[str, ...] = CATEGORICAL_FEATURES
SILVER_NUMERIC_FEATURES: tuple[str, ...] = (
    "age",
    "duration",
    "campaign",
    "days_since_previous_contact",
    "previously_contacted",
    "previous",
    "emp_var_rate",
    "cons_price_idx",
    "cons_conf_idx",
    "euribor3m",
    "nr_employed",
)
SILVER_FEATURES: tuple[str, ...] = (
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "days_since_previous_contact",
    "previously_contacted",
    "previous",
    "poutcome",
    "emp_var_rate",
    "cons_price_idx",
    "cons_conf_idx",
    "euribor3m",
    "nr_employed",
)

# duration est disponible après l'appel seulement. Elle reste dans Silver pour
# documenter la fuite, mais cette liste est la seule autorisée pour les modèles
# qui doivent classer les clients avant l'appel.
DEPLOYMENT_NUMERIC_FEATURES: tuple[str, ...] = tuple(
    feature for feature in SILVER_NUMERIC_FEATURES if feature not in LEAKAGE_COLUMNS
)
DEPLOYMENT_CATEGORICAL_FEATURES: tuple[str, ...] = SILVER_CATEGORICAL_FEATURES
DEPLOYMENT_FEATURES: tuple[str, ...] = (
    DEPLOYMENT_NUMERIC_FEATURES + DEPLOYMENT_CATEGORICAL_FEATURES
)

BRONZE_METADATA_COLUMNS: tuple[str, ...] = (
    SOURCE_ROW_COLUMN,
    "_source_file",
    "_source_sha256",
    "_ingested_at_utc",
)

EXPECTED_SILVER_ROWS = EXPECTED_ROWS - EXPECTED_EXACT_DUPLICATES
EXPECTED_SILVER_TARGET_COUNTS = {0: 36_537, 1: 4_639}
EXPECTED_SILVER_SPLIT_COUNTS = {
    "train": 24_705,
    "validation": 8_235,
    "test": 8_236,
}


@dataclass(frozen=True)
class SilverPreparationReport:
    """Résumé vérifiable des transformations Bronze vers Silver."""

    input_rows: int
    output_rows: int
    duplicates_removed: int
    target_counts: dict[int, int]
    split_counts: dict[str, int]


def chronological_split(source_row_number: int) -> str:
    """Retourne le split 60/20/20 associé à une position du fichier source."""

    if isinstance(source_row_number, bool) or not isinstance(source_row_number, int):
        raise TypeError("source_row_number doit être un entier.")
    if not 0 <= source_row_number < EXPECTED_ROWS:
        raise ValueError(
            f"source_row_number doit être compris entre 0 et {EXPECTED_ROWS - 1}."
        )
    if source_row_number < TRAIN_END_ROW:
        return "train"
    if source_row_number < VALIDATION_END_ROW:
        return "validation"
    return "test"


def prepare_silver_frame(
    bronze_frame: Any,
    *,
    validate_reference_counts: bool = True,
) -> tuple[Any, SilverPreparationReport]:
    """Prépare une copie pandas de Bronze pour l'écriture de Silver.

    Les doublons sont définis uniquement par les 21 colonnes métier : les
    métadonnées d'ingestion et le numéro de ligne ne doivent pas empêcher leur
    détection. La première occurrence chronologique est conservée.
    """

    missing = [column for column in BRONZE_METADATA_COLUMNS if column not in bronze_frame]
    if missing:
        raise ValueError(f"Métadonnées Bronze manquantes: {missing}")

    business_frame = bronze_frame.loc[:, EXPECTED_COLUMNS]
    validate_pandas_frame(
        business_frame,
        validate_counts=validate_reference_counts,
    )

    if bronze_frame[SOURCE_ROW_COLUMN].isna().any():
        raise ValueError(f"{SOURCE_ROW_COLUMN} contient une valeur manquante.")
    if bronze_frame[SOURCE_ROW_COLUMN].duplicated().any():
        raise ValueError(f"{SOURCE_ROW_COLUMN} doit être unique.")

    ordered = bronze_frame.sort_values(SOURCE_ROW_COLUMN, kind="stable").copy()
    try:
        source_rows = ordered[SOURCE_ROW_COLUMN].astype("int64")
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{SOURCE_ROW_COLUMN} doit contenir des entiers.") from exc
    if not (ordered[SOURCE_ROW_COLUMN] == source_rows).all():
        raise ValueError(f"{SOURCE_ROW_COLUMN} doit contenir des entiers.")
    if not source_rows.map(lambda value: 0 <= value < EXPECTED_ROWS).all():
        raise ValueError(f"{SOURCE_ROW_COLUMN} contient une position hors limites.")

    duplicate_mask = ordered.loc[:, EXPECTED_COLUMNS].duplicated(keep="first")
    duplicates_removed = int(duplicate_mask.sum())
    if validate_reference_counts and duplicates_removed != EXPECTED_EXACT_DUPLICATES:
        raise ValueError(
            f"Doublons inattendus: {duplicates_removed}; "
            f"attendu={EXPECTED_EXACT_DUPLICATES}."
        )

    silver = ordered.loc[~duplicate_mask].copy()

    invalid_targets = set(silver[TARGET_COLUMN].dropna().unique()) - {"no", "yes"}
    if invalid_targets or silver[TARGET_COLUMN].isna().any():
        raise ValueError(f"Valeurs de cible invalides: {sorted(invalid_targets)}")
    silver[SILVER_TARGET_COLUMN] = (
        silver[TARGET_COLUMN].map({"no": 0, "yes": 1}).astype("int8")
    )

    if (
        silver["pdays"].isna().any()
        or (silver["pdays"] < 0).any()
        or (silver["pdays"] % 1 != 0).any()
    ):
        raise ValueError("pdays doit contenir uniquement des entiers positifs ou 999.")
    silver["previously_contacted"] = (silver["pdays"] != 999).astype("int8")
    silver["days_since_previous_contact"] = (
        silver["pdays"].where(silver["pdays"] != 999, 0).astype("int32")
    )

    silver[SPLIT_COLUMN] = silver[SOURCE_ROW_COLUMN].map(
        lambda value: chronological_split(int(value))
    )
    silver = silver.rename(columns=COLUMN_RENAME_MAP)

    output_columns = list(SILVER_FEATURES) + [
        SILVER_TARGET_COLUMN,
        SOURCE_ROW_COLUMN,
        SPLIT_COLUMN,
        "_source_file",
        "_source_sha256",
        "_ingested_at_utc",
    ]
    silver = silver.loc[:, output_columns].reset_index(drop=True)

    report = SilverPreparationReport(
        input_rows=len(bronze_frame),
        output_rows=len(silver),
        duplicates_removed=duplicates_removed,
        target_counts={
            int(label): int(count)
            for label, count in silver[SILVER_TARGET_COLUMN].value_counts().items()
        },
        split_counts={
            str(label): int(count)
            for label, count in silver[SPLIT_COLUMN].value_counts().items()
        },
    )

    if validate_reference_counts:
        if report.output_rows != EXPECTED_SILVER_ROWS:
            raise AssertionError(
                f"Silver contient {report.output_rows} lignes; "
                f"attendu={EXPECTED_SILVER_ROWS}."
            )
        if report.target_counts != EXPECTED_SILVER_TARGET_COUNTS:
            raise AssertionError(f"Cible Silver inattendue: {report.target_counts}")
        if report.split_counts != EXPECTED_SILVER_SPLIT_COUNTS:
            raise AssertionError(f"Splits Silver inattendus: {report.split_counts}")

    return silver, report
