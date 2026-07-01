# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "2"
# ///
# MAGIC %md
# MAGIC # 00 — Configuration du projet
# MAGIC
# MAGIC Ce notebook centralise les noms Unity Catalog, les chemins du Volume et
# MAGIC les noms de tables. Les autres notebooks l'exécutent avec `%run` afin
# MAGIC d'utiliser exactement la même configuration.

# COMMAND ----------

from __future__ import annotations

import json
import sys
from pathlib import Path


def find_repository_root(start: Path) -> Path:
    """Remonte jusqu'au dossier contenant ``src`` et le manifeste du dataset."""

    current = start.resolve()
    while current != current.parent:
        if (current / "src").is_dir() and (current / "data" / "dataset_manifest.json").is_file():
            return current
        current = current.parent
    raise FileNotFoundError(
        "Racine du dépôt introuvable. Exécuter ce notebook depuis le Git Folder "
        "bank-marketing-project."
    )


REPOSITORY_ROOT = find_repository_root(Path.cwd())
SOURCE_ROOT = REPOSITORY_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from bank_marketing.data_contract import (  # noqa: E402
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    LEAKAGE_COLUMNS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
)

with (REPOSITORY_ROOT / "data" / "dataset_manifest.json").open(
    "r", encoding="utf-8"
) as manifest_file:
    DATASET_MANIFEST = json.load(manifest_file)

# COMMAND ----------


def ensure_text_widget(name: str, default_value: str, label: str) -> None:
    """Crée un widget seulement s'il n'existe pas déjà."""

    try:
        dbutils.widgets.get(name)
    except Exception:
        dbutils.widgets.text(name, default_value, label)


current_catalog = spark.sql("SELECT current_catalog()").first()[0]
current_schema = spark.sql("SELECT current_schema()").first()[0]

ensure_text_widget("catalog", current_catalog, "Unity Catalog")
ensure_text_widget("schema", current_schema or "default", "Schema")
ensure_text_widget("volume", "bank_marketing", "Volume")

CATALOG = dbutils.widgets.get("catalog").strip()
SCHEMA = dbutils.widgets.get("schema").strip()
VOLUME = dbutils.widgets.get("volume").strip()


def quote_identifier(value: str) -> str:
    """Protège un identifiant SQL Databricks avec des accents graves."""

    return "`" + value.replace("`", "``") + "`"


CATALOG_SQL = quote_identifier(CATALOG)
SCHEMA_SQL = quote_identifier(SCHEMA)
VOLUME_SQL = quote_identifier(VOLUME)

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG_SQL}.{SCHEMA_SQL}")
spark.sql(
    f"CREATE VOLUME IF NOT EXISTS {CATALOG_SQL}.{SCHEMA_SQL}.{VOLUME_SQL}"
)

VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"
RAW_DIRECTORY = f"{VOLUME_PATH}/raw"
RAW_CSV_PATH = f"{RAW_DIRECTORY}/{DATASET_MANIFEST['variant']}"

BRONZE_TABLE = f"{CATALOG}.{SCHEMA}.bank_marketing_bronze"
SILVER_TABLE = f"{CATALOG}.{SCHEMA}.bank_marketing_silver"
PREDICTIONS_TABLE = f"{CATALOG}.{SCHEMA}.bank_marketing_predictions"

print("Configuration active")
print(f"- dépôt       : {REPOSITORY_ROOT}")
print(f"- catalogue   : {CATALOG}")
print(f"- schéma      : {SCHEMA}")
print(f"- volume      : {VOLUME_PATH}")
print(f"- CSV brut    : {RAW_CSV_PATH}")
print(f"- table Bronze: {BRONZE_TABLE}")
print(f"- table Silver: {SILVER_TABLE}")


# COMMAND ----------

# DBTITLE 1,Créer la structure du Volume
# Crée le sous-dossier attendu par le notebook d'ingestion.
raw_dir = Path(RAW_DIRECTORY)
raw_dir.mkdir(parents=True, exist_ok=True)

# Si le fichier a été téléversé à la racine du Volume, le déplacer dans raw/.
volume_root = Path(VOLUME_PATH)
wrong_location = volume_root / DATASET_MANIFEST["variant"]
if wrong_location.is_file() and not Path(RAW_CSV_PATH).is_file():
    wrong_location.rename(RAW_CSV_PATH)
    print(f"Fichier déplacé vers: {RAW_CSV_PATH}")
elif Path(RAW_CSV_PATH).is_file():
    print(f"Fichier déjà présent: {RAW_CSV_PATH}")
else:
    print(f"Fichier attendu à: {RAW_CSV_PATH}")
    print("Veuillez téléverser le fichier dans le volume.")
