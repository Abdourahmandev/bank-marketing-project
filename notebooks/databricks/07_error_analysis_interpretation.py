# Databricks notebook source
# MAGIC %md
# MAGIC # 07 - Analyse des erreurs et interpretation
# MAGIC
# MAGIC Ce notebook explique le modele final apres l'evaluation du test :
# MAGIC
# MAGIC - faux positifs et faux negatifs ;
# MAGIC - importance des variables ;
# MAGIC - performance par sous-groupes ;
# MAGIC - limites metier et risques d'utilisation.

# COMMAND ----------

# MAGIC %run ./00_configuration

# COMMAND ----------

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from sklearn.inspection import permutation_importance

from bank_marketing.modeling import (
    FINAL_BUSINESS_THRESHOLD,
    FINAL_REFIT_STRATEGY,
    RANDOM_STATE,
    SELECTED_TUNING_MODEL_NAME,
    VALIDATION_BUDGET_FRACTION,
    build_model_pipeline,
    positive_class_scores,
    predictions_from_threshold,
    selected_tuning_spec,
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

if FINAL_REFIT_STRATEGY != "train_only":
    raise ValueError(f"Strategie finale non prise en charge: {FINAL_REFIT_STRATEGY}")

selected_spec = selected_tuning_spec(random_state=RANDOM_STATE)

print("Modele interprete")
print(f"- modele       : {SELECTED_TUNING_MODEL_NAME}")
print(f"- unknown      : {selected_spec.unknown_strategy}")
print(f"- seuil metier : {FINAL_BUSINESS_THRESHOLD:.12f}")
print(f"- refit        : {FINAL_REFIT_STRATEGY}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chargement et controle de Silver

# COMMAND ----------

try:
    silver_df = spark.table(SILVER_TABLE)
except Exception as exc:
    raise RuntimeError(
        f"Table {SILVER_TABLE} introuvable. Executer 03_preprocessing_silver avant l'analyse."
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
# MAGIC ## Reconstruction du candidat final

# COMMAND ----------

pipeline = build_model_pipeline(selected_spec)
pipeline.fit(splits.X_train, splits.y_train)

test_scores = positive_class_scores(pipeline, splits.X_test)
test_predictions = predictions_from_threshold(test_scores, FINAL_BUSINESS_THRESHOLD)

test_pdf = splits.X_test.copy()
test_pdf[SILVER_TARGET_COLUMN] = splits.y_test.astype(int)
test_pdf["score_yes"] = test_scores
test_pdf["predicted_target"] = test_predictions.astype(int)
test_pdf["predicted_label"] = np.where(test_pdf["predicted_target"] == 1, "yes", "no")
test_pdf["actual_label"] = np.where(test_pdf[SILVER_TARGET_COLUMN] == 1, "yes", "no")
test_pdf["error_type"] = np.select(
    [
        (test_pdf[SILVER_TARGET_COLUMN] == 1) & (test_pdf["predicted_target"] == 1),
        (test_pdf[SILVER_TARGET_COLUMN] == 0) & (test_pdf["predicted_target"] == 1),
        (test_pdf[SILVER_TARGET_COLUMN] == 1) & (test_pdf["predicted_target"] == 0),
        (test_pdf[SILVER_TARGET_COLUMN] == 0) & (test_pdf["predicted_target"] == 0),
    ],
    ["true_positive", "false_positive", "false_negative", "true_negative"],
    default="unexpected",
)
test_pdf["rank_score"] = (
    pd.Series(test_scores)
    .rank(method="first", ascending=False)
    .astype(int)
)
test_pdf["in_top_10_percent"] = (
    test_pdf["rank_score"] <= math.ceil(len(test_pdf) * VALIDATION_BUDGET_FRACTION)
)

display(
    spark.createDataFrame(
        test_pdf[
            [
                "actual_label",
                "predicted_label",
                "error_type",
                "score_yes",
                "rank_score",
                "in_top_10_percent",
            ]
        ].head(20)
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Erreurs du modele

# COMMAND ----------

error_summary_pdf = (
    test_pdf.groupby("error_type")
    .agg(
        rows=("error_type", "size"),
        mean_score=("score_yes", "mean"),
        median_score=("score_yes", "median"),
        min_score=("score_yes", "min"),
        max_score=("score_yes", "max"),
        top_10_rows=("in_top_10_percent", "sum"),
    )
    .reset_index()
)
error_summary_pdf["share_of_test"] = error_summary_pdf["rows"] / len(test_pdf)
display(spark.createDataFrame(error_summary_pdf))

high_score_false_positives_pdf = (
    test_pdf.loc[test_pdf["error_type"] == "false_positive"]
    .sort_values("score_yes", ascending=False)
    .head(25)
)
high_score_false_negatives_pdf = (
    test_pdf.loc[test_pdf["error_type"] == "false_negative"]
    .sort_values("score_yes", ascending=False)
    .head(25)
)

example_columns = [
    "score_yes",
    "rank_score",
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "campaign",
    "previously_contacted",
    "previous",
    "poutcome",
    "emp_var_rate",
    "euribor3m",
    "nr_employed",
]

display(spark.createDataFrame(high_score_false_positives_pdf[example_columns]))
display(spark.createDataFrame(high_score_false_negatives_pdf[example_columns]))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Importance des variables
# MAGIC
# MAGIC Les importances natives de la foret sont calculees sur les variables apres
# MAGIC encodage one-hot, puis regroupees par variable d'origine. Une importance
# MAGIC elevee indique une forte utilisation predictive par le modele, pas une
# MAGIC cause de souscription.

# COMMAND ----------


def original_feature_name(encoded_feature: str) -> str:
    if encoded_feature.startswith("numeric__"):
        return encoded_feature.replace("numeric__", "", 1)
    if encoded_feature.startswith("categorical__"):
        category_name = encoded_feature.replace("categorical__", "", 1)
        for feature in DEPLOYMENT_CATEGORICAL_FEATURES:
            if category_name == feature or category_name.startswith(f"{feature}_"):
                return feature
    return encoded_feature


preprocessor = pipeline.named_steps["preprocessor"]
model = pipeline.named_steps["model"]
encoded_features = preprocessor.get_feature_names_out()
native_importance_pdf = pd.DataFrame(
    {
        "encoded_feature": encoded_features,
        "original_feature": [original_feature_name(feature) for feature in encoded_features],
        "importance": model.feature_importances_,
    }
).sort_values("importance", ascending=False)

feature_importance_pdf = (
    native_importance_pdf.groupby("original_feature", as_index=False)
    .agg(
        importance=("importance", "sum"),
        encoded_feature_count=("encoded_feature", "size"),
    )
    .sort_values("importance", ascending=False)
)
feature_importance_pdf["importance_share"] = (
    feature_importance_pdf["importance"] / feature_importance_pdf["importance"].sum()
)

display(spark.createDataFrame(feature_importance_pdf))
display(spark.createDataFrame(native_importance_pdf.head(30)))

fig_importance, ax_importance = plt.subplots(figsize=(8, 6))
top_features_for_plot = feature_importance_pdf.head(15).sort_values("importance")
ax_importance.barh(
    top_features_for_plot["original_feature"],
    top_features_for_plot["importance"],
)
ax_importance.set_title("Random forest feature importance by original feature")
ax_importance.set_xlabel("Summed native importance")
display(fig_importance)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Importance par permutation
# MAGIC
# MAGIC La permutation mesure la perte de PR-AUC lorsque chaque variable originale
# MAGIC est melangee. Elle est plus couteuse, mais elle tient compte de la pipeline
# MAGIC complete.

# COMMAND ----------

permutation_result = permutation_importance(
    pipeline,
    splits.X_test,
    splits.y_test,
    scoring="average_precision",
    n_repeats=5,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

permutation_importance_pdf = pd.DataFrame(
    {
        "feature": DEPLOYMENT_FEATURES,
        "importance_mean": permutation_result.importances_mean,
        "importance_std": permutation_result.importances_std,
    }
).sort_values("importance_mean", ascending=False)

display(spark.createDataFrame(permutation_importance_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Performance par sous-groupes
# MAGIC
# MAGIC Ces tableaux servent a repérer des groupes ou le modele est instable. Ils
# MAGIC ne prouvent pas une relation causale et ne suffisent pas a valider une
# MAGIC utilisation equitable.

# COMMAND ----------


def subgroup_metrics(frame: pd.DataFrame, column: str, *, min_rows: int = 100) -> pd.DataFrame:
    rows = []
    for value, group in frame.groupby(column, dropna=False):
        if len(group) < min_rows:
            continue
        positives = int(group[SILVER_TARGET_COLUMN].sum())
        predicted_positives = int(group["predicted_target"].sum())
        true_positives = int(
            ((group[SILVER_TARGET_COLUMN] == 1) & (group["predicted_target"] == 1)).sum()
        )
        false_positives = int(
            ((group[SILVER_TARGET_COLUMN] == 0) & (group["predicted_target"] == 1)).sum()
        )
        precision_yes = (
            true_positives / predicted_positives if predicted_positives else 0.0
        )
        recall_yes = true_positives / positives if positives else 0.0
        rows.append(
            {
                "feature": column,
                "value": str(value),
                "rows": len(group),
                "positive_rate": positives / len(group),
                "mean_score": group["score_yes"].mean(),
                "predicted_positive_rate": predicted_positives / len(group),
                "precision_yes": precision_yes,
                "recall_yes": recall_yes,
                "false_positives": false_positives,
                "true_positives": true_positives,
            }
        )
    return pd.DataFrame(rows)


subgroup_columns = [
    "job",
    "education",
    "marital",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "poutcome",
    "previously_contacted",
]

subgroup_metrics_pdf = pd.concat(
    [subgroup_metrics(test_pdf, column) for column in subgroup_columns],
    ignore_index=True,
)
subgroup_metrics_pdf = subgroup_metrics_pdf.sort_values(
    ["feature", "rows"],
    ascending=[True, False],
)

display(spark.createDataFrame(subgroup_metrics_pdf))

risky_subgroups_pdf = subgroup_metrics_pdf.sort_values(
    ["predicted_positive_rate", "rows"],
    ascending=[False, False],
).head(25)
display(spark.createDataFrame(risky_subgroups_pdf))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusions d'interpretation

# COMMAND ----------

top_native_features = feature_importance_pdf.head(8)["original_feature"].tolist()
top_permutation_features = permutation_importance_pdf.head(8)["feature"].tolist()

error_counts = test_pdf["error_type"].value_counts().to_dict()
top_10_precision = float(
    test_pdf.loc[test_pdf["in_top_10_percent"], SILVER_TARGET_COLUMN].mean()
)
overall_positive_rate = float(test_pdf[SILVER_TARGET_COLUMN].mean())
top_10_lift = top_10_precision / overall_positive_rate

interpretation_summary = {
    "selected_model": SELECTED_TUNING_MODEL_NAME,
    "business_threshold": FINAL_BUSINESS_THRESHOLD,
    "refit_strategy": FINAL_REFIT_STRATEGY,
    "test_rows": int(len(test_pdf)),
    "true_positives": int(error_counts.get("true_positive", 0)),
    "false_positives": int(error_counts.get("false_positive", 0)),
    "false_negatives": int(error_counts.get("false_negative", 0)),
    "true_negatives": int(error_counts.get("true_negative", 0)),
    "top_10_precision": top_10_precision,
    "overall_positive_rate": overall_positive_rate,
    "top_10_lift": top_10_lift,
    "top_native_features": top_native_features,
    "top_permutation_features": top_permutation_features,
    "main_limitations": [
        "Le rappel de la classe yes reste faible.",
        "Le modele priorise mieux que le hasard sur test, mais ne capture pas la majorite des souscriptions.",
        "Les variables socio-economiques et de contact peuvent refleter une periode historique particuliere.",
        "Les sous-groupes doivent etre surveilles avant toute utilisation operationnelle.",
        "Les importances ne doivent pas etre interpretees comme des causes.",
    ],
}

print("Synthese interpretation")
print(f"- top 10 precision : {top_10_precision:.4f}")
print(f"- positive rate    : {overall_positive_rate:.4f}")
print(f"- top 10 lift      : {top_10_lift:.4f}")
print(f"- erreurs          : {error_counts}")
print(f"- principales variables natives      : {top_native_features}")
print(f"- principales variables permutation  : {top_permutation_features}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Journalisation MLflow

# COMMAND ----------

experiment_path = f"/Users/{spark.sql('SELECT current_user()').first()[0]}/bank_marketing_interpretation"
mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(experiment_path)

with mlflow.start_run(run_name="error_analysis_interpretation"):
    mlflow.log_param("selected_model", SELECTED_TUNING_MODEL_NAME)
    mlflow.log_param("business_threshold", FINAL_BUSINESS_THRESHOLD)
    mlflow.log_param("refit_strategy", FINAL_REFIT_STRATEGY)
    mlflow.log_param("test_rows", len(test_pdf))
    mlflow.log_metric("top_10_precision", top_10_precision)
    mlflow.log_metric("overall_positive_rate", overall_positive_rate)
    mlflow.log_metric("top_10_lift", top_10_lift)
    for error_type, count in error_counts.items():
        mlflow.log_metric(f"count_{error_type}", int(count))

    mlflow.log_dict(interpretation_summary, "interpretation_summary.json")
    mlflow.log_text(error_summary_pdf.to_csv(index=False), "error_summary.csv")
    mlflow.log_text(
        high_score_false_positives_pdf[example_columns].to_csv(index=False),
        "high_score_false_positives.csv",
    )
    mlflow.log_text(
        high_score_false_negatives_pdf[example_columns].to_csv(index=False),
        "high_score_false_negatives.csv",
    )
    mlflow.log_text(
        feature_importance_pdf.to_csv(index=False),
        "native_feature_importance.csv",
    )
    mlflow.log_text(
        native_importance_pdf.head(100).to_csv(index=False),
        "encoded_feature_importance_top100.csv",
    )
    mlflow.log_text(
        permutation_importance_pdf.to_csv(index=False),
        "permutation_importance.csv",
    )
    mlflow.log_text(
        subgroup_metrics_pdf.to_csv(index=False),
        "subgroup_metrics.csv",
    )
    mlflow.log_figure(fig_importance, "figures/native_feature_importance.png")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prochaine etape
# MAGIC
# MAGIC Construire la demonstration de prediction et sauvegarder la pipeline finale.
