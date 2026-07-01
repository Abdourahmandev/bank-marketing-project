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

La configuration Databricks, le contrat de données et les notebooks initiaux
d'ingestion/EDA sont préparés. Le CSV doit encore être téléversé dans Unity
Catalog et la table Bronze doit être exécutée. Aucun résultat de modèle n'est
encore disponible.

## Documentation de travail

- [Plan d'action détaillé](plan_action.md)
- [Journal de suivi et registre des décisions](SUIVI_PROJET.md)
- [Configuration Databricks](docs/databricks_setup.md)

Les notebooks Databricks se trouvent dans [`notebooks/databricks/`](notebooks/databricks/).
