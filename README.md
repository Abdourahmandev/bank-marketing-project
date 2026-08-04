# Bank Marketing Project

Projet de session du cours **420-C74-BB - Techniques d'apprentissage automatique**.

Ce projet construit une pipeline de classification capable d'estimer, **avant un
appel**, la probabilité qu'un client souscrive à un dépôt à terme. Le but
métier est d'aider une équipe marketing bancaire à prioriser les clients les
plus prometteurs, sans utiliser d'information connue seulement après l'appel.

Plateforme principale : **Databricks Free Edition**, avec Unity Catalog, Delta
Lake, MLflow, DVC, GitHub Actions et un Git Folder connecté à GitHub.

## Résultat Court

Le modèle final est une forêt aléatoire scikit-learn avec prétraitement intégré
dans une `Pipeline`. La variable `duration` est exclue du modèle, car elle
représente la durée de l'appel et n'est pas disponible au moment de choisir les
clients à contacter.

Évaluation finale sur le split chronologique `test` :

| Métrique | Valeur |
|---|---:|
| lignes test | 8 236 |
| positifs test | 2 539 |
| PR-AUC | 0.3491 |
| ROC-AUC | 0.5578 |
| précision `yes` | 0.4040 |
| rappel `yes` | 0.1276 |
| F1 `yes` | 0.1940 |
| lift top 10 % | 1.3148 |
| précision top 10 % | 0.4053 |

Interprétation honnête : le modèle priorise mieux qu'une sélection aléatoire sur
le test final, mais son rappel reste faible. Il doit donc être présenté comme un
outil de priorisation imparfait, pas comme une solution complète de ciblage.

## Dataset

Dataset public : **UCI Bank Marketing**, variante `bank-additional-full.csv`.

- Source : <https://archive.ics.uci.edu/dataset/222/bank>
- Téléchargement : <https://archive.ics.uci.edu/static/public/222/bank+marketing.zip>
- Citation : Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing*. UCI
  Machine Learning Repository. <https://doi.org/10.24432/C5K306>
- Licence : Creative Commons Attribution 4.0 International, CC BY 4.0
- Lignes brutes : 41 188
- Colonnes brutes : 21
- Cible : `y`, avec classes `yes` et `no`
- Classe positive : `yes`
- SHA-256 attendu :
  `74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8`

Le manifeste complet se trouve dans
[`data/dataset_manifest.json`](data/dataset_manifest.json).

## Architecture

Le projet utilise une architecture hybride :

1. GitHub versionne le code, les notebooks, la documentation et les pointeurs DVC.
2. DVC suit la provenance du CSV brut côté local.
3. Unity Catalog Volume stocke le CSV utilisé dans Databricks.
4. Delta Lake stocke les tables Bronze, Silver et prédictions.
5. Spark sert à l'ingestion et aux contrôles de tables.
6. pandas et scikit-learn servent à l'entraînement des modèles.
7. MLflow Databricks suit les expériences, métriques et artefacts.
8. GitHub Actions valide les tests et la compilation Python à chaque push.

Tables et artefacts principaux :

| Élément | Emplacement |
|---|---|
| Silver Delta | `workspace.default.bank_marketing_silver` |
| Prédictions Delta | `workspace.default.bank_marketing_predictions` |
| Pipeline joblib | `/Volumes/workspace/default/bank_marketing/models/bank_marketing_final_pipeline.joblib` |
| Schéma de prédiction | `/Volumes/workspace/default/bank_marketing/models/prediction_schema.json` |

## Méthodologie

Le fichier officiel est ordonné chronologiquement. La séparation principale est
donc :

- 60 % entraînement ;
- 20 % validation ;
- 20 % test final.

Cette séparation simule une utilisation réelle : entraîner sur le passé et
prédire sur des campagnes futures.

Règles anti-fuite :

- `duration` exclue des variables déployables ;
- imputation, encodage one-hot et normalisation ajustés seulement dans une
  pipeline scikit-learn ;
- validation utilisée pour choisir le modèle, les hyperparamètres et le seuil ;
- test final consulté une seule fois après avoir figé la configuration.

## Notebooks Databricks

Les notebooks source sont dans
[`notebooks/databricks/`](notebooks/databricks/).

| Ordre | Notebook | Rôle |
|---:|---|---|
| 00 | `00_configuration.py` | configuration Unity Catalog, Volume, tables et chemins |
| 01 | `01_ingestion_bronze.py` | ingestion contrôlée du CSV brut en Bronze |
| 02 | `02_eda.py` | exploration initiale, doublons, déséquilibre et fuite `duration` |
| 03 | `03_preprocessing_silver.py` | création de Silver, cible 0/1, splits et variables déployables |
| 04 | `04_modeling_baselines.py` | modèles de référence sans consulter le test |
| 05 | `05_tuning_mlflow.py` | optimisation contrôlée sur validation |
| 06 | `06_final_evaluation.py` | évaluation finale unique sur test |
| 07 | `07_error_analysis_interpretation.py` | erreurs, importances, sous-groupes et limites |
| 08 | `08_inference_demo.py` | sauvegarde joblib, rechargement et table de prédictions |

