# Suivi détaillé du projet

## 1. Rôle de ce document

Ce fichier est le journal de bord vivant du projet. Il doit répondre en permanence à quatre questions :

1. Qu'est-ce qui a été fait ?
2. Qu'est-ce qui reste à faire ?
3. Pourquoi les décisions ont-elles été prises ?
4. Quelles preuves permettent de considérer une tâche terminée ?

Il doit être mis à jour après chaque séance de travail importante. Le plan cible se trouve dans [`plan_action.md`](plan_action.md). Si la réalisation s'écarte du plan, l'écart et sa raison doivent être inscrits ici.

### Statuts utilisés

- `TERMINÉ` : résultat vérifié et critère de sortie atteint.
- `EN COURS` : travail commencé, mais résultat non encore validé.
- `À FAIRE` : tâche prévue et non commencée.
- `BLOQUÉ` : une dépendance ou une décision empêche d'avancer.
- `ABANDONNÉ` : tâche retirée avec justification.
- `OPTIONNEL` : amélioration non nécessaire au produit minimum viable.

---

## 2. État global au 3 août 2026

| Élément | État | Commentaire |
|---|---|---|
| cadrage du besoin | TERMINÉ | classification des souscriptions avant appel |
| choix du dataset | TERMINÉ | UCI Bank Marketing, variante additional-full |
| dépôt GitHub | TERMINÉ | dépôt créé par l'étudiant |
| clone local | TERMINÉ | clone effectué ; dépôt initialement vide |
| push initial GitHub | TERMINÉ | identité corrigée avec l'adresse GitHub privée `noreply` |
| GitHub App Databricks | TERMINÉ | autorisation et accès au dépôt confirmés par l'étudiant |
| Databricks Git Folder | TERMINÉ | dépôt visible et synchronisable dans le workspace |
| fondation Databricks publiée | TERMINÉ | PR #1 fusionnée dans `main` |
| planification | TERMINÉ | `plan_action.md` créé |
| journal de suivi | TERMINÉ | présent fichier créé |
| arborescence initiale | TERMINÉ | dossiers de données, notebooks, code, modèles, rapports, tests et présentation |
| configuration Databricks | TERMINÉ | notebook de configuration Unity Catalog ajouté |
| manifeste du dataset | TERMINÉ | taille, SHA-256, schéma et comptes de référence ajoutés |
| CSV brut local | TERMINÉ | copie officielle vérifiée dans `data/raw/`, ignorée par Git |
| ingestion Bronze | TERMINÉ | CSV téléversé et notebook exécuté par l'étudiant |
| environnement Python | EN COURS | compute serverless retenu ; scikit-learn et MLflow validés, versions à documenter |
| acquisition avec DVC | À FAIRE | fichier officiel pas encore ajouté au dépôt de projet |
| EDA | EN COURS | notebook initial exécuté ; export des figures finales reste à faire |
| prétraitement | TERMINÉ | table Silver créée et contrôles validés dans Databricks |
| modélisation | TERMINÉ | baselines, tuning et sélection finale exécutés |
| MLflow | TERMINÉ | expériences baselines, tuning et évaluation finale enregistrées |
| évaluation finale | TERMINÉ | notebook 06 exécuté une seule fois sur test chronologique |
| présentation | À FAIRE | plan temporel défini, PowerPoint non créé |

Estimation prudente de l'avancement total : **environ 65 %**. L'architecture,
l'ingestion, l'EDA initiale, Silver, les baselines, le tuning et l'évaluation
finale fonctionnent. La prochaine étape est d'expliquer les erreurs, les
variables importantes, les sous-groupes et les limites métier.

---

## 3. Travail effectué

### Séance du 30 juin 2026 — Analyse du cours et cadrage

#### A. Lecture des consignes du projet

**État : TERMINÉ**

Les documents suivants ont été examinés dans le dépôt local du cours :

- `tp_session/projet_session.docx` ;
- `whiteboards/whiteboard04_tp.pdf` ;
- le plan de cours `e2_420-C74-BB_IA1309_H26_vf.docx` ;
- `travaux_a_faire.docx` ;
- les supports sur l'EDA, l'encodage et la normalisation ;
- les cours et pratiques sur la régression, k-NN, arbres, Naive Bayes, PCA, k-means, ensembles, MLflow, régularisation et DVC.

**Constats :**

- le projet vaut 30 % ;
- le travail doit couvrir toute la matière ;
- le besoin d'affaires, le workflow, les algorithmes, métriques, résultats, difficultés et compétences doivent être présentés ;
- l'accent est placé sur la mise en place d'un pipeline et d'une infrastructure reproductible ;
- la présentation dure 15 minutes, suivie de 5 minutes de questions ;
- le PowerPoint et le code/notebooks doivent être remis ;
- aucun barème détaillé n'est présent dans les fichiers ;
- une phrase des consignes et la liste annoncée des domaines sont absentes du document source.

**Pourquoi cette étape a été faite :** éviter de construire un modèle techniquement intéressant qui ne correspondrait pas aux attentes pédagogiques.

