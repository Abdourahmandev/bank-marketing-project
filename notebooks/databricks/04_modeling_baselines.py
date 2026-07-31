# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Baselines de modélisation
# MAGIC
# MAGIC Ce notebook utilise la table Silver pour construire la première pipeline
# MAGIC scikit-learn et comparer des modèles de référence. Les modèles sont
# MAGIC ajustés uniquement sur `train` et comparés sur `validation`.
# MAGIC
# MAGIC Le split `test` est chargé seulement pour confirmer sa présence. Aucune
# MAGIC métrique de test n'est calculée ici.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from __future__ import annotations

import math

import mlflow
import pandas as pd
from pyspark.sql import functions as F

from bank_marketing.modeling import (
    RANDOM_STATE,
    VALIDATION_BUDGET_FRACTION,
    baseline_model_specs,
    build_model_pipeline,
    evaluate_binary_predictions,
    positive_class_scores,
    split_silver_frame,
)
from bank_marketing.preprocessing import (
    DEPLOYMENT_CATEGORICAL_FEATURES,
    DEPLOYMENT_FEATURES,
    DEPLOYMENT_NUMERIC_FEATURES,
    EXPECTED_SILVER_ROWS,
    EXPECTED_SILVER_SPLIT_COUNTS,
    EXPECTED_SILVER_TARGET_COUNTS,
    SILVER_TARGET_COLUMN,
    SOURCE_ROW_COLUMN,
    SPLIT_COLUMN,
)

try:
    silver_df = spark.table(SILVER_TABLE)
except Exception as exc:
    raise RuntimeError(
        f"Table {SILVER_TABLE} introuvable. Exécuter 03_preprocessing_silver avant les baselines."
    ) from exc

if silver_df.count() != EXPECTED_SILVER_ROWS:
    raise ValueError(f"La table Silver ne contient pas {EXPECTED_SILVER_ROWS} lignes.")

target_summary = {
    int(row[SILVER_TARGET_COLUMN]): int(row["count"])
    for row in silver_df.groupBy(SILVER_TARGET_COLUMN).count().collect()
}
split_summary = {
    row[SPLIT_COLUMN]: int(row["count"])
    for row in silver_df.groupBy(SPLIT_COLUMN).count().collect()
}
if target_summary != EXPECTED_SILVER_TARGET_COUNTS:
    raise ValueError(f"Cible Silver inattendue: {target_summary}")
if split_summary != EXPECTED_SILVER_SPLIT_COUNTS:
    raise ValueError(f"Splits Silver inattendus: {split_summary}")
if "duration" in DEPLOYMENT_FEATURES:
    raise AssertionError("Fuite détectée: duration apparaît dans DEPLOYMENT_FEATURES.")

silver_pdf = (
    silver_df.orderBy(SOURCE_ROW_COLUMN)
    .select(
        *[F.col(feature) for feature in DEPLOYMENT_FEATURES],
        F.col("duration"),
        F.col(SILVER_TARGET_COLUMN),
        F.col(SOURCE_ROW_COLUMN),
        F.col(SPLIT_COLUMN),
    )
    .toPandas()
)

splits = split_silver_frame(silver_pdf)

