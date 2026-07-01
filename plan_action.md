# Plan d'action — Bank Marketing Project

## 1. Informations générales

- **Étudiant :** Abdourahmane
- **Cours :** Techniques d'apprentissage automatique — 420-C74-BB
- **Projet :** prédiction du succès d'une campagne de télémarketing bancaire
- **Type d'apprentissage :** apprentissage supervisé, classification binaire
- **Plateforme d'exécution :** Databricks Free Edition, compute serverless
- **Date de création du plan :** 30 juin 2026
- **Présentation prévue :** 11 août 2026
- **Remise prévue :** 15 août 2026
- **Dépôt :** <https://github.com/Abdourahmandev/bank-marketing-project>
- **État initial :** dépôt vide, structure et planification en cours

Ce document décrit le projet à réaliser, l'ordre des travaux, les livrables attendus, les critères de réussite et les raisons qui motivent les choix techniques. Il doit servir de référence pendant toute la réalisation.

Le suivi quotidien, les décisions réellement appliquées et les écarts par rapport à ce plan sont consignés dans [`SUIVI_PROJET.md`](SUIVI_PROJET.md).

---

## 2. Résumé du projet

### 2.1 Besoin d'affaires

Une banque effectue des campagnes téléphoniques pour proposer des dépôts à terme. Appeler tous les clients est coûteux et peut augmenter l'insatisfaction. Le projet doit construire un système capable, **avant l'appel**, d'estimer la probabilité qu'un client souscrive au produit.

Le résultat attendu n'est donc pas simplement une classe `yes` ou `no`. Le modèle devra produire une probabilité permettant au responsable marketing de prioriser les clients selon les ressources disponibles.

### 2.2 Question analytique

> À partir des informations disponibles avant un appel, quels clients devraient être contactés en priorité parce qu'ils ont la plus forte probabilité de souscrire à un dépôt à terme ?

### 2.3 Partie prenante principale

Le client fictif est le responsable de la campagne marketing de la banque. Il souhaite :

- réduire les appels à faible potentiel ;
- augmenter le taux de conversion ;
- mieux utiliser le temps des agents ;
- limiter la sollicitation inutile des clients ;
- comprendre les facteurs associés aux souscriptions.

### 2.4 Type de problème

- La cible `y` est connue dans les données historiques.
- La cible possède deux catégories : `yes` et `no`.
- Le problème est donc une **classification binaire supervisée**.
- La classe positive sera `yes`, car elle représente l'événement d'affaires recherché.

---

## 3. Jeu de données retenu

### 3.1 Source

- **Nom :** Bank Marketing
- **Variante :** `bank-additional-full.csv`
- **Source officielle :** <https://archive.ics.uci.edu/dataset/222/bank>
- **Téléchargement officiel :** <https://archive.ics.uci.edu/static/public/222/bank+marketing.zip>
- **Auteurs :** Sérgio Moro, Paulo Cortez et Paulo Rita
- **Licence :** Creative Commons Attribution 4.0 International, CC BY 4.0
- **Citation :** Moro, S., Rita, P., & Cortez, P. (2014). *Bank Marketing*. UCI Machine Learning Repository. <https://doi.org/10.24432/C5K306>

### 3.2 Caractéristiques déjà vérifiées

- 41 188 observations ;
- 20 prédicteurs et une cible ;
- mélange de variables numériques et catégorielles ;
- données ordonnées chronologiquement de mai 2008 à novembre 2010 ;
- cible déséquilibrée : environ 11,27 % de `yes` ;
- valeurs inconnues représentées par la chaîne `unknown` ;
- 12 lignes exactement dupliquées à examiner ;
- aucune valeur `NaN` brute dans le fichier ;
- une variable problématique, `duration`, qui n'est disponible qu'après l'appel.

### 3.3 Pourquoi ce dataset est approprié

Ce dataset permet de démontrer une grande partie des notions du cours dans un seul projet :