#### B. Choix du projet

**État : TERMINÉ**

Projet retenu : prédire si un client bancaire souscrira à un dépôt à terme afin de prioriser les appels de télémarketing.

**Pourquoi :**

- le problème possède un besoin d'affaires facile à expliquer ;
- il s'agit d'une classification binaire, largement couverte dans le cours ;
- le dataset permet de montrer encodage, normalisation, déséquilibre, modèles multiples et suivi d'expériences ;
- le projet reste réalisable par une seule personne ;
- les résultats peuvent être traduits en impact métier avec le nombre d'appels et le lift.

#### C. Vérification du dataset

**État : TERMINÉ POUR LE CHOIX, À REPRODUIRE DANS LE DÉPÔT**

L'archive officielle UCI a été téléchargée temporairement et inspectée hors du dépôt du projet.

Résultats vérifiés sur `bank-additional-full.csv` :

- forme : `(41188, 21)` ;
- 10 colonnes numériques ;
- 10 prédicteurs catégoriels et une cible catégorielle ;
- cible : 36 548 `no` et 4 640 `yes` ;
- taux positif : environ 11,27 % ;
- 12 doublons exacts ;
- 0 `NaN` brut ;
- présence de `unknown` dans `job`, `marital`, `education`, `default`, `housing` et `loan` ;
- `duration` très différente entre les classes et explicitement déclarée non disponible avant l'appel par la documentation officielle.

**Pourquoi cette vérification a été faite :** le dataset ne devait pas être choisi uniquement à partir de son titre. Il fallait confirmer sa taille, ses types de variables, sa licence et la présence de difficultés analytiques pertinentes.

#### D. Création et clone du dépôt

**État : TERMINÉ**

- Dépôt fourni : `Abdourahmandev/bank-marketing-project`.
- Vérification de l'accès HTTPS effectuée.
- Clone créé localement.
- Git a confirmé que le dépôt était vide.
- Aucun commit ni push n'a été effectué pendant cette séance.

**Pourquoi aucun push :** l'autorisation portait sur le clone et le début des fichiers. Publier des changements est une action distincte ; les modifications seront d'abord relues localement.

#### E. Initialisation documentaire et structurelle

**État : TERMINÉ**

Fichiers créés :

- `README.md` ;
- `plan_action.md` ;
- `SUIVI_PROJET.md` ;
- `.gitignore` ;
- fichiers `.gitkeep` pour conserver l'arborescence vide dans Git.

Dossiers créés :

- `data/raw/` ;
- `data/interim/` ;
- `data/processed/` ;
- `notebooks/` ;
- `src/bank_marketing/` ;
- `models/` ;
- `reports/figures/` ;
- `presentation/` ;
- `tests/`.

**Pourquoi cette structure :** elle sépare clairement données brutes, données transformées, exploration, code réutilisable, modèles, rapports et tests. Elle est inspirée de Cookiecutter Data Science, mentionné dans le tableau blanc du cours.

### Séance du 30 juin 2026 — Migration vers Databricks

#### Objectif

Adapter le projet à Databricks Free Edition sans abandonner les méthodes du cours
ni rendre le projet dépendant de fonctions payantes.

#### Actions effectuées

- connexion GitHub/Databricks terminée par l'étudiant ;
- vérification que `main` local et `origin/main` sont synchronisés ;
- ajout d'un manifeste JSON du dataset officiel ;
- calcul et enregistrement du SHA-256 du CSV complet ;
- création d'un contrat de données réutilisable dans `src/` ;
- création du notebook Databricks `00_configuration.py` ;
- création du notebook `01_ingestion_bronze.py` ;
- création du notebook initial `02_eda.py` ;
- création d'un guide de configuration Databricks ;
- adaptation du plan et du journal à Unity Catalog, Delta Lake et MLflow géré.
- copie du CSV officiel vérifié dans `data/raw/bank-additional-full.csv` pour le téléversement manuel ;
- publication du commit `prepare Databricks foundation` sur une branche dédiée ;
- ouverture de la pull request brouillon GitHub #1 vers `main`.

#### Résultats et preuves

- SHA-256 attendu : `74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8` ;
- taille attendue : 5 834 924 octets ;
- contrat attendu : 41 188 lignes, 21 colonnes, 36 548 `no`, 4 640 `yes` ;
- l'ingestion refuse un fichier différent avant toute écriture Delta ;
- `_source_row_number` est créé dans pandas avant Spark pour préserver l'ordre du CSV.

#### Décisions prises et raisons

- Spark/SQL pour ingestion et tables ; pandas/scikit-learn pour les modèles.
  Le dataset est petit et le cours porte sur scikit-learn.
- Unity Catalog Volume pour le CSV d'exécution ; DVC conserve un rôle de
  provenance côté local.
- MLflow intégré remplacera le serveur MLflow local.
- Le téléchargement UCI ne sera pas exécuté depuis Free Edition, car l'accès
  Internet sortant y est restreint.

#### Prochaine action exacte

