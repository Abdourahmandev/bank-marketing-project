# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Prétraitement déterministe et table Silver
# MAGIC
# MAGIC Ce notebook transforme Bronze en une table Silver reproductible :
# MAGIC
# MAGIC 1. il conserve la première occurrence de chacun des 12 doublons exacts ;
# MAGIC 2. il encode la cible `y` en `target` (0/1) ;
# MAGIC 3. il transforme la sentinelle `pdays=999` ;
# MAGIC 4. il crée une séparation chronologique 60/20/20 ;
# MAGIC 5. il conserve `unknown` comme catégorie pour la première baseline ;
# MAGIC 6. il garde `duration` pour l'audit, mais l'exclut explicitement de la
# MAGIC    liste des variables déployables.
# MAGIC
# MAGIC Aucune statistique n'est apprise ici. L'imputation, le one-hot encoding
# MAGIC et la normalisation seront ajustés uniquement sur `train` dans la
# MAGIC pipeline scikit-learn du prochain notebook.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from __future__ import annotations

from pyspark.sql import functions as F

from bank_marketing.data_contract import (
    EXPECTED_COLUMNS,
    EXPECTED_ROWS,
)
from bank_marketing.preprocessing import (
    BRONZE_METADATA_COLUMNS,
    DEPLOYMENT_CATEGORICAL_FEATURES,
    DEPLOYMENT_FEATURES,
    DEPLOYMENT_NUMERIC_FEATURES,
    EXPECTED_SILVER_ROWS,
    EXPECTED_SILVER_SPLIT_COUNTS,
    EXPECTED_SILVER_TARGET_COUNTS,
    SILVER_CATEGORICAL_FEATURES,
    SILVER_TARGET_COLUMN,
    SOURCE_ROW_COLUMN,
    SPLIT_COLUMN,
    prepare_silver_frame,
)

try:
    bronze_df = spark.table(BRONZE_TABLE)
except Exception as exc:
    raise RuntimeError(
        f"Table {BRONZE_TABLE} introuvable. Exécuter 01_ingestion_bronze avant Silver."
    ) from exc

if bronze_df.count() != EXPECTED_ROWS:
    raise ValueError(f"La table Bronze ne contient pas {EXPECTED_ROWS} lignes.")

missing_columns = set(EXPECTED_COLUMNS + BRONZE_METADATA_COLUMNS) - set(bronze_df.columns)
if missing_columns:
    raise ValueError(f"Colonnes Bronze manquantes: {sorted(missing_columns)}")

# Le dataset est assez petit pour une conversion contrôlée vers pandas. Le tri
# explicite restaure l'ordre physique enregistré avant l'écriture Spark.
bronze_pdf = (
    bronze_df.orderBy(SOURCE_ROW_COLUMN)
    .select(
        *[F.col(f"`{name}`") for name in EXPECTED_COLUMNS],
        *[F.col(name) for name in BRONZE_METADATA_COLUMNS],
    )
    .toPandas()
)

silver_pdf, preparation_report = prepare_silver_frame(bronze_pdf)

print("Préparation Silver validée")
print(f"- lignes Bronze       : {preparation_report.input_rows:,}")
print(f"- doublons retirés    : {preparation_report.duplicates_removed}")
print(f"- lignes Silver       : {preparation_report.output_rows:,}")
print(f"- cible               : {preparation_report.target_counts}")
print(f"- splits              : {preparation_report.split_counts}")
print(f"- variables modèle    : {len(DEPLOYMENT_FEATURES)}")
print("- variable audit seule: duration")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pourquoi ces transformations ?
# MAGIC
# MAGIC - **Doublons :** les 12 paires restent chacune dans un seul split. Les
# MAGIC   retirer évite de surpondérer des observations identiques sans modifier
# MAGIC   la frontière chronologique.
# MAGIC - **`unknown` :** cette chaîne n'est pas un `NaN`. Elle reste une
# MAGIC   catégorie explicite pour la baseline et pourra être comparée à une
# MAGIC   stratégie d'imputation sur la validation.
# MAGIC - **`pdays=999` :** 999 signifie « jamais contacté auparavant ». Silver
# MAGIC   crée `previously_contacted` et met
# MAGIC   `days_since_previous_contact=0` lorsque cette durée n'existe pas.
# MAGIC - **`duration` :** la colonne reste disponible pour prouver la fuite,
# MAGIC   mais `DEPLOYMENT_FEATURES` ne la contient jamais.

# COMMAND ----------