- analyse exploratoire ;
- variables numériques et catégorielles ;
- traitement de valeurs inconnues ;
- encodage ;
- normalisation ;
- classification ;
- déséquilibre de classes ;
- comparaison de modèles ;
- compromis biais-variance ;
- prévention des fuites de données ;
- validation ;
- métriques de classification ;
- interprétation ;
- suivi des expériences ;
- reproductibilité avec Git, DVC et MLflow.

### 3.4 Risque de fuite avec `duration`

`duration` correspond à la durée du dernier appel. Elle est fortement liée à la cible, mais elle ne peut pas être connue avant l'appel. Elle sera donc :

1. étudiée pendant l'EDA pour démontrer le risque de fuite ;
2. exclue du pipeline final ;
3. éventuellement utilisée dans une expérience séparée appelée explicitement « benchmark non déployable » ;
4. jamais utilisée pour choisir les clients à appeler.

Cette décision garantit que le modèle correspond au besoin réel et évite de présenter une performance artificiellement élevée.

---

## 4. Résultats attendus et définition de « terminé »

Le projet sera considéré terminé lorsque les éléments suivants seront disponibles et reproductibles :

- un README expliquant le besoin, l'installation et l'exécution ;
- une copie brute du dataset suivie par DVC ;
- une fiche descriptive du dataset et de sa licence ;
- un notebook d'EDA exécuté et lisible ;
- un notebook ou script de prétraitement ;
- une pipeline scikit-learn sans fuite de données ;
- un modèle de référence naïf ;
- au moins trois modèles de classification comparés ;
- une procédure de validation et d'optimisation documentée ;
- un jeu de test final non utilisé pendant le développement ;
- des métriques adaptées au déséquilibre de la cible ;
- une analyse des erreurs ;
- une interprétation du modèle retenu ;
- les expériences enregistrées dans MLflow ;
- le dataset versionné avec DVC ;
- une pipeline finale sérialisée ;
- un script de prédiction sur de nouvelles observations ;
- des tests minimaux automatisés ;
- une présentation PowerPoint de 15 minutes ;
- une démonstration fonctionnelle ;
- une liste honnête des difficultés et limites.

Aucun résultat de performance ne sera inventé. Toutes les valeurs présentées devront provenir d'une exécution reproductible.

---

## 5. Périmètre du projet

### 5.1 Périmètre principal obligatoire

- Classification binaire de `y`.
- Données disponibles avant l'appel seulement.
- EDA complète, mais ciblée sur le besoin.
- Prétraitement reproductible avec `Pipeline` et `ColumnTransformer`.
- Comparaison d'un modèle naïf, d'une régression logistique, d'un arbre de décision et d'une forêt aléatoire.
- Évaluation sur un test chronologique final.
- MLflow, Git et DVC.
- Script de prédiction ou petite démonstration en ligne de commande.
- Présentation et code explicables par l'étudiant.

### 5.2 Éléments secondaires si le temps le permet

- k-NN comme modèle supplémentaire du cours ;
- comparaison « avec `duration` / sans `duration` » uniquement pour illustrer la fuite ;
- ajustement du seuil selon un budget d'appels ;
- analyse de performance par sous-groupes ;
- petite interface Streamlit ou API FastAPI ;
- rapport automatisé ydata-profiling conservé comme artefact.

### 5.3 Hors périmètre initial

- réseaux de neurones ;
- déploiement sur une infrastructure payante ;
- traitement temps réel ;
- collecte de nouvelles données personnelles ;
- interprétation causale des relations ;
- ajout de PCA, k-means ou Naive Bayes sans justification expérimentale.

Le but est de livrer un projet complet et défendable, pas d'accumuler des technologies.

### 5.4 Architecture Databricks retenue

Le projet utilise une architecture hybride, afin de profiter de Databricks sans
abandonner les outils du cours :

1. **GitHub** demeure la source de vérité du code, des notebooks et de la documentation.
2. **Databricks Git Folder** synchronise le dépôt dans le workspace.
3. Le CSV officiel est vérifié localement, suivi par DVC pour sa provenance, puis
   téléversé dans un **Unity Catalog Volume**.
4. Une table **Delta Bronze** conserve une copie contrôlée des données et l'ordre
   original des lignes.