Relire et fusionner la pull request #1, tirer `main` dans le Git Folder, exécuter
`00_configuration.py`, téléverser le CSV dans le Volume, puis exécuter
`01_ingestion_bronze.py` et `02_eda.py`.

### Séance du 1er juillet 2026 — Exécution Bronze/EDA et préparation Silver

#### Objectif

Transformer les données contrôlées en un jeu modélisable, sans apprendre de
paramètres sur la validation ou le test.

#### Actions effectuées

- fusion de la pull request #1 et synchronisation de `main` ;
- correction par l'étudiant de la création du sous-dossier `raw` dans le Volume ;
- téléversement du CSV et exécution réussie des notebooks 00, 01 et 02 ;
- inspection locale des 12 groupes de doublons selon la séparation 60/20/20 ;
- création de `src/bank_marketing/preprocessing.py` ;
- création du notebook `03_preprocessing_silver.py` ;
- ajout de tests sur les frontières chronologiques, la fuite et les
  transformations Silver.

#### Résultats et décisions

- les 12 répétitions se trouvent dans le même split que leur première occurrence :
  7 dans train, 3 dans validation et 2 dans test ;
- Silver conserve la première occurrence et retire les 12 répétitions ;
- Silver contient donc 41 176 lignes : 36 537 cibles 0 et 4 639 cibles 1 ;
- les splits contiennent 24 705, 8 235 et 8 236 lignes ;
- les taux positifs diffèrent fortement dans le temps, ce qui justifie une
  validation chronologique ;
- `unknown` reste une catégorie pour la baseline ;
- `pdays=999` devient `previously_contacted=0` et
  `days_since_previous_contact=0` ;
- `duration` reste dans Silver pour l'audit, mais est exclue de
  `DEPLOYMENT_FEATURES`.

#### Pourquoi ces choix

Bronze doit rester une copie fidèle et traçable. Silver peut retirer les
répétitions sans masquer leur existence, car leur nombre et leur emplacement
sont documentés. La transformation de `pdays` empêche qu'une sentinelle 999 soit
interprétée comme un nombre réel de jours. La conservation temporaire de
`unknown` évite une imputation arbitraire avant toute comparaison sur validation.

#### Validation locale

- transformation complète exécutée sur le CSV officiel ;
- 14 tests automatisés réussis ;
- compilation Python et contrôle des espaces Git réussis.

#### Prochaine action exacte

Publier la branche Silver, la tirer dans Databricks, exécuter
`03_preprocessing_silver.py`, puis construire la pipeline scikit-learn et les
baselines dans `04_modeling_baselines.py`.

### Séance du 31 juillet 2026 — Exécution Silver et baselines MLflow

#### Objectif

Créer la table Silver dans Databricks, puis entraîner les premières références
scikit-learn sans utiliser le test final.

#### Actions effectuées

- authentification Databricks CLI avec le profil `bank-marketing` ;
- synchronisation du Git Folder Databricks sur `main` ;
- exécution de `03_preprocessing_silver.py` sur compute serverless ;
- création de `src/bank_marketing/modeling.py` ;
- création de `notebooks/databricks/04_modeling_baselines.py` ;
- ajout de `tests/test_modeling.py` ;
- exécution du notebook 04 dans Databricks ;
- création de l'expérience MLflow
  `/Users/abdourahman03@gmail.com/bank_marketing_baselines`.

#### Résultats et preuves

- table Silver créée : `workspace.default.bank_marketing_silver` ;
- lignes Silver : 41 176 ;
- cible Silver : 36 537 zéros et 4 639 uns ;
- splits : 24 705 train, 8 235 validation et 8 236 test ;
- `days_since_previous_contact=999` : 0 ligne ;
- `previously_contacted` invalide : 0 ligne ;
- tests locaux : 16 réussis, 1 ignoré parce que scikit-learn n'est pas installé
  localement ;
- notebook 04 terminé avec tous les cells en succès ;
- 5 runs MLflow terminés : `dummy_prior`, `logistic_regression`,
  `logistic_regression_balanced`, `decision_tree_balanced` et
  `random_forest_balanced`.

#### Premiers résultats de validation

| Modèle | PR-AUC validation | ROC-AUC validation | F1 yes | Rappel yes | Lift top 10 % |
|---|---:|---:|---:|---:|---:|
| `random_forest_balanced` | 0.1180 | 0.5432 | 0.1572 | 0.2160 | 0.9205 |
| `dummy_prior` | 0.1107 | 0.5000 | 0.0000 | 0.0000 | 0.2849 |
| `logistic_regression_balanced` | 0.1041 | 0.4770 | 0.0663 | 0.0603 | 0.6246 |
| `decision_tree_balanced` | 0.1030 | 0.4286 | 0.0971 | 0.1886 | 0.6465 |
| `logistic_regression` | 0.0974 | 0.4766 | 0.0000 | 0.0000 | 0.4712 |

#### Décisions prises et raisons

- Conserver `unknown` comme catégorie pour cette première baseline.
  L'imputation sera comparée seulement après observation des résultats de
  validation.
