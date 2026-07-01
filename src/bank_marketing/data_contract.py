"""Contrat de données commun aux traitements locaux et Databricks.

Le contrat échoue rapidement si le mauvais fichier est chargé. Cette vérification
évite de produire silencieusement des résultats à partir d'une variante réduite
ou d'un schéma modifié du dataset Bank Marketing.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

EXPECTED_COLUMNS: tuple[str, ...] = (
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
    "pdays",
    "previous",
    "poutcome",
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
    "y",
)

NUMERIC_FEATURES: tuple[str, ...] = (
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
)

CATEGORICAL_FEATURES: tuple[str, ...] = (
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
)

TARGET_COLUMN = "y"
POSITIVE_CLASS = "yes"
LEAKAGE_COLUMNS: tuple[str, ...] = ("duration",)
EXPECTED_ROWS = 41_188
EXPECTED_TARGET_COUNTS = {"no": 36_548, "yes": 4_640}
EXPECTED_EXACT_DUPLICATES = 12


def validate_columns(columns: Iterable[str]) -> None:
    """Vérifie la présence et l'ordre exact des colonnes officielles."""

    actual = tuple(columns)
    if actual == EXPECTED_COLUMNS:
        return

    missing = [column for column in EXPECTED_COLUMNS if column not in actual]
    unexpected = [column for column in actual if column not in EXPECTED_COLUMNS]
    order_only = not missing and not unexpected

    details: list[str] = []
    if missing:
        details.append(f"colonnes manquantes={missing}")
    if unexpected:
        details.append(f"colonnes inattendues={unexpected}")
    if order_only:
        details.append("les colonnes sont présentes, mais dans un ordre différent")

    raise ValueError("Schéma Bank Marketing invalide: " + "; ".join(details))


def validate_pandas_frame(frame: Any, *, validate_counts: bool = True) -> None:
    """Valide le schéma et, pour le fichier complet, les comptes de référence.

    ``Any`` est utilisé volontairement afin que le module puisse être importé sans
    imposer pandas à la simple lecture des constantes. L'objet reçu doit exposer
    l'interface minimale d'un ``pandas.DataFrame``.
    """

    validate_columns(frame.columns)

    if not validate_counts:
        return

    row_count = len(frame)
    if row_count != EXPECTED_ROWS:
        raise ValueError(
            f"Nombre de lignes inattendu: {row_count}; attendu={EXPECTED_ROWS}. "
            "Vérifier que bank-additional-full.csv a bien été chargé."
        )

    target_counts = frame[TARGET_COLUMN].value_counts(dropna=False).to_dict()
    if target_counts != EXPECTED_TARGET_COUNTS:
        raise ValueError(
            "Distribution de la cible inattendue: "
            f"{target_counts}; attendue={EXPECTED_TARGET_COUNTS}."
        )
