# Configuration de Databricks Free Edition

Ce guide décrit les actions manuelles nécessaires dans le compte Databricks. Le
code et les notebooks restent versionnés dans GitHub ; les données sont stockées
dans Unity Catalog.

## 1. Synchroniser le Git Folder

Dans le Git Folder `bank-marketing-project` :

1. ouvrir le panneau Git ;
2. vérifier que la branche est `main` ;
3. cliquer sur **Pull** après chaque mise à jour publiée depuis le poste local ;
4. vérifier que `notebooks/databricks/` et `data/dataset_manifest.json` apparaissent.

Ne jamais copier un token GitHub ou Databricks dans un notebook ou un fichier du dépôt.

## 2. Exécuter la configuration

1. Ouvrir `notebooks/databricks/00_configuration.py`.
2. Choisir le compute serverless.
3. Exécuter tout le notebook.
4. Noter les valeurs affichées pour le catalogue, le schéma et le Volume.

Par défaut, le notebook utilise le catalogue et le schéma courants et crée un
Volume géré nommé `bank_marketing`. Les widgets permettent de modifier ces noms
sans changer le code.

La commande SQL suivante peut aussi confirmer le contexte :

```sql
SELECT current_catalog(), current_schema();
```

## 3. Téléverser le CSV officiel

Databricks Free Edition limite les téléchargements Internet depuis le compute.
Le fichier doit donc être téléversé avec l'interface.

Fichier attendu :

```text
bank-additional-full.csv
```

Une copie officielle déjà vérifiée est disponible sur ce poste dans :

```text
C:\Users\User\Downloads\420-C74-20260630T221457Z-3-001\bank-marketing-project\data\raw\bank-additional-full.csv
```

Ce fichier est volontairement ignoré par Git.

Empreinte SHA-256 attendue :

```text
74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8
```

Taille attendue : `5 834 924` octets.

Dans Databricks :

1. ouvrir **Catalog** ;
2. ouvrir le catalogue et le schéma affichés par `00_configuration` ;
3. ouvrir **Volumes** puis `bank_marketing` ;
4. créer ou sélectionner le dossier `raw` ;
5. utiliser **Upload to this volume** ;
6. téléverser `bank-additional-full.csv`.

Le chemin final attendu est affiché par le notebook de configuration et ressemble à :

```text
/Volumes/<catalogue>/<schema>/bank_marketing/raw/bank-additional-full.csv
```

Le CSV ne doit pas être ajouté directement à GitHub.

## 4. Créer la table Bronze

Ouvrir et exécuter :

```text
notebooks/databricks/01_ingestion_bronze.py
```

Le notebook refuse de continuer si :

- le fichier est absent ;
- sa taille ou son SHA-256 diffère ;
- il ne contient pas 41 188 lignes et 21 colonnes ;
- les colonnes ou la cible ne correspondent pas à la variante officielle ;
- le nombre de doublons exacts diffère du fichier vérifié.

Il ajoute `_source_row_number` avant la conversion Spark pour préserver l'ordre
chronologique du CSV, puis crée la table Delta `bank_marketing_bronze`.

## 5. Exécuter l'EDA

Après la réussite de l'ingestion, ouvrir et exécuter :

```text
notebooks/databricks/02_eda.py
```

Les premiers résultats attendus sont :

- 36 548 lignes `no` ;
- 4 640 lignes `yes` ;
- environ 11,27 % de classe positive ;
- 12 doublons exacts ;
- aucune valeur `NaN` brute ;
- plusieurs valeurs catégorielles `unknown` ;
- forte association entre `duration` et `y`, mais `duration` non disponible avant l'appel.

## 6. Créer la table Silver

Après l'EDA, exécuter :

```text
notebooks/databricks/03_preprocessing_silver.py
```

Les contrôles attendus sont :

- 41 176 lignes après retrait des 12 répétitions exactes ;
- cible binaire : 36 537 zéros et 4 639 uns ;
- 24 705 lignes d'entraînement, 8 235 de validation et 8 236 de test ;
- aucune valeur sentinelle `999` dans `days_since_previous_contact` ;
- `duration` absente de la liste `DEPLOYMENT_FEATURES`.

## 7. Règles de travail

- GitHub contient le code, la documentation et les notebooks.
- Le Volume contient le CSV brut.
- Les tables Delta contiennent les états Bronze, Silver et les prédictions.
- MLflow contiendra les paramètres, métriques, figures et modèles.
- Le test final ne sera pas consulté pendant le réglage.
- Les sorties critiques seront sauvegardées, car Free Edition est soumise à des quotas.