5. Une table **Delta Silver** contiendra les transformations déterministes et les
   variables préparées.
6. Spark et SQL servent à l'ingestion, aux contrôles et aux tables Delta.
7. Le dataset de 41 188 lignes est converti en pandas pour la modélisation avec
   scikit-learn, conformément au cours.
8. **MLflow Databricks** enregistre les expériences, métriques, figures et modèles.
9. Le modèle final produit des probabilités et peut écrire les résultats dans une
   table Delta de prédictions.

Free Edition étant limitée en compute et en accès Internet sortant, le projet ne
dépendra ni d'un téléchargement Web exécuté depuis un notebook, ni d'un endpoint
temps réel pour sa démonstration principale.

---

## 6. Outils retenus et raisons

| Outil | Utilisation prévue | Justification |
|---|---|---|
| Python | langage principal | langage utilisé dans le cours et écosystème ML mature |
| Databricks Notebooks | exploration, ingestion, modélisation et présentation | environnement principal du projet, synchronisé par Git Folder |
| Databricks Free Edition | exécution serverless | permet d'apprendre la plateforme sans coût, avec un périmètre compatible avec les quotas |
| Apache Spark / SQL | ingestion, contrôles et tables | démontre l'utilisation Databricks sans imposer Spark à la modélisation scikit-learn |
| Unity Catalog Volume | stockage gouverné du CSV brut | remplace les chemins locaux pendant l'exécution Databricks |
| Delta Lake | tables Bronze, Silver et prédictions | apporte schéma, historique et reproductibilité des transformations |
| pandas | chargement, audit et transformation | outil principal du cours pour les données tabulaires |
| NumPy | calcul numérique | base des opérations scientifiques Python |
| matplotlib / seaborn | visualisations | adaptés aux distributions, box plots et matrices de corrélation |
| ydata-profiling | rapport exploratoire secondaire | utile pour détecter rapidement certains problèmes, sans remplacer l'EDA manuelle |
| scikit-learn | prétraitement, modèles, validation et métriques | bibliothèque centrale du cours |
| MLflow Databricks | suivi des paramètres, métriques, figures et modèles | service intégré ; aucun serveur MLflow local à maintenir |
| Git / GitHub | version du code et collaboration | historique, sauvegarde et démonstration de bonnes pratiques |
| DVC | provenance durable du fichier officiel côté local | complète Delta Lake ; le CSV utilisé par Databricks réside dans Unity Catalog |
| joblib | sauvegarde de la pipeline finale | format simple pour les objets scikit-learn |
| pytest | tests minimaux | vérifie automatiquement les fonctions importantes |
| GitHub Actions | intégration continue minimale | exécute les validations de base à chaque changement publié |

Les versions exactes seront verrouillées après la création et la validation de l'environnement, afin de ne pas inscrire des versions arbitraires avant d'avoir testé leur compatibilité.

---

## 7. Arborescence prévue

```text
bank-marketing-project/
├── README.md
├── plan_action.md
├── SUIVI_PROJET.md
├── requirements.txt
├── params.yaml
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── dataset_manifest.json
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
│   └── databricks_setup.md
├── notebooks/
│   └── databricks/
│       ├── 00_configuration.py
│       ├── 01_ingestion_bronze.py
│       ├── 02_eda.py
│       ├── 03_preprocessing_silver.py
│       ├── 04_modeling_baselines.py
│       ├── 05_tuning_mlflow.py
│       ├── 06_final_evaluation.py
│       └── 07_inference_demo.py
├── src/
│   └── bank_marketing/
│       ├── __init__.py
│       ├── data.py
│       ├── features.py
│       ├── train.py
│       ├── evaluate.py
│       └── predict.py
├── models/
├── reports/
│   └── figures/
├── presentation/
└── tests/
```

Les notebooks Databricks au format source `.py` servent à expliquer, explorer et
orchestrer. Le code réutilisable reste dans `src/` pour éviter que toute la
logique soit enfermée dans des notebooks. Les données volumineuses ne sont jamais
placées dans le Git Folder.

