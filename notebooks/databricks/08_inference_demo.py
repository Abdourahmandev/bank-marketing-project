# Databricks notebook source
# MAGIC %md
# MAGIC # 08 - Demonstration de prediction
# MAGIC
# MAGIC Ce notebook reconstruit la pipeline finale, la sauvegarde avec joblib,
# MAGIC recharge l'objet sauvegarde, puis produit une table Delta de predictions.
# MAGIC La demonstration utilise le split `test` historique comme jeu de clients a
# MAGIC scorer, mais le code de prediction ne lit pas la cible et n'utilise pas
# MAGIC `duration`.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from __future__ import annotations

import json
import math
from pathlib import Path

import mlflow
import pandas as pd
from pyspark.sql import functions as F

from bank_marketing.modeling import (
    FINAL_BUSINESS_THRESHOLD,
    FINAL_REFIT_STRATEGY,
    RANDOM_STATE,
    SELECTED_TUNING_MODEL_NAME,
    VALIDATION_BUDGET_FRACTION,
    build_model_pipeline,
    selected_tuning_spec,
    split_silver_frame,
)
from bank_marketing.predict import (
    PREDICTED_TARGET_COLUMN,
    RANK_COLUMN,
    SCORE_COLUMN,
    load_pipeline,
    prediction_schema,
    save_pipeline,
    score_customers,
    top_recommendations,
)
from bank_marketing.preprocessing import (
    DEPLOYMENT_FEATURES,
    EXPECTED_SILVER_ROWS,
    EXPECTED_SILVER_SPLIT_COUNTS,
    EXPECTED_SILVER_TARGET_COUNTS,
    SILVER_TARGET_COLUMN,
    SOURCE_ROW_COLUMN,
    SPLIT_COLUMN,
)

if FINAL_REFIT_STRATEGY != "train_only":
    raise ValueError(f"Strategie finale non prise en charge: {FINAL_REFIT_STRATEGY}")

selected_spec = selected_tuning_spec(random_state=RANDOM_STATE)
if selected_spec.name != SELECTED_TUNING_MODEL_NAME:
    raise AssertionError("La configuration finale ne correspond pas au candidat fige.")

MODEL_DIRECTORY = f"{VOLUME_PATH}/models"
FINAL_PIPELINE_PATH = f"{MODEL_DIRECTORY}/bank_marketing_final_pipeline.joblib"
PREDICTION_SCHEMA_PATH = f"{MODEL_DIRECTORY}/prediction_schema.json"