- Ne pas évaluer le test final dans le notebook 04. Le test reste réservé à la
  dernière évaluation.
- Utiliser PR-AUC, rappel de `yes` et lift comme signaux principaux, car
  l'accuracy seule masque le déséquilibre de classe.

#### Problèmes rencontrés

- Le Databricks CLI ne peut pas lancer ce notebook en Jobs serverless dans ce
  workspace. L'exécution a donc été faite dans l'interface Databricks, puis
  vérifiée avec le CLI et MLflow.
- Les premiers résultats sont faibles sur validation chronologique. Ce n'est pas
  un échec : cela confirme que le protocole est difficile et qu'il faut
  optimiser prudemment.

#### Tâches restantes

- comparer le traitement de `unknown` ;
- ajuster les hyperparamètres et le seuil sur validation ;
- analyser les erreurs et les sous-groupes ;
- figer un modèle avant de consulter le test final.

#### Prochaine action exacte

Créer `05_tuning_mlflow.py` pour comparer quelques configurations contrôlées :
traitement de `unknown`, poids de classes, hyperparamètres raisonnables et seuil
métier sur validation.

### Séance du 3 août 2026 — Préparation du tuning MLflow

#### Objectif

Implémenter le notebook `05_tuning_mlflow.py` pour améliorer les baselines sans
utiliser le jeu de test final.

#### Actions effectuées

- ajout de configurations d'optimisation contrôlées dans
  `src/bank_marketing/modeling.py` ;
- ajout de deux stratégies pour `unknown` : conservation comme catégorie et
  conversion en valeur manquante avant imputation ;
- ajout d'une fonction de seuil métier basée sur les 10 % meilleurs scores de
  validation ;
- création du notebook Databricks `05_tuning_mlflow.py` ;
- ajout de tests unitaires pour la transformation de `unknown`, le seuil métier
  et l'unicité des configurations.

#### Résultats et preuves

- le notebook 05 charge Silver, valide les volumes attendus et conserve le test
  hors des métriques ;
- les configurations comparent régression logistique, arbre de décision et forêt
  aléatoire avec quelques hyperparamètres raisonnables ;
- le Git Folder Databricks est synchronisé sur le commit
  `47adc11a6fe8b379ce40bb5eeef004ecadceb4fa` ;
- le notebook 05 a été exécuté avec succès dans Databricks, run Jobs
  `625039448677736` ;
- expérience MLflow :
  `/Users/abdourahman03@gmail.com/bank_marketing_tuning`,
  ID `3057066165070548` ;
- candidat retenu sur validation :
  `random_forest_depth_12_leaf_25_n150_unknown_category` ;
- stratégie `unknown` retenue : conserver `unknown` comme catégorie explicite ;
- seuil métier fixé sur validation : `0.525244` ;
- métriques validation du candidat : PR-AUC `0.116787`, ROC-AUC `0.542584`,
  rappel `yes` `0.205`, F1 `yes` `0.152`, lift top 10 % `0.899` ;
- validation locale : `18 passed, 3 skipped`.

#### Décisions prises et raisons

- Ne pas lancer une recherche exhaustive : le dataset est petit, mais le projet
  doit rester explicable et défendable.
- Classer les candidats avec lift top 10 %, PR-AUC validation, rappel `yes`,
  puis F1 `yes`.
- Fixer le seuil métier sur validation avec un budget de 10 % d'appels.

#### Problèmes rencontrés

- Le Git Folder Databricks contenait des copies locales importées manuellement.
  La synchronisation a nécessité un discard forcé côté Git Folder pour revenir
  à GitHub comme source de vérité.
- La première exécution Jobs a échoué parce que MLflow cherchait à lire
  `spark.mlflow.modelRegistryUri`, indisponible avec Spark Connect serverless.
  Le notebook fixe maintenant explicitement `mlflow.set_tracking_uri("databricks")`
  et `mlflow.set_registry_uri("databricks-uc")`.
- Le lift top 10 % du meilleur candidat reste inférieur à 1. Ce résultat doit
  être présenté comme une limite importante du protocole chronologique.

#### Tâches restantes

- préparer `06_final_evaluation.py`.
- décider avant le test si le modèle sera réentraîné sur train + validation ou
  conservé tel qu'ajusté sur train.

#### Prochaine action exacte

Créer `06_final_evaluation.py` pour reconstruire le candidat retenu, appliquer
le seuil `0.525244` et évaluer une seule fois le jeu de test chronologique.

### Séance du 3 août 2026 — Évaluation finale sur test

#### Objectif

Évaluer une seule fois le modèle final figé sur le split chronologique `test`,
sans modifier le modèle après consultation des résultats.

#### Actions effectuées

- ajout des constantes finales dans `src/bank_marketing/modeling.py` ;
- ajout du notebook Databricks `06_final_evaluation.py` ;
- ajout de tests unitaires pour vérifier le candidat final, le seuil et la
  stratégie de réentraînement ;