---

## 8. Méthodologie de validation

### 8.1 Séparation chronologique

Le fichier complet étant ordonné par date, la séparation principale sera :

- premiers 60 % : entraînement ;
- 20 % suivants : validation ;
- derniers 20 % : test final.

Pourquoi : en production, le modèle est entraîné sur le passé et utilisé sur le futur. Un mélange aléatoire peut transférer de l'information temporelle entre les ensembles et produire une estimation trop optimiste.

Une séparation aléatoire stratifiée 80/20 pourra être exécutée comme analyse de sensibilité, mais elle sera clairement distinguée du protocole principal.

### 8.2 Règles contre la fuite

- `duration` exclue du modèle final ;
- prétraitement ajusté seulement sur les données d'entraînement ;
- validation utilisée pour choisir modèle, hyperparamètres et seuil ;
- test final utilisé une seule fois après les décisions ;
- aucune imputation ou normalisation avant la séparation ;
- aucun suréchantillonnage avant la séparation ;
- toutes les transformations intégrées dans une pipeline.

### 8.3 Métriques

Métriques principales :

- matrice de confusion ;
- précision de la classe `yes` ;
- rappel de la classe `yes` ;
- F1 de la classe `yes` ;
- PR-AUC / Average Precision ;
- ROC-AUC ;
- balanced accuracy.

Métriques d'affaires :

- précision parmi les 10 % de clients ayant les plus hauts scores ;
- rappel parmi ces 10 % ;
- lift par rapport à une sélection aléatoire ;
- nombre estimé d'appels évités pour un niveau de rappel donné.

L'accuracy sera rapportée pour respecter les notions du cours, mais elle ne sera pas utilisée seule, car un modèle prédisant toujours `no` obtiendrait déjà environ 88,7 %.

---

## 9. Modèles prévus

### 9.1 DummyClassifier

Rôle : référence minimale permettant de démontrer qu'une accuracy élevée peut être trompeuse.

### 9.2 Régression logistique

Rôle : modèle linéaire interprétable fournissant naturellement des probabilités.

Points à tester :

- `class_weight=None` et `class_weight="balanced"` ;
- paramètre de régularisation `C` ;
- stabilité des coefficients ;
- temps d'entraînement et de prédiction.

### 9.3 Arbre de décision

Rôle : modèle interprétable capable de représenter des relations non linéaires.

Points à tester :

- `criterion` ;
- `max_depth` ;
- `min_samples_split` ;
- `min_samples_leaf` ;
- poids de classes ;
- écart entre performance d'entraînement et de validation.

### 9.4 Forêt aléatoire

Rôle : méthode d'ensemble du cours pouvant réduire la variance d'un arbre unique.

Points à tester :

- `n_estimators` ;
- `max_depth` ;
- `max_features` ;
- `min_samples_leaf` ;
- `class_weight` ;
- importance des prédicteurs ;
- coût de calcul.

### 9.5 k-NN, optionnel

Rôle : comparaison avec un modèle fondé sur la distance, directement étudié dans le cours.

Limites attendues : coût de prédiction sur 41 188 lignes, sensibilité à l'échelle et haute dimension après one-hot encoding. Il ne sera conservé que si l'expérience apporte une information utile.

---

## 10. Plan de travail détaillé

### Phase 0 — Cadrage et initialisation

- [x] P0.1 Choisir le domaine et le problème.
- [x] P0.2 Choisir le dataset.
- [x] P0.3 Vérifier licence, dimensions et cible.
- [x] P0.4 Créer le dépôt GitHub.
- [x] P0.5 Cloner le dépôt localement.
- [x] P0.6 Créer le plan d'action et le journal de suivi.
- [x] P0.7 Créer l'arborescence initiale.
- [x] P0.8 Connecter GitHub à Databricks avec un Git Folder.
- [x] P0.9 Ajouter le manifeste et la configuration Databricks initiale.
- [ ] P0.10 Configurer DVC.
- [ ] P0.11 Valider les bibliothèques du compute serverless et documenter les dépendances additionnelles.
- [ ] P0.12 Valider MLflow géré avec `mlflow.autolog()`.

