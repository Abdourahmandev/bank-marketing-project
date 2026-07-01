# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Ingestion contrôlée vers la table Bronze
# MAGIC
# MAGIC Objectifs :
# MAGIC
# MAGIC 1. vérifier l'identité exacte du fichier officiel avec SHA-256 ;
# MAGIC 2. préserver l'ordre original des lignes ;
# MAGIC 3. valider le schéma, la taille et la cible ;
# MAGIC 4. écrire une table Delta Bronze immuable et traçable.
# MAGIC
# MAGIC Le fichier doit d'abord être téléversé dans le chemin affiché par le
# MAGIC notebook `00_configuration`.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from pyspark.sql import functions as F

from bank_marketing.data_contract import (
    EXPECTED_COLUMNS,
    EXPECTED_EXACT_DUPLICATES,
    EXPECTED_ROWS,
    EXPECTED_TARGET_COUNTS,
    TARGET_COLUMN,
    validate_pandas_frame,
)


def sha256_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    """Calcule SHA-256 sans charger tout le fichier en mémoire."""

    digest = hashlib.sha256()
    with open(path, "rb") as source_file:
        while chunk := source_file.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


raw_path = Path(RAW_CSV_PATH)
if not raw_path.is_file():
    raise FileNotFoundError(
        f"CSV introuvable: {RAW_CSV_PATH}\n"
        "Dans Databricks, ouvrir Catalog, sélectionner le catalogue et le schéma "
        f"configurés, puis téléverser le fichier dans {RAW_DIRECTORY}."
    )

actual_size = raw_path.stat().st_size
expected_size = DATASET_MANIFEST["file_size_bytes"]
if actual_size != expected_size:
    raise ValueError(
        f"Taille du fichier invalide: {actual_size}; attendue={expected_size}."
    )

actual_sha256 = sha256_file(RAW_CSV_PATH)
expected_sha256 = DATASET_MANIFEST["sha256"]
if actual_sha256.lower() != expected_sha256.lower():
    raise ValueError(
        "Empreinte SHA-256 invalide. Le fichier téléversé n'est pas exactement "
        f"la variante officielle attendue. Calculée={actual_sha256}"
    )

print(f"Fichier vérifié: {RAW_CSV_PATH}")
print(f"SHA-256: {actual_sha256}")

# COMMAND ----------

# pandas préserve ici l'ordre physique du CSV. Cet ordre est nécessaire parce
# que la documentation UCI indique que le fichier complet est ordonné par date.
raw_pdf = pd.read_csv(
    RAW_CSV_PATH,
    sep=DATASET_MANIFEST["separator"],
    encoding="utf-8",
)
validate_pandas_frame(raw_pdf)

exact_duplicate_count = int(raw_pdf.duplicated().sum())
if exact_duplicate_count != EXPECTED_EXACT_DUPLICATES:
    raise ValueError(
        f"Nombre de doublons inattendu: {exact_duplicate_count}; "
        f"attendu={EXPECTED_EXACT_DUPLICATES}."
    )

# Numéro séquentiel stable, ajouté avant toute conversion Spark.
raw_pdf["_source_row_number"] = np.arange(len(raw_pdf), dtype=np.int64)

print(f"Lignes: {len(raw_pdf):,}")
print(f"Colonnes métier: {len(EXPECTED_COLUMNS)}")
print(f"Doublons exacts: {exact_duplicate_count}")
print(f"Cible: {raw_pdf[TARGET_COLUMN].value_counts().to_dict()}")

# COMMAND ----------

integer_columns = {"age", "duration", "campaign", "pdays", "previous"}
double_columns = {
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
}


def spark_column(column_name: str):
    """Référence correctement les colonnes dont le nom contient un point."""

    return F.col(f"`{column_name}`")


expressions = []
for column_name in EXPECTED_COLUMNS:
    column = spark_column(column_name)
    if column_name in integer_columns:
        column = column.cast("int")
    elif column_name in double_columns:
        column = column.cast("double")
    else:
        column = column.cast("string")
    expressions.append(column.alias(column_name))

expressions.append(F.col("_source_row_number").cast("long"))

bronze_df = (
    spark.createDataFrame(raw_pdf)
    .select(*expressions)
    .withColumn("_source_file", F.lit(DATASET_MANIFEST["variant"]))
    .withColumn("_source_sha256", F.lit(actual_sha256))
    .withColumn("_ingested_at_utc", F.current_timestamp())
)

if bronze_df.count() != EXPECTED_ROWS:
    raise AssertionError("Le nombre de lignes a changé pendant la conversion Spark.")

spark_target_counts = {
    row[TARGET_COLUMN]: row["count"]
    for row in bronze_df.groupBy(TARGET_COLUMN).count().collect()
}
if spark_target_counts != EXPECTED_TARGET_COUNTS:
    raise AssertionError(
        f"La cible a changé pendant la conversion Spark: {spark_target_counts}."
    )

# COMMAND ----------

(
    bronze_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(BRONZE_TABLE)
)

spark.sql(
    f"COMMENT ON TABLE {BRONZE_TABLE} IS "
    "'Copie Bronze contrôlée du fichier UCI bank-additional-full.csv; "
    "ordre source préservé dans _source_row_number.'"
)

print(f"Table créée: {BRONZE_TABLE}")
display(
    spark.table(BRONZE_TABLE)
    .orderBy("_source_row_number")
    .limit(10)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Contrôles finaux

# COMMAND ----------

quality_summary = spark.createDataFrame(
    [
        ("row_count", str(EXPECTED_ROWS)),
        ("business_column_count", str(len(EXPECTED_COLUMNS))),
        ("exact_duplicate_count", str(exact_duplicate_count)),
        ("target_no", str(EXPECTED_TARGET_COUNTS["no"])),
        ("target_yes", str(EXPECTED_TARGET_COUNTS["yes"])),
        ("sha256", actual_sha256),
        ("ingestion_utc", datetime.now(timezone.utc).isoformat()),
    ],
    ["control", "value"],
)
display(quality_summary)
display(spark.sql(f"DESCRIBE HISTORY {BRONZE_TABLE} LIMIT 5"))