integer_columns = {
    "age",
    "duration",
    "campaign",
    "days_since_previous_contact",
    "previously_contacted",
    "previous",
    SILVER_TARGET_COLUMN,
}
double_columns = {
    "emp_var_rate",
    "cons_price_idx",
    "cons_conf_idx",
    "euribor3m",
    "nr_employed",
}

silver_df = spark.createDataFrame(silver_pdf)
cast_expressions = []
for column_name in silver_pdf.columns:
    column = F.col(column_name)
    if column_name in integer_columns:
        column = column.cast("int")
    elif column_name in double_columns:
        column = column.cast("double")
    elif column_name == SOURCE_ROW_COLUMN:
        column = column.cast("long")
    elif column_name != "_ingested_at_utc":
        column = column.cast("string")
    cast_expressions.append(column.alias(column_name))

silver_df = (
    silver_df.select(*cast_expressions)
    .withColumn("_silver_created_at_utc", F.current_timestamp())
)

if silver_df.count() != EXPECTED_SILVER_ROWS:
    raise AssertionError("Le nombre de lignes Silver est invalide après conversion Spark.")
if "duration" in DEPLOYMENT_FEATURES:
    raise AssertionError("Fuite détectée: duration apparaît dans les variables déployables.")

# COMMAND ----------

(
    silver_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(SILVER_TABLE)
)

spark.sql(
    f"COMMENT ON TABLE {SILVER_TABLE} IS "
    "'Données UCI Bank Marketing dédupliquées et préparées; cible binaire, "
    "pdays transformé et split chronologique 60/20/20. duration est réservée "
    "à l audit et exclue des variables déployables.'"
)

print(f"Table créée: {SILVER_TABLE}")
display(spark.table(SILVER_TABLE).orderBy(SOURCE_ROW_COLUMN).limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Contrôles finaux

# COMMAND ----------

persisted_silver_df = spark.table(SILVER_TABLE)

target_summary = {
    int(row[SILVER_TARGET_COLUMN]): int(row["count"])
    for row in persisted_silver_df.groupBy(SILVER_TARGET_COLUMN).count().collect()
}
split_summary = {
    row[SPLIT_COLUMN]: int(row["count"])
    for row in persisted_silver_df.groupBy(SPLIT_COLUMN).count().collect()
}

assert target_summary == EXPECTED_SILVER_TARGET_COUNTS
assert split_summary == EXPECTED_SILVER_SPLIT_COUNTS
assert persisted_silver_df.filter(F.col("days_since_previous_contact") == 999).count() == 0
assert (
    persisted_silver_df.filter(
        F.col("previously_contacted").isNull()
        | ~F.col("previously_contacted").isin(0, 1)
    ).count()
    == 0
)

split_quality = (
    persisted_silver_df.groupBy(SPLIT_COLUMN)
    .agg(
        F.count("*").alias("observations"),
        F.sum(SILVER_TARGET_COLUMN).alias("positives"),
        F.round(F.avg(SILVER_TARGET_COLUMN) * 100, 2).alias("positive_percentage"),
        F.min(SOURCE_ROW_COLUMN).alias("first_source_row"),
        F.max(SOURCE_ROW_COLUMN).alias("last_source_row"),
    )
    .orderBy(
        F.when(F.col(SPLIT_COLUMN) == "train", 1)
        .when(F.col(SPLIT_COLUMN) == "validation", 2)
        .otherwise(3)
    )
)
display(split_quality)

unknown_expressions = [
    F.sum(F.when(F.col(column_name) == "unknown", 1).otherwise(0)).alias(column_name)
    for column_name in SILVER_CATEGORICAL_FEATURES
]
display(persisted_silver_df.agg(*unknown_expressions))

feature_registry = spark.createDataFrame(
    [
        (feature, "numeric", "deployment")
        for feature in DEPLOYMENT_NUMERIC_FEATURES
    ]
    + [
        (feature, "categorical", "deployment")
        for feature in DEPLOYMENT_CATEGORICAL_FEATURES
    ]
    + [("duration", "numeric", "audit_only")],
    ["feature", "type", "usage"],
)
display(feature_registry)
display(spark.sql(f"DESCRIBE HISTORY {SILVER_TABLE} LIMIT 5"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Résultat méthodologique important
# MAGIC
# MAGIC Le taux positif augmente fortement au fil des trois segments temporels.
# MAGIC Cette dérive confirme que la validation aléatoire aurait été trop
# MAGIC optimiste. Les futurs modèles seront ajustés sur `train`, comparés sur
# MAGIC `validation`, puis évalués une seule fois sur `test`.