- exécution locale des tests automatisés ;
- synchronisation du Git Folder Databricks sur `main` ;
- exécution du notebook 06 dans Databricks Jobs serverless.

#### Résultats et preuves

- commit exécuté dans Databricks : `46fa45ea77db2f55abc992fb31118430549f2c0c` ;
- run Jobs Databricks : `38771101216806` ;
- expérience MLflow :
  `/Users/abdourahman03@gmail.com/bank_marketing_final_evaluation`,
  ID `1171963300815498` ;
- run MLflow final : `0de8816ed1864ce982ee7f911b500b9b` ;
- modèle évalué :
  `random_forest_depth_12_leaf_25_n150_unknown_category` ;
- stratégie de réentraînement : `train_only` ;
- seuil appliqué : `0.525244344106127` ;
- taille du test : 8 236 lignes, dont 2 539 positives ;
- matrice de confusion test : TN `5219`, FP `478`, FN `2215`, TP `324` ;
- métriques test : accuracy `0.6730`, balanced accuracy `0.5219`,
  PR-AUC `0.3491`, ROC-AUC `0.5578`, précision `yes` `0.4040`,
  rappel `yes` `0.1276`, F1 `yes` `0.1940` ;
- métriques métier test : top 10 % = 824 clients, précision `0.4053`,
  rappel `0.1315`, lift `1.3148` ;
- validation locale : `18 passed, 4 skipped`.

#### Décisions prises et raisons

- Ne pas réentraîner sur train + validation avant le test. Le seuil
  `0.525244344106127` a été calibré sur le modèle entraîné uniquement sur
  `train`. Conserver ce modèle évite de changer la distribution des scores juste
  avant le test.
- Présenter le résultat sans exagération : le lift top 10 % est supérieur à 1
  sur test, mais le rappel reste faible. Le modèle trouve une partie des clients
  intéressants, pas une solution complète de ciblage.

#### Problèmes rencontrés

- Aucun blocage d'exécution. Le notebook 06 a réussi en Jobs serverless.

#### Tâches restantes

- analyser les faux positifs et faux négatifs ;
- interpréter les variables importantes du modèle ;
- examiner les performances par sous-groupes ;
- formuler les limites pour la présentation.

#### Prochaine action exacte

Ajouter une analyse d'erreurs et d'interprétation : faux positifs, faux
négatifs, importance des variables et limites métier.

---

## 4. Registre des décisions

### DEC-001 — Choisir une classification supervisée

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** prédire la cible binaire `y`.
- **Raison :** les résultats historiques sont connus et le besoin est de prédire une catégorie.
- **Alternatives rejetées :** régression, car la cible n'est pas continue ; clustering, car le besoin n'est pas seulement de segmenter sans cible.
- **Conséquence :** métriques et modèles de classification.

### DEC-002 — Utiliser UCI Bank Marketing

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** utiliser le dataset officiel UCI.
- **Raison :** gratuit, documenté, associé à un besoin d'affaires, licence CC BY 4.0, taille suffisante et difficulté raisonnable.
- **Conséquence :** citation et attribution obligatoires dans le README et la présentation.

### DEC-003 — Utiliser `bank-additional-full.csv`

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** choisir la variante de 41 188 lignes et 20 prédicteurs.
- **Raison :** elle comprend le contexte socio-économique et est ordonnée par date ; elle offre une étude plus riche que la version réduite.
- **Alternative :** `bank-additional.csv` de 4 119 lignes, conservée seulement pour des tests rapides éventuels.

### DEC-004 — Exclure `duration` du modèle final

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** ne pas utiliser `duration` dans le scénario déployable.
- **Raison :** cette information est connue seulement après l'appel ; l'utiliser pour décider qui appeler constitue une fuite.
- **Conséquence :** performance potentiellement plus faible, mais évaluation réaliste.

### DEC-005 — Conserver `duration` dans l'EDA

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** analyser la variable et montrer son effet, sans l'inclure dans le modèle final.
- **Raison :** c'est un excellent exemple pédagogique de différence entre corrélation, prédiction hors contexte et disponibilité opérationnelle.

### DEC-006 — Utiliser un test chronologique

- **Date :** 30 juin 2026
- **État :** À VALIDER PAR L'IMPLÉMENTATION
- **Décision proposée :** derniers 20 % comme test futur.
- **Raison :** le dataset est ordonné par date et le modèle serait appliqué à de futures campagnes.
- **Risque :** les dates exactes ne sont pas fournies ligne par ligne ; il faudra documenter que l'ordre officiel sert de proxy temporel.

### DEC-007 — Ne pas utiliser l'accuracy seule

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** F1 positif, précision, rappel, PR-AUC, ROC-AUC, balanced accuracy et lift.
- **Raison :** environ 88,7 % des observations appartiennent à `no`. Un modèle inutile pourrait avoir une accuracy élevée.

### DEC-008 — Utiliser une pipeline scikit-learn

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** combiner prétraitement et modèle dans `Pipeline`/`ColumnTransformer`.
- **Raison :** prévenir les fuites, garantir les mêmes transformations et simplifier la prédiction.