**Critère de sortie :** projet clonable, structure compréhensible, environnement reproductible et plan approuvé.

### Phase 1 — Acquisition et gouvernance des données

- [x] P1.1 Télécharger l'archive officielle hors Databricks.
- [x] P1.2 Vérifier le fichier, sa taille et son empreinte SHA-256.
- [x] P1.3 Conserver le CSV brut sans modification dans `data/raw/`.
- [ ] P1.4 Ajouter le CSV à DVC.
- [x] P1.5 Documenter la source, licence, citation et empreinte dans un manifeste.
- [ ] P1.6 Téléverser le CSV dans un Unity Catalog Volume.
- [x] P1.7 Écrire un contrat validant les colonnes, les lignes et la cible.
- [x] P1.8 Préparer le notebook d'ingestion Delta Bronze.
- [ ] P1.9 Exécuter et valider la table Bronze dans Databricks.

**Critère de sortie :** la source exacte du dataset est prouvée, son ordre est
préservé, le chargement échoue clairement si le fichier change et la table Delta
Bronze est visible dans Unity Catalog.

### Phase 2 — Analyse exploratoire

- [ ] P2.1 Examiner dimensions, types et aperçu.
- [ ] P2.2 Rechercher doublons, `NaN`, infinis et valeurs `unknown`.
- [ ] P2.3 Vérifier la distribution de `y`.
- [ ] P2.4 Étudier les variables numériques avec statistiques, histogrammes, KDE et box plots.
- [ ] P2.5 Étudier les variables catégorielles et leur taux de souscription.
- [ ] P2.6 Produire la matrice de corrélation numérique.
- [ ] P2.7 Examiner les variations temporelles.
- [ ] P2.8 Étudier `duration` et expliquer la fuite.
- [ ] P2.9 Tester quelques hypothèses pertinentes.
- [ ] P2.10 Documenter les limites et biais potentiels.
- [ ] P2.11 Exporter les figures finales dans `reports/figures/`.

**Critère de sortie :** chaque transformation ultérieure découle d'un constat visible dans l'EDA.

### Phase 3 — Prétraitement et création des variables

- [ ] P3.1 Séparer prédicteurs et cible.
- [ ] P3.2 Encoder la cible en 0/1.
- [ ] P3.3 Retirer `duration` du scénario réaliste.
- [ ] P3.4 Décider du traitement des 12 doublons après inspection.
- [ ] P3.5 Décider du traitement de `unknown` par validation.
- [ ] P3.6 Transformer le code sentinelle `pdays=999`.
- [ ] P3.7 Créer `previously_contacted` si elle apporte une information utile.
- [ ] P3.8 Définir listes numériques et catégorielles.
- [ ] P3.9 Construire `ColumnTransformer`.
- [ ] P3.10 Ajouter imputation, one-hot encoding et normalisation.
- [ ] P3.11 Tester le pipeline sur un petit échantillon.
- [ ] P3.12 Vérifier que les données de test ne sont jamais utilisées au `fit`.

**Critère de sortie :** la même pipeline transforme entraînement, validation, test et nouvelles observations.

### Phase 4 — Protocole expérimental et références

- [ ] P4.1 Créer les ensembles chronologiques 60/20/20.
- [ ] P4.2 Vérifier les proportions de classes dans chaque ensemble.
- [ ] P4.3 Conserver les indices de séparation.
- [ ] P4.4 Entraîner `DummyClassifier`.
- [ ] P4.5 Produire les métriques de référence.
- [ ] P4.6 Montrer pourquoi l'accuracy seule est insuffisante.

**Critère de sortie :** toute amélioration est mesurée contre une référence explicite.

### Phase 5 — Modèles de première itération

- [ ] P5.1 Entraîner la régression logistique.
- [ ] P5.2 Entraîner l'arbre de décision.
- [ ] P5.3 Entraîner la forêt aléatoire.
- [ ] P5.4 Tester k-NN si raisonnable.
- [ ] P5.5 Enregistrer paramètres, temps et métriques dans MLflow.
- [ ] P5.6 Construire un tableau comparatif initial.
- [ ] P5.7 Identifier biais, variance et surapprentissage.

