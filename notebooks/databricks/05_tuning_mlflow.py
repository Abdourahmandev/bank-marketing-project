# Databricks notebook source
# MAGIC %md
# MAGIC # 05 — Optimisation controlee avec MLflow
# MAGIC
# MAGIC Ce notebook affine les modeles de `04_modeling_baselines.py` sans toucher
# MAGIC au jeu `test`. Les decisions sont prises uniquement avec `train` et
# MAGIC `validation`.
# MAGIC
# MAGIC Objectifs :
# MAGIC
# MAGIC - comparer deux traitements de `unknown` ;
# MAGIC - tester quelques hyperparametres raisonnables ;
# MAGIC - choisir un candidat selon lift top 10 %, PR-AUC et rappel de `yes` ;
# MAGIC - fixer un seuil metier sur validation pour un budget de 10 % d'appels.

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
    build_model_pipeline,
    controlled_tuning_specs,
    evaluate_binary_predictions,
    positive_class_scores,
    predictions_from_threshold,
    split_silver_frame,
    threshold_for_top_budget,
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
        f"Table {SILVER_TABLE} introuvable. Executer 03_preprocessing_silver avant le tuning."
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

print("Table Silver prete pour l'optimisation")
print(f"- train rows      : {len(splits.X_train):,}")
print(f"- validation rows : {len(splits.X_validation):,}")
print(f"- test rows charges mais non evalues : {len(splits.X_test):,}")
print(f"- variables modele: {len(DEPLOYMENT_FEATURES)}")
print(f"- budget metier   : {VALIDATION_BUDGET_FRACTION:.0%} des clients")
display(splits.split_summary)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configurations testees
# MAGIC
# MAGIC La grille reste volontairement courte. Le but est d'obtenir une decision
# MAGIC defendable avant le test final, pas de multiplier les essais au hasard.

# COMMAND ----------