### DEC-009 — One-hot encoder les prédicteurs nominaux

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE COMME CHOIX PAR DÉFAUT
- **Décision :** utiliser `OneHotEncoder(handle_unknown="ignore")`.
- **Raison :** `LabelEncoder` imposerait un ordre numérique artificiel aux métiers, mois, types de contacts, etc.
- **Exception possible :** un encodage ordinal de l'éducation seulement s'il est clairement justifié et comparé.

### DEC-010 — Comparer au moins quatre niveaux de modèle

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** Dummy, régression logistique, arbre de décision et forêt aléatoire.
- **Raison :** référence naïve, modèle linéaire, modèle interprétable non linéaire et ensemble réduisant la variance.
- **Option :** k-NN seulement si son coût apporte une comparaison utile.

### DEC-011 — Utiliser MLflow et DVC

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** MLflow pour les expériences, DVC pour le dataset.
- **Raison :** ces outils sont enseignés dans le cours et répondent à l'accent mis sur l'infrastructure et la reproductibilité.

### DEC-012 — Séparer notebooks et code réutilisable

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** EDA dans notebooks, fonctions et entraînement dans `src/`.
- **Raison :** les notebooks expliquent ; les modules rendent l'exécution répétable et testable.

### DEC-013 — Prioriser un produit minimum complet

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** Streamlit, FastAPI et modèles supplémentaires sont des bonus.
- **Raison :** le projet est réalisé par une seule personne. Un pipeline complet vaut davantage qu'une démonstration spectaculaire mais fragile.

### DEC-014 — Ne pas supprimer automatiquement les doublons ou outliers

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** inspecter leur nature avant traitement.
- **Raison :** des appels ou clients distincts peuvent partager les mêmes valeurs ; une valeur extrême peut être valide.

### DEC-015 — Ne pas publier les changements sans étape explicite

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** travailler et vérifier localement avant commit/push.
- **Raison :** éviter de publier des fichiers incomplets ou des données qui ne devraient pas être suivies par Git.

### DEC-016 — Utiliser Databricks Free Edition comme plateforme principale

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** exécuter ingestion, EDA, modèles et MLflow dans Databricks.
- **Raison :** objectif d'apprentissage de l'étudiant et bonne adéquation avec l'infrastructure demandée dans le cours.

### DEC-017 — Adopter une architecture hybride Spark et scikit-learn

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** Spark/Delta pour les données, pandas/scikit-learn pour le ML.
- **Raison :** profiter de Databricks tout en restant cohérent avec le cours et la taille modeste du dataset.

### DEC-018 — Stocker le CSV dans un Unity Catalog Volume

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** ne pas placer le CSV dans Git ou dans le Git Folder.
- **Raison :** séparation du code et des données, gouvernance Unity Catalog et limites des Git Folders.

### DEC-019 — Utiliser Delta Bronze et Silver

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** Bronze pour la copie contrôlée, Silver pour les transformations déterministes.
- **Raison :** démontrer Delta Lake avec une architecture proportionnée au projet.

### DEC-020 — Préserver explicitement l'ordre source

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** créer `_source_row_number` avant la conversion Spark.
- **Raison :** une table Spark n'a pas d'ordre implicite, alors que la validation finale dépend de l'ordre chronologique publié par UCI.

### DEC-021 — Utiliser MLflow géré et activer autolog explicitement

- **Date :** 30 juin 2026
- **État :** ACCEPTÉE
- **Décision :** ne pas démarrer de serveur MLflow local.
- **Raison :** Databricks fournit MLflow ; le compute serverless demande un appel explicite à `mlflow.autolog()`.

### DEC-022 — Dédupliquer seulement dans Silver

- **Date :** 1er juillet 2026
- **État :** ACCEPTÉE
- **Décision :** conserver Bronze intact et retirer les 12 répétitions exactes
  dans Silver en gardant la première occurrence chronologique.
- **Raison :** aucune paire ne traverse deux splits, mais conserver les deux
  occurrences surpondérerait inutilement des lignes identiques.

### DEC-023 — Conserver `unknown` pour la première baseline

- **Date :** 1er juillet 2026
- **État :** PROVISOIRE
- **Décision :** traiter `unknown` comme une catégorie explicite dans le premier
  modèle.
- **Raison :** ce n'est pas un `NaN` brut et l'imputation ne doit pas être
  choisie sans comparaison sur validation.

### DEC-024 — Transformer la sentinelle `pdays=999`

- **Date :** 1er juillet 2026
- **État :** ACCEPTÉE
- **Décision :** créer `previously_contacted` et
  `days_since_previous_contact`, avec zéro jour lorsque le client n'a jamais été
  contacté.
- **Raison :** 999 est un code métier, pas une durée réelle ; l'indicateur
  distingue l'absence de contact d'un véritable délai de zéro jour.

### DEC-025 — Optimiser avec une grille courte avant le test

