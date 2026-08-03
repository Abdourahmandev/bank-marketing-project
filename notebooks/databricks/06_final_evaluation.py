# Databricks notebook source
# MAGIC %md
# MAGIC # 06 - Evaluation finale
# MAGIC
# MAGIC Ce notebook applique la decision figee dans `05_tuning_mlflow.py` et
# MAGIC evalue une seule fois le split `test`.
# MAGIC
# MAGIC Decisions figees avant test :
# MAGIC
# MAGIC - modele : `random_forest_depth_12_leaf_25_n150_unknown_category` ;
# MAGIC - seuil metier : `0.525244344106127` ;
# MAGIC - strategie de reentrainement : conserver le modele ajuste sur `train`.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import mlflow
import pandas as pd
from pyspark.sql import functions as F
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    classification_report,
    confusion_matrix,
)

from bank_marketing.modeling import (
    FINAL_BUSINESS_THRESHOLD,
    FINAL_REFIT_STRATEGY,
    RANDOM_STATE,
    SELECTED_TUNING_MODEL_NAME,
    VALIDATION_BUDGET_FRACTION,
    build_model_pipeline,
    evaluate_binary_predictions,
    positive_class_scores,
    predictions_from_threshold,
    selected_tuning_spec,
    split_silver_frame,
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

print("Configuration finale figee avant test")
print(f"- modele       : {SELECTED_TUNING_MODEL_NAME}")
print(f"- unknown      : {selected_spec.unknown_strategy}")
print(f"- seuil metier : {FINAL_BUSINESS_THRESHOLD:.12f}")
print(f"- refit        : {FINAL_REFIT_STRATEGY}")

# COMMAND ----------

try:
    silver_df = spark.table(SILVER_TABLE)
except Exception as exc:
    raise RuntimeError(
        f"Table {SILVER_TABLE} introuvable. Executer 03_preprocessing_silver avant le test final."
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
# MAGIC ## Ajustement du candidat final
# MAGIC
# MAGIC Le modele est ajuste uniquement sur `train`. Le split `validation` reste
# MAGIC utilise seulement comme reference deja connue. Le split `test` est evalue
# MAGIC dans ce notebook pour la premiere fois.

# COMMAND ----------

pipeline = build_model_pipeline(selected_spec)
pipeline.fit(splits.X_train, splits.y_train)


def evaluate_split(split_name: str, features: pd.DataFrame, target: pd.Series) -> dict[str, float]:
    scores = positive_class_scores(pipeline, features)
    predictions = predictions_from_threshold(scores, FINAL_BUSINESS_THRESHOLD)
    metrics = evaluate_binary_predictions(
        target,
        predictions,
        scores,
        budget_fraction=VALIDATION_BUDGET_FRACTION,
    )
    metrics["predicted_positive_count"] = float(predictions.sum())
    metrics["actual_positive_count"] = float(target.sum())
    metrics["rows"] = float(len(target))
    return metrics


metrics_by_split = {
    "train": evaluate_split("train", splits.X_train, splits.y_train),
    "validation": evaluate_split(
        "validation",
        splits.X_validation,
        splits.y_validation,
    ),
    "test": evaluate_split("test", splits.X_test, splits.y_test),
}

metrics_rows = []
for split_name, metrics in metrics_by_split.items():
    row = {"split": split_name}
    row.update(metrics)
    metrics_rows.append(row)

metrics_pdf = pd.DataFrame(metrics_rows)
display(spark.createDataFrame(metrics_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Matrice de confusion et rapport de classification

# COMMAND ----------

test_scores = positive_class_scores(pipeline, splits.X_test)
test_predictions = predictions_from_threshold(test_scores, FINAL_BUSINESS_THRESHOLD)

confusion_raw = confusion_matrix(
    splits.y_test,
    test_predictions,
    labels=[0, 1],
)
confusion_normalized = confusion_matrix(
    splits.y_test,
    test_predictions,
    labels=[0, 1],
    normalize="true",
)

confusion_pdf = pd.DataFrame(
    [
        {
            "actual": "no",
            "predicted_no": int(confusion_raw[0, 0]),
            "predicted_yes": int(confusion_raw[0, 1]),
            "predicted_no_rate": float(confusion_normalized[0, 0]),
            "predicted_yes_rate": float(confusion_normalized[0, 1]),
        },
        {
            "actual": "yes",
            "predicted_no": int(confusion_raw[1, 0]),
            "predicted_yes": int(confusion_raw[1, 1]),
            "predicted_no_rate": float(confusion_normalized[1, 0]),
            "predicted_yes_rate": float(confusion_normalized[1, 1]),
        },
    ]
)
display(spark.createDataFrame(confusion_pdf))

report_dict = classification_report(
    splits.y_test,
    test_predictions,
    labels=[0, 1],
    target_names=["no", "yes"],
    output_dict=True,
    zero_division=0,
)
report_pdf = (
    pd.DataFrame(report_dict)
    .transpose()
    .reset_index()
    .rename(columns={"index": "label"})
)
display(spark.createDataFrame(report_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Courbes ROC, precision-rappel et confusion

# COMMAND ----------

fig_cm, ax_cm = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay(
    confusion_matrix=confusion_raw,
    display_labels=["no", "yes"],
).plot(ax=ax_cm, colorbar=False)
ax_cm.set_title("Test confusion matrix - fixed threshold")

fig_roc, ax_roc = plt.subplots(figsize=(5, 4))
RocCurveDisplay.from_predictions(splits.y_test, test_scores, ax=ax_roc)
ax_roc.set_title("Test ROC curve")

fig_pr, ax_pr = plt.subplots(figsize=(5, 4))
PrecisionRecallDisplay.from_predictions(splits.y_test, test_scores, ax=ax_pr)
ax_pr.set_title("Test precision-recall curve")

display(fig_cm)
display(fig_roc)
display(fig_pr)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Journalisation MLflow

# COMMAND ----------

experiment_path = f"/Users/{spark.sql('SELECT current_user()').first()[0]}/bank_marketing_final_evaluation"
mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(experiment_path)


def finite_metrics(metrics: dict[str, float]) -> dict[str, float]:
    return {
        key: value
        for key, value in metrics.items()
        if isinstance(value, (int, float)) and math.isfinite(float(value))
    }


summary = {
    "selected_model": SELECTED_TUNING_MODEL_NAME,
    "unknown_strategy": selected_spec.unknown_strategy,
    "business_threshold": FINAL_BUSINESS_THRESHOLD,
    "refit_strategy": FINAL_REFIT_STRATEGY,
    "train_rows": len(splits.X_train),
    "validation_rows": len(splits.X_validation),
    "test_rows": len(splits.X_test),
    "test_average_precision": metrics_by_split["test"]["average_precision"],
    "test_roc_auc": metrics_by_split["test"]["roc_auc"],
    "test_recall_yes": metrics_by_split["test"]["recall_yes"],
    "test_precision_yes": metrics_by_split["test"]["precision_yes"],
    "test_f1_yes": metrics_by_split["test"]["f1_yes"],
    "test_top_10_percent_lift": metrics_by_split["test"]["top_10_percent_lift"],
    "test_top_10_percent_precision": metrics_by_split["test"][
        "top_10_percent_precision"
    ],
    "test_top_10_percent_recall": metrics_by_split["test"][
        "top_10_percent_recall"
    ],
}

with mlflow.start_run(run_name="final_evaluation"):
    mlflow.log_param("selected_model", SELECTED_TUNING_MODEL_NAME)
    mlflow.log_param("unknown_strategy", selected_spec.unknown_strategy)
    mlflow.log_param("business_threshold", FINAL_BUSINESS_THRESHOLD)
    mlflow.log_param("refit_strategy", FINAL_REFIT_STRATEGY)
    mlflow.log_param("test_split_used_for_metrics", True)
    mlflow.log_param("feature_count", len(DEPLOYMENT_FEATURES))
    mlflow.log_param("random_state", RANDOM_STATE)

    for split_name, metrics in metrics_by_split.items():
        mlflow.log_metrics(
            finite_metrics(
                {
                    f"{split_name}_{key}": value
                    for key, value in metrics.items()
                }
            )
        )

    mlflow.log_dict(summary, "final_evaluation_summary.json")
    mlflow.log_text(metrics_pdf.to_csv(index=False), "metrics_by_split.csv")
    mlflow.log_text(confusion_pdf.to_csv(index=False), "test_confusion_matrix.csv")
    mlflow.log_text(report_pdf.to_csv(index=False), "test_classification_report.csv")
    mlflow.log_figure(fig_cm, "figures/test_confusion_matrix.png")
    mlflow.log_figure(fig_roc, "figures/test_roc_curve.png")
    mlflow.log_figure(fig_pr, "figures/test_precision_recall_curve.png")

print("Evaluation finale terminee")
print(f"- test PR-AUC       : {summary['test_average_precision']:.4f}")
print(f"- test ROC-AUC      : {summary['test_roc_auc']:.4f}")
print(f"- test recall yes   : {summary['test_recall_yes']:.4f}")
print(f"- test F1 yes       : {summary['test_f1_yes']:.4f}")
print(f"- test lift top 10% : {summary['test_top_10_percent_lift']:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prochaine etape
# MAGIC
# MAGIC Les metriques de test sont maintenant connues. La suite consiste a analyser
# MAGIC les erreurs, expliquer les limites et preparer une demo de prediction.
