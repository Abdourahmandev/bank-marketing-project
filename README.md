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

## Documentation de travail

- [Plan d'action détaillé](plan_action.md)
- [Journal de suivi et registre des décisions](SUIVI_PROJET.md)
- [Configuration Databricks](docs/databricks_setup.md)

Les notebooks Databricks se trouvent dans [`notebooks/databricks/`](notebooks/databricks/).