- **Date :** 3 août 2026
- **État :** ACCEPTÉE POUR L'IMPLÉMENTATION
- **Décision :** comparer un nombre limité de configurations dans
  `05_tuning_mlflow.py` : traitement de `unknown`, poids de classes,
  régularisation/profondeur minimale et seuil métier sur validation.
- **Raison :** le projet doit rester reproductible, explicable et aligné avec le
  cours. Une recherche exhaustive augmenterait le coût et le risque de choisir
  un modèle opportuniste.
- **Conséquence :** le modèle final sera choisi sur validation en priorisant le
  lift top 10 %, avant toute évaluation du test chronologique.

### DEC-026 — Conserver le modèle entraîné sur train pour le test

- **Date :** 3 août 2026
- **État :** ACCEPTÉE
- **Décision :** ne pas réentraîner le candidat final sur train + validation
  avant l'évaluation du test.
- **Raison :** le seuil métier a été fixé sur les scores de validation du modèle
  entraîné uniquement sur `train`. Réentraîner le modèle juste avant le test
  aurait changé la distribution des scores sans recalibrer le seuil.
- **Conséquence :** l'évaluation test mesure exactement le candidat figé à la
  fin du notebook 05.

---

## 5. Décisions encore ouvertes

### OUV-001 — Traitement de `unknown`

- **État :** RÉSOLUE par validation dans le notebook 05
- **Options :** conserver comme catégorie ; convertir en valeur manquante et imputer ; comparer les deux.
- **Décision :** conserver `unknown` comme catégorie explicite pour le candidat retenu.
- **Preuve :** le meilleur candidat selon la règle de sélection est
  `random_forest_depth_12_leaf_25_n150_unknown_category`.

### OUV-002 — Traitement des 12 doublons

- **État :** RÉSOLUE par DEC-022
- **Décision :** retirer dans Silver les 12 répétitions en conservant la
  première occurrence.
- **Preuve :** 7 répétitions sont dans train, 3 dans validation et 2 dans test ;
  aucune paire ne traverse deux ensembles.

### OUV-003 — Seuil métier

- **État :** RÉSOLUE par validation dans le notebook 05
- **Options :** 0,5 ; maximiser F1 ; atteindre un rappel cible ; sélectionner les 10 % meilleurs scores.
- **Décision :** utiliser le seuil `0.525244`, dérivé du budget de 10 % sur validation.
- **Limite :** le lift top 10 % reste inférieur à 1, donc ce seuil doit être
  validé prudemment sur le test final.

### OUV-004 — Réentraînement final

- **État :** RÉSOLUE par DEC-026
- **Décision :** conserver le modèle ajusté uniquement sur train pour
  l'évaluation finale.
- **Preuve :** notebook 06 exécuté avec `FINAL_REFIT_STRATEGY="train_only"`.

### OUV-005 — DVC remote

- **État :** À FAIRE
- **Options :** stockage local, Google Drive ou autre espace distant.
- **Contrainte :** ne pas ajouter un remote contenant des secrets dans Git.

### OUV-006 — Interface de démonstration

- **État :** OPTIONNEL
- **Options :** ligne de commande, notebook, Streamlit, FastAPI.
- **Choix provisoire :** ligne de commande stable ; interface seulement si le cœur est terminé.

---

## 6. Backlog détaillé

### Prochaine étape immédiate

1. `TERMINÉ` Publier les fichiers Databricks préparés sur GitHub dans une branche de fondation Databricks.
2. `TERMINÉ` Relire et fusionner la pull request #1 dans `main`.
3. `TERMINÉ` Tirer `main` dans le Databricks Git Folder.
4. `TERMINÉ` Exécuter `00_configuration.py` sur compute serverless.
5. `TERMINÉ` Téléverser `data/raw/bank-additional-full.csv` dans le Volume affiché.
6. `TERMINÉ` Exécuter et valider `01_ingestion_bronze.py`.
7. `TERMINÉ` Exécuter `02_eda.py` et conserver les premières observations.
8. `TERMINÉ` Préparer et exécuter `03_preprocessing_silver.py`.
9. `À FAIRE` Initialiser DVC côté local pour la provenance du fichier.
10. `EN COURS` Valider les bibliothèques disponibles dans le compute serverless.

### Acquisition et validation du schéma

- `À FAIRE` Créer `src/bank_marketing/data.py`.
- `TERMINÉ` Définir la liste exacte des 21 colonnes attendues.
- `TERMINÉ` Vérifier séparateur `;`, encodage et types.
- `TERMINÉ` Ajouter une erreur claire si la cible manque.
- `TERMINÉ` Ajouter des tests du contrat de données.
- `TERMINÉ` Documenter la provenance dans le README et le manifeste.

### EDA