print("Demonstration de prediction")
print(f"- modele       : {SELECTED_TUNING_MODEL_NAME}")
print(f"- unknown      : {selected_spec.unknown_strategy}")
print(f"- seuil metier : {FINAL_BUSINESS_THRESHOLD:.12f}")
print(f"- refit        : {FINAL_REFIT_STRATEGY}")
print(f"- modele joblib: {FINAL_PIPELINE_PATH}")
print(f"- table sortie : {PREDICTIONS_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chargement de Silver

# COMMAND ----------

try:
    silver_df = spark.table(SILVER_TABLE)
except Exception as exc:
    raise RuntimeError(
        f"Table {SILVER_TABLE} introuvable. Executer 03_preprocessing_silver avant la demo."
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
    raise AssertionError("Fuite detectee: duration apparait dans DEPLOYMENT_FEATURES.")

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
display(splits.split_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Entrainement et sauvegarde joblib

# COMMAND ----------

pipeline = build_model_pipeline(selected_spec)
pipeline.fit(splits.X_train, splits.y_train)

pipeline_path = save_pipeline(pipeline, FINAL_PIPELINE_PATH)
loaded_pipeline = load_pipeline(pipeline_path)

Path(PREDICTION_SCHEMA_PATH).write_text(
    json.dumps(prediction_schema(), indent=2),
    encoding="utf-8",
)

print(f"Pipeline sauvegardee: {pipeline_path}")
print(f"Schema sauvegarde: {PREDICTION_SCHEMA_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Scoring de demonstration

# COMMAND ----------

test_metadata_pdf = (
    silver_pdf.loc[
        silver_pdf[SPLIT_COLUMN] == "test",
        [SOURCE_ROW_COLUMN, SILVER_TARGET_COLUMN],
    ]
    .sort_values(SOURCE_ROW_COLUMN, kind="stable")
    .reset_index(drop=True)
)

scored_test_pdf = score_customers(
    loaded_pipeline,
    splits.X_test,
    threshold=FINAL_BUSINESS_THRESHOLD,
    include_input_columns=True,
).reset_index(drop=True)
scored_test_pdf.insert(0, SOURCE_ROW_COLUMN, test_metadata_pdf[SOURCE_ROW_COLUMN])
scored_test_pdf["actual_target"] = test_metadata_pdf[SILVER_TARGET_COLUMN].astype(int)
scored_test_pdf["actual_label"] = scored_test_pdf["actual_target"].map(
    {0: "no", 1: "yes"}
)

top_10_count = math.ceil(len(scored_test_pdf) * VALIDATION_BUDGET_FRACTION)
scored_test_pdf["in_top_10_percent"] = scored_test_pdf[RANK_COLUMN] <= top_10_count

prediction_output_pdf = scored_test_pdf[
    [
        SOURCE_ROW_COLUMN,
        SCORE_COLUMN,
        PREDICTED_TARGET_COLUMN,
        "predicted_label",
        RANK_COLUMN,
        "threshold",
        "in_top_10_percent",
        "actual_target",
        "actual_label",
    ]
].copy()

spark.createDataFrame(prediction_output_pdf).write.mode("overwrite").option(
    "overwriteSchema",
    "true",
).saveAsTable(PREDICTIONS_TABLE)

demo_columns = [
    SOURCE_ROW_COLUMN,
    SCORE_COLUMN,
    "predicted_label",
    "actual_label",
    RANK_COLUMN,
    "age",
    "job",
    "education",
    "month",
    "campaign",
    "previously_contacted",
    "euribor3m",
]
demo_recommendations_pdf = top_recommendations(
    scored_test_pdf[demo_columns],
    count=10,
)

display(spark.createDataFrame(demo_recommendations_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Synthese et journalisation MLflow

# COMMAND ----------

top_10_pdf = scored_test_pdf.loc[scored_test_pdf["in_top_10_percent"]]
top_10_precision = float(top_10_pdf["actual_target"].mean())
overall_positive_rate = float(scored_test_pdf["actual_target"].mean())
top_10_lift = top_10_precision / overall_positive_rate
predicted_positive_count = int(scored_test_pdf[PREDICTED_TARGET_COLUMN].sum())

summary = {
    "selected_model": SELECTED_TUNING_MODEL_NAME,
    "unknown_strategy": selected_spec.unknown_strategy,
    "business_threshold": FINAL_BUSINESS_THRESHOLD,
    "refit_strategy": FINAL_REFIT_STRATEGY,
    "pipeline_path": str(pipeline_path),
    "prediction_schema_path": PREDICTION_SCHEMA_PATH,
    "predictions_table": PREDICTIONS_TABLE,
    "scored_rows": int(len(scored_test_pdf)),
    "predicted_positive_count": predicted_positive_count,
    "top_10_count": int(top_10_count),
    "top_10_precision": top_10_precision,
    "overall_positive_rate": overall_positive_rate,
    "top_10_lift": top_10_lift,
    "top_score": float(demo_recommendations_pdf.iloc[0][SCORE_COLUMN]),
}

experiment_path = f"/Users/{spark.sql('SELECT current_user()').first()[0]}/bank_marketing_inference_demo"
mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(experiment_path)

with mlflow.start_run(run_name="inference_demo"):
    mlflow.log_param("selected_model", SELECTED_TUNING_MODEL_NAME)
    mlflow.log_param("unknown_strategy", selected_spec.unknown_strategy)
    mlflow.log_param("business_threshold", FINAL_BUSINESS_THRESHOLD)
    mlflow.log_param("refit_strategy", FINAL_REFIT_STRATEGY)
    mlflow.log_param("pipeline_path", str(pipeline_path))
    mlflow.log_param("predictions_table", PREDICTIONS_TABLE)
    mlflow.log_metric("scored_rows", len(scored_test_pdf))
    mlflow.log_metric("predicted_positive_count", predicted_positive_count)
    mlflow.log_metric("top_10_precision", top_10_precision)
    mlflow.log_metric("overall_positive_rate", overall_positive_rate)
    mlflow.log_metric("top_10_lift", top_10_lift)
    mlflow.log_metric("top_score", summary["top_score"])

    mlflow.log_artifact(str(pipeline_path), artifact_path="model")
    mlflow.log_dict(prediction_schema(), "prediction_schema.json")
    mlflow.log_dict(summary, "inference_demo_summary.json")
    mlflow.log_text(
        demo_recommendations_pdf.to_csv(index=False),
        "demo_recommendations.csv",
    )
    mlflow.log_text(
        prediction_output_pdf.head(100).to_csv(index=False),
        "prediction_sample_top100_source_order.csv",
    )

print("Demonstration terminee")
print(f"- lignes scorees          : {summary['scored_rows']}")
print(f"- predictions positives   : {summary['predicted_positive_count']}")
print(f"- precision top 10 %      : {summary['top_10_precision']:.4f}")
print(f"- lift top 10 %           : {summary['top_10_lift']:.4f}")
print(f"- pipeline joblib         : {summary['pipeline_path']}")
print(f"- table Delta predictions : {summary['predictions_table']}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps(summary, ensure_ascii=False))