**Critère de sortie :** un modèle prometteur et un modèle interprétable sont identifiés sans toucher au test final.

### Phase 6 — Optimisation et sélection

- [ ] P6.1 Définir des espaces d'hyperparamètres raisonnables.
- [ ] P6.2 Utiliser validation chronologique ou recherche contrôlée.
- [ ] P6.3 Comparer poids de classes et seuils.
- [ ] P6.4 Choisir le modèle selon performance, robustesse, coût et interprétabilité.
- [ ] P6.5 Fixer le seuil sur la validation.
- [ ] P6.6 Figer la configuration finale.

**Critère de sortie :** le modèle final est sélectionné selon une règle annoncée avant l'évaluation du test.

### Phase 7 — Évaluation finale

- [ ] P7.1 Réentraîner sur entraînement + validation si approprié.
- [ ] P7.2 Évaluer une seule fois sur le test chronologique.
- [ ] P7.3 Produire matrice de confusion brute et normalisée.
- [ ] P7.4 Produire rapport de classification.
- [ ] P7.5 Produire courbes ROC et précision-rappel.
- [ ] P7.6 Calculer métriques métier et lift.
- [ ] P7.7 Comparer entraînement, validation et test.
- [ ] P7.8 Documenter les résultats sans les exagérer.

**Critère de sortie :** la performance annoncée correspond à des données futures non utilisées pendant le développement.

### Phase 8 — Interprétation, erreurs et responsabilité

- [ ] P8.1 Examiner faux positifs et faux négatifs.
- [ ] P8.2 Étudier les prédicteurs importants.
- [ ] P8.3 Comparer coefficients, arbre et permutation importance.
- [ ] P8.4 Examiner la performance par sous-groupes pertinents.
- [ ] P8.5 Identifier risques de discrimination ou de variables proxy.
- [ ] P8.6 Distinguer corrélation et causalité.
- [ ] P8.7 Décrire limites et conditions d'utilisation.

**Critère de sortie :** il est possible d'expliquer ce que fait le modèle, ce qu'il ne prouve pas et où il peut échouer.

### Phase 9 — Reproductibilité et démonstration

- [ ] P9.1 Sérialiser la pipeline finale avec joblib.
- [ ] P9.2 Écrire `predict.py`.
- [ ] P9.3 Valider les entrées de prédiction.
- [ ] P9.4 Ajouter des tests unitaires et un test de bout en bout.
- [ ] P9.5 Ajouter `params.yaml` et les commandes DVC nécessaires.
- [ ] P9.6 Ajouter la GitHub Action minimale.
- [ ] P9.7 Vérifier l'installation depuis un environnement propre.
- [ ] P9.8 Compléter le README.
- [ ] P9.9 Préparer une démonstration stable.

**Critère de sortie :** une personne peut reproduire l'entraînement et exécuter une prédiction en suivant le README.

### Phase 10 — Présentation et remise

- [ ] P10.1 Construire le PowerPoint.
- [ ] P10.2 Sélectionner uniquement les graphiques utiles.
- [ ] P10.3 Préparer une démonstration de moins de deux minutes.
- [ ] P10.4 Préparer les réponses aux questions probables.
- [ ] P10.5 Répéter en respectant 15 minutes.
- [ ] P10.6 Vérifier que tout le code s'exécute.
- [ ] P10.7 Nettoyer les sorties inutiles des notebooks.
- [ ] P10.8 Vérifier citations et attribution CC BY 4.0.
- [ ] P10.9 Créer l'archive ou la version finale de remise.

**Critère de sortie :** présentation claire, projet exécutable, fichiers complets et étudiant capable de justifier chaque choix.

---

## 11. Plan proposé pour la présentation de 15 minutes

