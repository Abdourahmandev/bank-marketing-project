# Bank Marketing Project

Projet de session du cours **420-C74-BB — Techniques d'apprentissage automatique**.

Plateforme principale : **Databricks Free Edition**, avec Unity Catalog, Delta
Lake, MLflow et un Git Folder connecté à GitHub.

## Objectif

Construire un modèle de classification capable d'estimer, avant un appel, la probabilité qu'un client souscrive à un dépôt à terme. Le modèle doit aider à prioriser les appels d'une campagne de télémarketing bancaire.

## Dataset

Le projet utilisera la variante `bank-additional-full.csv` du dataset public [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank), publié sous licence CC BY 4.0.

La variable `duration` sera étudiée, mais exclue du modèle final puisqu'elle n'est connue qu'après l'appel.

## Architecture

- GitHub versionne le code, les notebooks et la documentation.
- Unity Catalog Volume stocke le CSV officiel.
- Delta Lake stocke les tables Bronze, Silver et les prédictions.
- Spark et SQL servent à l'ingestion et aux contrôles.
- pandas et scikit-learn servent à l'entraînement des modèles.
- MLflow Databricks suit les expériences et les modèles.
- DVC conserve la provenance durable du fichier source côté local.

## État

Le CSV officiel a été téléversé dans Unity Catalog et les notebooks de
configuration, d'ingestion Bronze, d'EDA et de prétraitement Silver ont été
exécutés. La table `workspace.default.bank_marketing_silver` contient 41 176
lignes après retrait des 12 répétitions exactes, avec les splits chronologiques
train/validation/test.

Le notebook `04_modeling_baselines.py` a entraîné les premières références
scikit-learn sans utiliser le test final : `DummyClassifier`, régressions
logistiques, arbre de décision et forêt aléatoire. Les métriques sont suivies
dans MLflow Databricks sous l'expérience
`/Users/abdourahman03@gmail.com/bank_marketing_baselines`.

Le notebook `05_tuning_mlflow.py` a exécuté l'optimisation contrôlée dans
Databricks sous l'expérience
`/Users/abdourahman03@gmail.com/bank_marketing_tuning`. Le candidat retenu sur
validation est `random_forest_depth_12_leaf_25_n150_unknown_category`, avec un
seuil métier de `0.525244`. Le lift top 10 % reste inférieur à 1, donc le test
final devait être interprété prudemment dans `06_final_evaluation.py`.

Le notebook `06_final_evaluation.py` a évalué une seule fois le test
chronologique sous l'expérience
`/Users/abdourahman03@gmail.com/bank_marketing_final_evaluation`. Résultat test :
PR-AUC `0.3491`, ROC-AUC `0.5578`, rappel `yes` `0.1276`, précision `yes`
`0.4040`, F1 `yes` `0.1940` et lift top 10 % `1.3148`.

Le notebook `07_error_analysis_interpretation.py` a analysé les erreurs, les
variables importantes, les sous-groupes et les limites sous l'expérience
`/Users/abdourahman03@gmail.com/bank_marketing_interpretation`. Les variables
les plus importantes selon la forêt sont notamment `age`, `euribor3m`, `job`,
`campaign`, `day_of_week` et `month`. Les importances ne sont pas interprétées
comme des causes.

Le notebook `08_inference_demo.py` a sauvegardé la pipeline finale avec joblib
dans le Volume Unity Catalog :
`/Volumes/workspace/default/bank_marketing/models/bank_marketing_final_pipeline.joblib`.
Il recharge cet artefact, score 8 236 clients du split test et écrit la table
Delta `workspace.default.bank_marketing_predictions`. La démonstration produit
802 prédictions positives au seuil `0.525244`, avec une précision top 10 % de
`0.4053` et un lift top 10 % de `1.3148`. L'expérience MLflow associée est
`/Users/abdourahman03@gmail.com/bank_marketing_inference_demo`.

## Documentation de travail

- [Plan d'action détaillé](plan_action.md)
- [Journal de suivi et registre des décisions](SUIVI_PROJET.md)
- [Configuration Databricks](docs/databricks_setup.md)

Les notebooks Databricks se trouvent dans [`notebooks/databricks/`](notebooks/databricks/).