tuning_specs = controlled_tuning_specs(random_state=RANDOM_STATE)
specs_pdf = pd.DataFrame(
    [
        {
            "model": spec.name,
            "unknown_strategy": spec.unknown_strategy,
            "estimator": type(spec.estimator).__name__,
            "description": spec.description,
        }
        for spec in tuning_specs
    ]
)
display(spark.createDataFrame(specs_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execution MLflow
# MAGIC
# MAGIC Chaque configuration est ajustee sur `train`. Les metriques de selection
# MAGIC sont calculees sur `validation`. Le seuil metier correspond au score
# MAGIC minimal dans les 10 % meilleurs scores de validation.

# COMMAND ----------

experiment_path = f"/Users/{spark.sql('SELECT current_user()').first()[0]}/bank_marketing_tuning"
mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(experiment_path)

try:
    mlflow.autolog(log_models=False, silent=True)
except TypeError:
    mlflow.autolog()


def finite_metrics(metrics: dict[str, float]) -> dict[str, float]:
    return {
        key: value
        for key, value in metrics.items()
        if isinstance(value, (int, float)) and math.isfinite(float(value))
    }


def log_estimator_params(estimator: object) -> None:
    params = estimator.get_params(deep=False)
    for name, value in params.items():
        if value is None or isinstance(value, (str, int, float, bool)):
            mlflow.log_param(f"model__{name}", value)


results_rows = []
fitted_models = {}

for spec in tuning_specs:
    with mlflow.start_run(run_name=spec.name):
        pipeline = build_model_pipeline(spec)
        pipeline.fit(splits.X_train, splits.y_train)
        fitted_models[spec.name] = pipeline

        row = {
            "model": spec.name,
            "unknown_strategy": spec.unknown_strategy,
            "estimator": type(spec.estimator).__name__,
            "description": spec.description,
        }

        mlflow.log_param("model_name", spec.name)
        mlflow.log_param("unknown_strategy", spec.unknown_strategy)
        mlflow.log_param("estimator", type(spec.estimator).__name__)
        mlflow.log_param("description", spec.description)
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("train_rows", len(splits.X_train))
        mlflow.log_param("validation_rows", len(splits.X_validation))
        mlflow.log_param("test_rows_not_evaluated", len(splits.X_test))
        mlflow.log_param("feature_count", len(DEPLOYMENT_FEATURES))
        mlflow.log_param("numeric_feature_count", len(DEPLOYMENT_NUMERIC_FEATURES))
        mlflow.log_param("categorical_feature_count", len(DEPLOYMENT_CATEGORICAL_FEATURES))
        mlflow.log_param("test_split_used_for_metrics", False)
        log_estimator_params(spec.estimator)

        validation_scores = None
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
                finite_metrics({f"{split_name}_{key}": value for key, value in metrics.items()})
            )
            if split_name == "validation":
                validation_scores = scores

        if validation_scores is None:
            raise AssertionError("Les scores de validation doivent etre calcules.")

        business_threshold = threshold_for_top_budget(
            validation_scores,
            budget_fraction=VALIDATION_BUDGET_FRACTION,
        )
        budget_predictions = predictions_from_threshold(validation_scores, business_threshold)
        budget_metrics = evaluate_binary_predictions(
            splits.y_validation,
            budget_predictions,
            validation_scores,
            budget_fraction=VALIDATION_BUDGET_FRACTION,
        )

        row["business_threshold"] = business_threshold
        row.update({f"validation_budget_{key}": value for key, value in budget_metrics.items()})
        mlflow.log_param("business_threshold_rule", "validation_top_10_percent_budget")
        mlflow.log_metric("business_threshold", business_threshold)
        mlflow.log_metrics(
            finite_metrics(
                {
                    f"validation_budget_{key}": value
                    for key, value in budget_metrics.items()
                }
            )
        )

        results_rows.append(row)

results_pdf = pd.DataFrame(results_rows)

selection_sort_columns = [
    "validation_top_10_percent_lift",
    "validation_average_precision",
    "validation_recall_yes",
    "validation_f1_yes",
]
ranked_results_pdf = results_pdf.sort_values(
    by=selection_sort_columns,
    ascending=[False, False, False, False],
).reset_index(drop=True)

display(spark.createDataFrame(ranked_results_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Comparaison du traitement de `unknown`
# MAGIC
# MAGIC Cette synthese indique si transformer `unknown` en valeur manquante apporte
# MAGIC un gain de validation par rapport a le conserver comme categorie explicite.

# COMMAND ----------

unknown_summary_pdf = (
    ranked_results_pdf.groupby("unknown_strategy")
    .agg(
        runs=("model", "count"),
        best_validation_average_precision=("validation_average_precision", "max"),
        best_validation_top_10_percent_lift=("validation_top_10_percent_lift", "max"),
        best_validation_recall_yes=("validation_recall_yes", "max"),
        best_validation_f1_yes=("validation_f1_yes", "max"),
    )
    .reset_index()
    .sort_values(
        by=[
            "best_validation_average_precision",
            "best_validation_top_10_percent_lift",
        ],
        ascending=False,
    )
)
display(spark.createDataFrame(unknown_summary_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Candidat retenu avant test
# MAGIC
# MAGIC La selection est figee ici avant le notebook `06_final_evaluation.py`.
# MAGIC Le test final reste non utilise dans cette etape.

# COMMAND ----------

best_row = ranked_results_pdf.iloc[0].to_dict()
selection_summary = {
    "selected_model": best_row["model"],
    "unknown_strategy": best_row["unknown_strategy"],
    "estimator": best_row["estimator"],
    "selection_rule": "validation_top_10_lift, then average_precision, recall_yes, f1_yes",
    "business_threshold_rule": "validation_top_10_percent_budget",
    "business_threshold": float(best_row["business_threshold"]),
    "validation_average_precision": float(best_row["validation_average_precision"]),
    "validation_roc_auc": float(best_row["validation_roc_auc"]),
    "validation_recall_yes": float(best_row["validation_recall_yes"]),
    "validation_f1_yes": float(best_row["validation_f1_yes"]),
    "validation_top_10_percent_lift": float(best_row["validation_top_10_percent_lift"]),
    "validation_budget_precision_yes": float(best_row["validation_budget_precision_yes"]),
    "validation_budget_recall_yes": float(best_row["validation_budget_recall_yes"]),
    "test_split_used_for_metrics": False,
}

with mlflow.start_run(run_name="selected_candidate_summary"):
    mlflow.log_param("selected_model", selection_summary["selected_model"])
    mlflow.log_param("unknown_strategy", selection_summary["unknown_strategy"])
    mlflow.log_param("estimator", selection_summary["estimator"])
    mlflow.log_param("selection_rule", selection_summary["selection_rule"])
    mlflow.log_param("business_threshold_rule", selection_summary["business_threshold_rule"])
    mlflow.log_param("test_split_used_for_metrics", False)
    mlflow.log_metrics(
        {
            key: value
            for key, value in selection_summary.items()
            if isinstance(value, (int, float)) and math.isfinite(float(value))
        }
    )
    mlflow.log_dict(selection_summary, "selection_summary.json")

print("Candidat retenu avant test final")
print(f"- modele              : {selection_summary['selected_model']}")
print(f"- unknown_strategy    : {selection_summary['unknown_strategy']}")
print(f"- seuil metier        : {selection_summary['business_threshold']:.6f}")
print(f"- validation PR-AUC   : {selection_summary['validation_average_precision']:.4f}")
print(f"- validation lift 10% : {selection_summary['validation_top_10_percent_lift']:.4f}")
print(f"- test utilise        : {selection_summary['test_split_used_for_metrics']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prochaine etape
# MAGIC
# MAGIC Le notebook `06_final_evaluation.py` devra reconstruire exactement le
# MAGIC candidat retenu, appliquer le seuil fixe ci-dessus et evaluer une seule
# MAGIC fois le jeu `test`.