| Temps | Contenu |
|---:|---|
| 0:00–0:30 | titre, contexte et objectif |
| 0:30–2:00 | besoin d'affaires et décision à soutenir |
| 2:00–3:15 | dataset, source, licence et cible |
| 3:15–5:15 | EDA, déséquilibre et fuite `duration` |
| 5:15–6:45 | pipeline de prétraitement |
| 6:45–8:30 | modèles et protocole de validation |
| 8:30–11:00 | résultats et métriques |
| 11:00–12:30 | interprétation et analyse des erreurs |
| 12:30–13:30 | MLflow, DVC et reproductibilité |
| 13:30–14:30 | démonstration ou prédiction réelle |
| 14:30–15:00 | limites, compétences acquises et conclusion |

Questions à préparer :

- Pourquoi ce dataset ?
- Pourquoi une classification et non une régression ?
- Pourquoi supprimer `duration` ?
- Pourquoi l'accuracy n'est-elle pas suffisante ?
- Comment avez-vous traité le déséquilibre ?
- Comment avez-vous évité le surapprentissage ?
- Pourquoi avoir choisi le modèle final ?
- Comment le modèle serait-il utilisé par la banque ?
- Quels biais ou risques demeurent ?
- Comment reproduire les résultats ?

---

## 12. Échéancier

| Période | Objectif principal | Phases |
|---|---|---|
| 30 juin–5 juillet | initialisation, environnement, dataset et DVC | 0–1 |
| 6–12 juillet | EDA complète et décisions de nettoyage | 2 |
| 13–19 juillet | prétraitement, séparation et baseline | 3–4 |
| 20–26 juillet | modèles initiaux et MLflow | 5 |
| 27 juillet–2 août | optimisation et évaluation finale | 6–7 |
| 3–7 août | interprétation, tests et démonstration | 8–9 |
| 8–10 août | PowerPoint et répétition | 10 |
| 11 août | présentation | 10 |
| 12–15 août | corrections et remise finale | 10 |

Un tampon est conservé après la présentation pour corriger la documentation et préparer la remise finale.

---

## 13. Risques et mesures de contrôle

| Risque | Conséquence | Contrôle prévu |
|---|---|---|
| fuite via `duration` | performance irréaliste | retirer la variable du modèle final |
| classe positive rare | accuracy trompeuse | F1, rappel, précision, PR-AUC et lift |
| changement temporel | mauvaise généralisation | test chronologique |
| encodage avant split | fuite d'information | pipeline ajustée sur train seulement |
| trop d'outils | projet incomplet | distinguer périmètre principal et bonus |
| hyperparamètres testés sur le test | résultat biaisé | test final isolé |
| suppression automatique des outliers | perte d'information valide | analyser avant toute suppression |
| valeur `unknown` mal interprétée | transformation injustifiée | comparer les traitements en validation |
| étudiant seul | surcharge et risque d'échéance | prioriser un produit minimum complet |
| résultats non reproductibles | perte de crédibilité | versions, seeds, Git, DVC et MLflow |
| quota Free Edition épuisé | compute indisponible temporairement | expériences limitées, résultats persistés et démonstration de secours |
| accès Internet sortant restreint | téléchargement UCI impossible dans le notebook | téléversement contrôlé du CSV dans un Volume |
| ordre des lignes perdu par Spark | test chronologique invalide | ajouter `_source_row_number` avec pandas avant la conversion Spark |
| modèle difficile à expliquer | présentation faible | conserver une référence interprétable |
| variables démographiques | risque de biais | analyse par sous-groupes et limites explicites |

---

## 14. Règles de qualité

1. Toute décision doit être liée à un constat, une contrainte ou le besoin d'affaires.
2. Toute expérimentation importante doit être enregistrée.
3. Le test final ne doit pas guider le développement.
4. Le README doit permettre l'exécution sans explication orale.
5. Les notebooks doivent expliquer les résultats, pas seulement afficher du code.
6. Les graphiques doivent avoir titre, axes, unité et légende lorsque nécessaire.
7. La classe positive doit toujours être clairement indiquée.
8. Les limites doivent être présentées honnêtement.
9. Toute source externe doit être citée.
10. Le code doit rester compréhensible par l'étudiant et pouvoir être expliqué pendant les questions.