- `TERMINÉ` Vue globale et statistiques.
- `TERMINÉ` Audit des valeurs inconnues.
- `TERMINÉ` Audit des doublons.
- `TERMINÉ` Distribution cible.
- `TERMINÉ` Distributions numériques.
- `TERMINÉ` Box plots et valeurs extrêmes.
- `TERMINÉ` Variables catégorielles et taux de conversion par groupe.
- `TERMINÉ` Corrélations.
- `TERMINÉ` Première mesure de dérive entre les segments temporels.
- `TERMINÉ` Illustration de la fuite `duration`.
- `À FAIRE` Tests statistiques ciblés et tailles d'effet.
- `À FAIRE` Export des graphiques.
- `À FAIRE` Conclusions écrites après chaque section.

### Prétraitement

- `TERMINÉ` Séparation chronologique.
- `TERMINÉ` Encodage de la cible.
- `TERMINÉ` Exclusion de `duration` des variables déployables.
- `TERMINÉ` Traitement de `pdays=999`.
- `EN COURS` Conserver `unknown` pour la baseline, puis comparer sur validation.
- `TERMINÉ` Encodage one-hot.
- `TERMINÉ` Standardisation des numériques.
- `TERMINÉ` Pipeline complète.
- `TERMINÉ` Tests de dimensions, colonnes et frontières chronologiques.
- `TERMINÉ` Vérification statique de l'absence de `duration` dans les variables déployables.

### Modèles et expériences

- `TERMINÉ` DummyClassifier.
- `TERMINÉ` Régression logistique.
- `TERMINÉ` Arbre de décision.
- `TERMINÉ` Forêt aléatoire.
- `OPTIONNEL` k-NN.
- `TERMINÉ` MLflow Databricks avec `mlflow.autolog()` explicite.
- `TERMINÉ` Fonction commune d'évaluation.
- `TERMINÉ` Tableau comparatif.
- `TERMINÉ` Recherche d'hyperparamètres.
- `TERMINÉ` Ajustement du seuil.
- `TERMINÉ` Sélection finale avant test.

### Évaluation et interprétation

- `TERMINÉ` Matrices de confusion.
- `TERMINÉ` Rapport de classification.
- `TERMINÉ` ROC-AUC et courbe ROC.
- `TERMINÉ` PR-AUC et courbe précision-rappel.
- `TERMINÉ` Lift et métriques top 10 %.
- `À FAIRE` Analyse des erreurs.
- `À FAIRE` Importances et coefficients.
- `À FAIRE` Analyse des sous-groupes.
- `À FAIRE` Limites, biais et conditions d'utilisation.

### Livraison

- `À FAIRE` Sauvegarde de la pipeline.
- `À FAIRE` Script de prédiction.
- `À FAIRE` Tests automatisés.
- `À FAIRE` GitHub Action.
- `À FAIRE` README final.
- `À FAIRE` PowerPoint.
- `À FAIRE` Démonstration.
- `À FAIRE` Répétition de 15 minutes.
- `À FAIRE` Vérification finale des citations.

---

## 7. Blocages actuels

Aucun blocage actif. Le notebook 04 a dû être exécuté dans l'interface
Databricks, car les Jobs serverless ne sont pas activés dans ce workspace.

Éléments à surveiller :

- l'étudiant réalise le projet seul alors que le document original prévoit une équipe ;
- aucun barème détaillé n'est disponible ;
- la méthode exacte de remise et le format final du PowerPoint peuvent encore être précisés par le professeur ;
- le choix du stockage distant DVC n'est pas encore défini.

Ces éléments n'empêchent pas de commencer l'implémentation.

---

## 8. Contrôle de qualité avant chaque jalon

### Avant de terminer l'EDA

- Tous les constats importants sont accompagnés d'une preuve ou d'un graphique.
- Les valeurs `unknown`, doublons et sentinelles sont quantifiés.
- La fuite `duration` est clairement expliquée.
- Les observations ne sont pas présentées comme des causalités.

### Avant de terminer la modélisation

- La baseline naïve existe.
- Les transformations sont dans une pipeline.
- Le test final n'a pas servi au réglage.
- Les métriques de la classe positive sont enregistrées.
- Les expériences sont comparables et traçables.

### Avant de consulter le test final

- Le modèle final est choisi.
- Les hyperparamètres sont figés.
- Le seuil est fixé.
- La fonction d'évaluation est figée.
- La décision de réentraînement est consignée.

### Avant la remise

- Le projet fonctionne depuis un environnement propre.
- Les données brutes ne sont pas suivies directement par Git.
- Aucun secret ou chemin local personnel n'est publié.
- Les notebooks s'exécutent dans l'ordre.
- Les résultats du PowerPoint correspondent aux artefacts du dépôt.
- Les sources et la licence sont citées.
- La présentation respecte 15 minutes.

---

## 9. Format des prochaines entrées du journal

Chaque nouvelle séance utilisera ce modèle :

```markdown
### Séance du AAAA-MM-JJ — Titre

#### Objectif

#### Actions effectuées

#### Résultats et preuves

#### Décisions prises et raisons

#### Problèmes rencontrés

#### Tâches restantes

#### Prochaine action exacte
```

---

## 10. Prochaine action exacte

Ajouter l'analyse d'erreurs et d'interprétation : faux positifs, faux négatifs,
importance des variables, sous-groupes et limites métier.
