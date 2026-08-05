# 10. Guide d'exécution

[Retour à l'index](README.md)

Ce guide décrit ce qu'une personne doit faire dans Databricks. Il n'est pas
nécessaire de comprendre chaque ligne de code pour suivre le déroulement.

## Avant de commencer

Il faut disposer de :

- l'accès au dépôt GitHub ;
- un compte Databricks Free Edition ;
- un Git Folder Databricks relié au dépôt ;
- le fichier officiel `bank-additional-full.csv` ;
- un compute serverless disponible.

Le guide technique détaillé se trouve dans
[`docs/databricks_setup.md`](../docs/databricks_setup.md).

## 1. Synchroniser le projet

Dans le Git Folder Databricks :

1. choisir la branche `main` ;
2. utiliser **Pull** ;
3. vérifier que le dossier `notebooks/databricks` est visible.

Cette étape récupère la dernière version du code et du wiki.

## 2. Exécuter la configuration

Ouvrir puis exécuter :

```text
notebooks/databricks/00_configuration.py
```

Le notebook affiche :

- la racine du dépôt ;
- le catalogue ;
- le schéma ;
- le chemin du Volume ;
- le chemin exact attendu pour le CSV ;
- les noms des tables Bronze et Silver.

Il crée également le dossier `raw` si nécessaire.

## 3. Téléverser le fichier

Dans **Catalog**, ouvrir le catalogue, le schéma et le Volume affichés. Placer
`bank-additional-full.csv` dans le sous-dossier `raw`.

Ne pas renommer le fichier et ne pas l'ouvrir puis le réenregistrer avec un
tableur : cela pourrait modifier son empreinte.

## 4. Créer Bronze

Exécuter :

```text
notebooks/databricks/01_ingestion_bronze.py
```

Résultats attendus :

| Contrôle | Valeur |
|---|---:|
| lignes | 41 188 |
| colonnes métier | 21 |
| répétitions exactes | 12 |
| `no` | 36 548 |
| `yes` | 4 640 |

Le SHA-256 affiché doit être :

```text
74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8
```

Si une valeur diffère, il faut arrêter et vérifier le fichier.

## 5. Exécuter l'analyse exploratoire

Exécuter :

```text
notebooks/databricks/02_eda.py
```

Lire les tableaux et graphiques dans cet ordre :

1. distribution de la cible ;
2. quantité de `unknown` ;
3. statistiques et histogrammes ;
4. comparaison de `duration` selon la cible ;
5. taux de souscription par catégorie ;
6. matrice de corrélation ;
7. conclusions.

Il faut éviter d'interpréter une association comme une cause.

## 6. Créer Silver

Lorsque le notebook 03 est présent dans `main`, exécuter :

```text
notebooks/databricks/03_preprocessing_silver.py
```

Résultats attendus :

| Contrôle | Valeur |
|---|---:|
| lignes Silver | 41 176 |
| répétitions retirées | 12 |
| cibles 0 | 36 537 |
| cibles 1 | 4 639 |
| train | 24 705 |
| validation | 8 235 |
| test | 8 236 |

Vérifier aussi que :

- `days_since_previous_contact` ne contient plus 999 ;
- `previously_contacted` contient seulement 0 ou 1 ;
- `duration` apparaît comme `audit_only` et non comme `deployment`.

## 7. Modélisation future

Les notebooks suivants ajouteront :

- la baseline naïve ;
- la pipeline scikit-learn ;
- la régression logistique ;
- l'arbre et la forêt aléatoire ;
- les expériences MLflow ;
- le choix du seuil ;
- l'évaluation finale.

Le test final ne doit pas être consulté pour choisir un modèle.

## En cas d'erreur

Conserver :

- le nom du notebook ;
- le numéro ou le titre de la cellule ;
- le message complet ;
- les valeurs des widgets catalogue, schéma et Volume ;
- l'étape qui venait d'être réalisée.

Ne jamais publier de jeton, mot de passe ou autre secret dans une capture ou un
message GitHub.

## Vérification visuelle dans Catalog

Après exécution, le schéma doit contenir :

- `bank_marketing_bronze` ;
- `bank_marketing_silver`, après le notebook 03 ;
- plus tard, une table de prédictions.

L'historique Delta affiché à la fin des notebooks prouve quand une table a été
créée ou remplacée.
