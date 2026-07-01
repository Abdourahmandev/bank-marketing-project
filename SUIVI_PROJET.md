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

## 2. État global au 1er juillet 2026

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
| environnement Python | EN COURS | compute serverless retenu ; bibliothèques à valider dans le workspace |
| acquisition avec DVC | À FAIRE | fichier officiel pas encore ajouté au dépôt de projet |
| EDA | EN COURS | notebook initial exécuté ; analyses avancées et export des figures restent à faire |
| prétraitement | EN COURS | transformations Silver et tests préparés ; exécution Databricks requise |
| modélisation | À FAIRE | aucun modèle entraîné dans le dépôt |
| MLflow | À FAIRE | MLflow Databricks géré ; autologging serverless à activer explicitement |
| évaluation finale | À FAIRE | aucun résultat ne doit être annoncé avant exécution |
| présentation | À FAIRE | plan temporel défini, PowerPoint non créé |

Estimation prudente de l'avancement total : **environ 30 %**. L'architecture,
l'ingestion et l'EDA initiale fonctionnent ; la table Silver doit maintenant être
exécutée avant de commencer les modèles de référence.

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

---

## 5. Décisions encore ouvertes

### OUV-001 — Traitement de `unknown`

- **État :** À FAIRE
- **Options :** conserver comme catégorie ; convertir en valeur manquante et imputer ; comparer les deux.
- **Choix provisoire :** conserver comme catégorie dans la première baseline.
- **Pourquoi le choix reste ouvert :** la documentation officielle autorise les deux interprétations. La validation et la signification métier doivent guider la décision.

### OUV-002 — Traitement des 12 doublons

- **État :** RÉSOLUE par DEC-022
- **Décision :** retirer dans Silver les 12 répétitions en conservant la
  première occurrence.
- **Preuve :** 7 répétitions sont dans train, 3 dans validation et 2 dans test ;
  aucune paire ne traverse deux ensembles.

### OUV-003 — Seuil métier

- **État :** À FAIRE
- **Options :** 0,5 ; maximiser F1 ; atteindre un rappel cible ; sélectionner les 10 % meilleurs scores.
- **Choix provisoire :** présenter les résultats pour un budget de 10 % d'appels et un seuil optimisé sur validation.

### OUV-004 — Réentraînement final

- **État :** À FAIRE
- **Question :** après sélection, réentraîner sur train + validation ou conserver le modèle ajusté uniquement sur train ?
- **Condition :** décider avant de consulter les métriques du test final.

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

1. `TERMINÉ` Publier les fichiers Databricks préparés sur GitHub dans la branche `codex/databricks-foundation`.
2. `TERMINÉ` Relire et fusionner la pull request #1 dans `main`.
3. `TERMINÉ` Tirer `main` dans le Databricks Git Folder.
4. `TERMINÉ` Exécuter `00_configuration.py` sur compute serverless.
5. `TERMINÉ` Téléverser `data/raw/bank-additional-full.csv` dans le Volume affiché.
6. `TERMINÉ` Exécuter et valider `01_ingestion_bronze.py`.
7. `TERMINÉ` Exécuter `02_eda.py` et conserver les premières observations.
8. `EN COURS` Préparer et exécuter `03_preprocessing_silver.py`.
9. `À FAIRE` Initialiser DVC côté local pour la provenance du fichier.
10. `À FAIRE` Valider les bibliothèques disponibles dans le compute serverless.

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
- `À FAIRE` Encodage one-hot.
- `À FAIRE` Standardisation des numériques.
- `À FAIRE` Pipeline complète.
- `TERMINÉ` Tests de dimensions, colonnes et frontières chronologiques.
- `TERMINÉ` Vérification statique de l'absence de `duration` dans les variables déployables.

### Modèles et expériences

- `À FAIRE` DummyClassifier.
- `À FAIRE` Régression logistique.
- `À FAIRE` Arbre de décision.
- `À FAIRE` Forêt aléatoire.
- `OPTIONNEL` k-NN.
- `À FAIRE` MLflow Databricks avec `mlflow.autolog()` explicite.
- `À FAIRE` Fonction commune d'évaluation.
- `À FAIRE` Tableau comparatif.
- `À FAIRE` Recherche d'hyperparamètres.
- `À FAIRE` Ajustement du seuil.
- `À FAIRE` Sélection finale avant test.

### Évaluation et interprétation

- `À FAIRE` Matrices de confusion.
- `À FAIRE` Rapport de classification.
- `À FAIRE` ROC-AUC et courbe ROC.
- `À FAIRE` PR-AUC et courbe précision-rappel.
- `À FAIRE` Lift et métriques top 10 %.
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

Aucun blocage actif. Une exécution manuelle du nouveau notebook Silver demeure
nécessaire dans Databricks après sa publication et sa synchronisation.

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

Publier la branche `codex/silver-preprocessing`, la synchroniser dans Databricks
et exécuter `03_preprocessing_silver.py`. Vérifier les comptes affichés avant de
commencer `04_modeling_baselines.py`. Le test final ne doit pas être utilisé pour
choisir une transformation, un modèle ou un seuil.
