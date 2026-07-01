# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Analyse exploratoire des données
# MAGIC
# MAGIC Cette première EDA vérifie la qualité des données, décrit la cible et
# MAGIC rend visible la fuite associée à `duration`. Elle ne prend encore aucune
# MAGIC décision irréversible de nettoyage.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pyspark.sql import functions as F

from bank_marketing.data_contract import (
    CATEGORICAL_FEATURES,
    EXPECTED_COLUMNS,
    EXPECTED_EXACT_DUPLICATES,
    EXPECTED_ROWS,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
)

sns.set_theme(style="whitegrid")

try:
    bronze_df = spark.table(BRONZE_TABLE)
except Exception as exc:
    raise RuntimeError(
        f"Table {BRONZE_TABLE} introuvable. Exécuter 01_ingestion_bronze avant l'EDA."
    ) from exc

if bronze_df.count() != EXPECTED_ROWS:
    raise ValueError(f"La table Bronze ne contient pas {EXPECTED_ROWS} lignes.")

business_df = bronze_df.select(*[F.col(f"`{name}`") for name in EXPECTED_COLUMNS])
display(bronze_df.orderBy("_source_row_number").limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Structure, cible et qualité globale

# COMMAND ----------

target_distribution = (
    business_df.groupBy(TARGET_COLUMN)
    .count()
    .withColumn("percentage", F.round(F.col("count") / EXPECTED_ROWS * 100, 2))
    .orderBy(TARGET_COLUMN)
)
display(target_distribution)

unknown_expressions = [
    F.sum(F.when(F.col(column_name) == "unknown", 1).otherwise(0)).alias(column_name)
    for column_name in CATEGORICAL_FEATURES
]
unknown_row = business_df.agg(*unknown_expressions).first().asDict()
unknown_summary = spark.createDataFrame(
    [(name, int(count)) for name, count in unknown_row.items()],
    ["column", "unknown_count"],
).withColumn(
    "unknown_percentage", F.round(F.col("unknown_count") / EXPECTED_ROWS * 100, 2)
)
display(unknown_summary.orderBy(F.desc("unknown_count")))

# COMMAND ----------

# Conversion contrôlée vers pandas. Avec 41 188 x 21, le dataset est assez petit
# pour la mémoire du driver et scikit-learn est l'outil cohérent avec le cours.
eda_pdf = (
    bronze_df.orderBy("_source_row_number")
    .select(*[F.col(f"`{name}`") for name in EXPECTED_COLUMNS])
    .toPandas()
)

exact_duplicates = int(eda_pdf.duplicated().sum())
print(f"Dimensions: {eda_pdf.shape}")
print(f"NaN bruts: {int(eda_pdf.isna().sum().sum())}")
print(f"Doublons exacts: {exact_duplicates}")
assert exact_duplicates == EXPECTED_EXACT_DUPLICATES

# COMMAND ----------

fig, ax = plt.subplots(figsize=(7, 4))
counts = eda_pdf[TARGET_COLUMN].value_counts().reindex(["no", "yes"])
sns.barplot(x=counts.index, y=counts.values, ax=ax, color="#2f6b9a")
ax.set_title("Distribution de la cible y")
ax.set_xlabel("Souscription à un dépôt à terme")
ax.set_ylabel("Nombre d'observations")
for index, count in enumerate(counts.values):
    ax.text(index, count, f"{count:,}\n({count / len(eda_pdf):.1%})", ha="center", va="bottom")
plt.tight_layout()
plt.show()

print(
    "Conclusion: l'accuracy seule sera trompeuse, car la classe positive "
    f"représente seulement {(eda_pdf[TARGET_COLUMN] == 'yes').mean():.2%} des lignes."
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Variables numériques et valeurs extrêmes

# COMMAND ----------

display(spark.createDataFrame(eda_pdf[list(NUMERIC_FEATURES)].describe().T.reset_index()))

columns_per_row = 2
rows = math.ceil(len(NUMERIC_FEATURES) / columns_per_row)
fig, axes = plt.subplots(rows, columns_per_row, figsize=(14, 4 * rows))
axes = np.asarray(axes).reshape(-1)

for axis, column_name in zip(axes, NUMERIC_FEATURES):
    sns.histplot(eda_pdf[column_name], bins=35, kde=False, ax=axis)
    axis.set_title(f"Distribution — {column_name}")
    axis.set_xlabel(column_name)

for axis in axes[len(NUMERIC_FEATURES):]:
    axis.set_visible(False)

plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Démonstration de la fuite `duration`
# MAGIC
# MAGIC `duration` est connue seulement après l'appel. Elle peut être analysée,
# MAGIC mais elle sera exclue du modèle destiné à choisir les clients avant appel.

# COMMAND ----------

duration_summary = (
    eda_pdf.groupby(TARGET_COLUMN)["duration"]
    .agg(["count", "mean", "median", "std"])
    .round(2)
)
display(spark.createDataFrame(duration_summary.reset_index()))

fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=eda_pdf, x=TARGET_COLUMN, y="duration", showfliers=False, ax=ax)
ax.set_title("Durée de l'appel selon la cible — variable non déployable")
ax.set_xlabel("Souscription")
ax.set_ylabel("Durée de l'appel (secondes)")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Taux de souscription par variable catégorielle

# COMMAND ----------

eda_with_target = eda_pdf.assign(target_yes=(eda_pdf[TARGET_COLUMN] == "yes").astype(int))

for column_name in CATEGORICAL_FEATURES:
    category_summary = (
        eda_with_target.groupby(column_name, dropna=False)
        .agg(observations=("target_yes", "size"), subscription_rate=("target_yes", "mean"))
        .sort_values("subscription_rate", ascending=False)
        .reset_index()
    )
    category_summary["subscription_rate"] = category_summary["subscription_rate"].round(4)
    print(f"\n{column_name}")
    display(spark.createDataFrame(category_summary))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Corrélations numériques
# MAGIC
# MAGIC La corrélation décrit une association et ne prouve pas une causalité.

# COMMAND ----------

correlation_pdf = eda_with_target[list(NUMERIC_FEATURES) + ["target_yes"]].corr(numeric_only=True)
fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(correlation_pdf, cmap="coolwarm", center=0, annot=True, fmt=".2f", ax=ax)
ax.set_title("Matrice de corrélation — variables numériques")
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Premières conclusions à valider
# MAGIC
# MAGIC - La classe `yes` est minoritaire : les métriques devront cibler cette classe.
# MAGIC - `duration` est une fuite opérationnelle et sera retirée du modèle final.
# MAGIC - `unknown` n'est pas un `NaN` brut : son traitement doit être comparé en validation.
# MAGIC - Les 12 doublons doivent être inspectés avant suppression.
# MAGIC - L'ordre `_source_row_number` doit être conservé pour le test chronologique.