## Modèle Final

Configuration figée :

- modèle : `random_forest_depth_12_leaf_25_n150_unknown_category` ;
- stratégie `unknown` : conserver `unknown` comme catégorie explicite ;
- stratégie de réentraînement : `train_only` ;
- seuil métier : `0.525244344106127` ;
- budget métier : top 10 % des clients par score.

La stratégie `train_only` a été conservée pour l'évaluation et la sérialisation,
car le seuil avait été calibré sur les scores de validation du modèle entraîné
uniquement sur `train`.

## Expériences MLflow

| Étape | Expérience |
|---|---|
| baselines | `/Users/abdourahman03@gmail.com/bank_marketing_baselines` |
| tuning | `/Users/abdourahman03@gmail.com/bank_marketing_tuning` |
| évaluation finale | `/Users/abdourahman03@gmail.com/bank_marketing_final_evaluation` |
| interprétation | `/Users/abdourahman03@gmail.com/bank_marketing_interpretation` |
| démonstration inference | `/Users/abdourahman03@gmail.com/bank_marketing_inference_demo` |

Runs importants :

- évaluation finale : `0de8816ed1864ce982ee7f911b500b9b` ;
- interprétation : `69da0d26d9dc484882c3d26d35bcf067` ;
- démonstration inference : `febd0ffd324e40eaa31a76ecfeaad4f9`.

## Reproduction Locale

Créer un environnement :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Lancer les contrôles :

```powershell
python -m pytest -q
python -m dvc status
```

Validation actuelle :

- tests locaux avec dépendances complètes : `31 passed` ;
- `python -m dvc status` : données et pipelines à jour ;
- GitHub Actions `CI` : tests et compilation Python réussis.

## Données et DVC

Le CSV brut est ignoré par Git. Le pointeur DVC est versionné ici :
[`data/raw/bank-additional-full.csv.dvc`](data/raw/bank-additional-full.csv.dvc).

Sur une nouvelle machine, si aucun remote DVC n'est encore configuré :

1. télécharger l'archive officielle UCI ;
2. extraire l'archive interne `bank-additional.zip` ;
3. placer `bank-additional-full.csv` dans `data/raw/` ;
4. vérifier le SHA-256 indiqué dans `params.yaml` ;
5. lancer `python -m dvc status`.

Le remote DVC durable reste un choix ouvert. Il ne doit pas être configuré avec
un secret ou un chemin personnel publié dans Git.

## Exécution Databricks

Configuration initiale :

1. ouvrir le Git Folder Databricks connecté au dépôt GitHub ;
2. exécuter `notebooks/databricks/00_configuration.py` ;
3. téléverser le CSV officiel dans le Volume affiché, sous `raw/` ;
4. exécuter les notebooks de `01` à `08` dans l'ordre.

Le guide détaillé est dans
[`docs/databricks_setup.md`](docs/databricks_setup.md).

Le projet a aussi été exécuté via Databricks CLI avec le Git Folder :

```powershell
databricks repos update /Users/abdourahman03@gmail.com/bank-marketing-project --branch main --dangerously-force-discard-all
```

## Prédire de Nouveaux Clients

Le module [`src/bank_marketing/predict.py`](src/bank_marketing/predict.py)
contient les fonctions réutilisables :

- `prepare_prediction_features` ;
- `score_customers` ;
- `top_recommendations` ;
- `save_pipeline` ;
- `load_pipeline`.

Le notebook `08_inference_demo.py` démontre le flux complet :

1. reconstruire le modèle final ;
2. sauvegarder la pipeline avec joblib ;
3. recharger la pipeline sauvegardée ;
4. scorer les clients ;
5. écrire `workspace.default.bank_marketing_predictions`.

## Structure du Dépôt

```text
bank-marketing-project/
├── .github/workflows/ci.yml
├── data/
│   ├── dataset_manifest.json
│   └── raw/bank-additional-full.csv.dvc
├── docs/databricks_setup.md
├── notebooks/databricks/
├── src/bank_marketing/
│   ├── data_contract.py
│   ├── modeling.py
│   ├── predict.py
│   └── preprocessing.py
├── tests/
├── params.yaml
├── plan_action.md
├── requirements.txt
└── SUIVI_PROJET.md
```

## Limites

- Le rappel de la classe `yes` reste faible sur le test final.
- Le dataset couvre une période historique précise, de mai 2008 à novembre 2010.
- Les variables économiques et de contact peuvent refléter ce contexte.
- Les importances de variables sont prédictives, pas causales.
- Les sous-groupes doivent être surveillés avant toute utilisation
  opérationnelle.
- Le projet est une démonstration académique, pas un système de production.

## Documentation de Travail

- [Plan d'action détaillé](plan_action.md)
- [Journal de suivi et registre des décisions](SUIVI_PROJET.md)
- [Configuration Databricks](docs/databricks_setup.md)

## Prochaine Étape

Préparer le PowerPoint de 15 minutes et la démonstration orale. Le modèle de
présentation fourni par l'étudiant sera utilisé comme base visuelle.