print("Table Silver prête pour la modélisation")
print(f"- observations        : {len(silver_pdf):,}")
print(f"- variables numériques: {len(DEPLOYMENT_NUMERIC_FEATURES)}")
print(f"- variables catégorielles: {len(DEPLOYMENT_CATEGORICAL_FEATURES)}")
print(f"- variables modèle    : {len(DEPLOYMENT_FEATURES)}")
print("- variable exclue     : duration")
display(splits.split_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Pipeline commune
# MAGIC
# MAGIC La pipeline applique les transformations suivantes :
# MAGIC
# MAGIC - médiane + standardisation sur les variables numériques ;
# MAGIC - catégorie la plus fréquente + one-hot encoding sur les variables catégorielles ;
# MAGIC - `handle_unknown="ignore"` pour transformer de nouvelles catégories sans erreur ;
# MAGIC - aucune transformation ajustée sur validation ou test.

# COMMAND ----------

feature_registry = pd.DataFrame(
    [
        (feature, "numeric", "deployment")
        for feature in DEPLOYMENT_NUMERIC_FEATURES
    ]
    + [
        (feature, "categorical", "deployment")
        for feature in DEPLOYMENT_CATEGORICAL_FEATURES
    ]
    + [("duration", "numeric", "audit_only")],
    columns=["feature", "type", "usage"],
)
display(spark.createDataFrame(feature_registry))

# COMMAND ----------

# MAGIC %md
# MAGIC ## MLflow et modèles entraînés
# MAGIC
# MAGIC Les métriques `train` sont utiles pour repérer un surapprentissage évident.
# MAGIC Le choix du modèle et des hyperparamètres se fait seulement avec
# MAGIC `validation`. Le test final reste isolé.

# COMMAND ----------

experiment_path = f"/Users/{spark.sql('SELECT current_user()').first()[0]}/bank_marketing_baselines"
mlflow.set_experiment(experiment_path)

try:
    mlflow.autolog(log_models=False, silent=True)
except TypeError:
    mlflow.autolog()

results_rows = []
fitted_models = {}

for model_spec in baseline_model_specs(random_state=RANDOM_STATE):
    with mlflow.start_run(run_name=model_spec.name):
        pipeline = build_model_pipeline(model_spec)
        pipeline.fit(splits.X_train, splits.y_train)
        fitted_models[model_spec.name] = pipeline

        row = {
            "model": model_spec.name,
            "description": model_spec.description,
        }
        mlflow.log_param("model_name", model_spec.name)
        mlflow.log_param("description", model_spec.description)
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("train_rows", len(splits.X_train))
        mlflow.log_param("validation_rows", len(splits.X_validation))
        mlflow.log_param("test_rows_not_evaluated", len(splits.X_test))
        mlflow.log_param("feature_count", len(DEPLOYMENT_FEATURES))
        mlflow.log_param("numeric_feature_count", len(DEPLOYMENT_NUMERIC_FEATURES))
        mlflow.log_param("categorical_feature_count", len(DEPLOYMENT_CATEGORICAL_FEATURES))
        mlflow.log_param("test_split_used_for_metrics", False)

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
                budget_fraction=VALIDATION_BUDGET_FRACTION,
            )
            row.update({f"{split_name}_{key}": value for key, value in metrics.items()})
            mlflow.log_metrics(
                {
                    f"{split_name}_{key}": value
                    for key, value in metrics.items()
                    if isinstance(value, (int, float)) and math.isfinite(value)
                }
            )

        results_rows.append(row)

results_pdf = pd.DataFrame(results_rows).sort_values(
    by=["validation_average_precision", "validation_f1_yes"],
    ascending=False,
)
display(spark.createDataFrame(results_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Lecture des premiers résultats
# MAGIC
# MAGIC Le tableau suivant se concentre sur la validation. L'accuracy est affichée,
# MAGIC mais la comparaison doit surtout regarder la classe `yes`, la PR-AUC et
# MAGIC le lift dans les 10 % de clients les mieux scorés.

# COMMAND ----------

validation_columns = [
    "model",
    "validation_accuracy",
    "validation_balanced_accuracy",
    "validation_precision_yes",
    "validation_recall_yes",
    "validation_f1_yes",
    "validation_average_precision",
    "validation_roc_auc",
    "validation_top_10_percent_precision",
    "validation_top_10_percent_recall",
    "validation_top_10_percent_lift",
]

validation_results_pdf = results_pdf.loc[:, validation_columns].copy()
display(spark.createDataFrame(validation_results_pdf))

best_model = validation_results_pdf.iloc[0]["model"]
print(f"Meilleur modèle provisoire selon PR-AUC validation: {best_model}")
print("Important: aucune métrique de test n'a été calculée dans ce notebook.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prochaine étape
# MAGIC
# MAGIC Les résultats de ce notebook servent à choisir une direction de travail,
# MAGIC pas à annoncer une performance finale. Le prochain notebook affinera les
# MAGIC hyperparamètres et le seuil sur `validation`, puis figera la décision
# MAGIC avant l'évaluation unique du test.
