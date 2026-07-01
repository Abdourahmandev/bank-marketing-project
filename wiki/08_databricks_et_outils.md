# 8. Databricks et les outils

[Retour à l'index](README.md)

## Pourquoi utiliser plusieurs outils ?

Chaque outil répond à une responsabilité différente. Les séparer rend le projet
plus facile à vérifier et évite qu'un seul notebook mélange données, modèles,
secrets et documentation.

## Databricks Free Edition

[Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition)
est l'environnement principal d'exécution. Il permet de lancer les
notebooks, consulter les tables, produire des graphiques et suivre les
expériences dans un même espace.

La Free Edition suffit pour les 41 188 lignes du projet. Elle impose toutefois
des quotas, fonctionne uniquement avec du compute serverless et limite certains
accès Internet, raison pour laquelle le CSV est téléversé manuellement. Ces
contraintes sont détaillées dans la
[documentation officielle des limites](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).

## GitHub et Git Folder

GitHub conserve :

- le code ;
- les notebooks au format texte ;
- les tests ;
- le plan ;
- ce wiki.

Le Git Folder Databricks synchronise ces fichiers avec le workspace. Git permet
de savoir qui a changé quoi et de revenir à une version précédente.

Le CSV brut n'est pas enregistré directement dans GitHub.

## Unity Catalog

Unity Catalog organise les données avec trois niveaux :

```text
catalogue.schema.objet
```

Il permet de retrouver les tables et les Volumes avec des noms cohérents et de
centraliser leur gouvernance.

## Volume

Le Volume contient le fichier CSV officiel utilisé pendant l'exécution. Le
chemin ressemble à :

```text
/Volumes/<catalogue>/<schema>/bank_marketing/raw/bank-additional-full.csv
```

Les valeurs entre chevrons dépendent du workspace de l'utilisateur.

## Spark

Spark est un moteur de traitement de données. Dans ce projet, il sert surtout à :

- lire et contrôler les tables ;
- effectuer des agrégations ;
- écrire les tables Delta ;
- afficher des résultats dans Databricks.

Le dataset étant petit, le modèle n'a pas besoin d'un entraînement distribué.

## Delta Lake

Delta ajoute aux tables un schéma contrôlé et un historique des écritures. Le
projet utilise :

- Bronze pour la copie fidèle et contrôlée ;
- Silver pour les transformations déterministes ;
- une future table de prédictions pour les scores et décisions.

## pandas

pandas manipule des tableaux en mémoire. Les 41 188 lignes tiennent facilement
dans cet environnement. pandas est utilisé pour préserver l'ordre du CSV,
effectuer certains audits et fournir les données à scikit-learn.

## scikit-learn

scikit-learn fournit les transformations, pipelines, modèles et métriques de
machine learning. C'est aussi la bibliothèque centrale étudiée dans le cours.

## MLflow

MLflow agit comme un cahier de laboratoire automatique. Pour chaque essai, il
conserve paramètres, mesures, graphiques et modèle. La version intégrée à
Databricks évite de maintenir un serveur séparé.

## DVC

DVC est prévu pour tracer la provenance du fichier de données côté local sans
placer le gros fichier dans Git. Son stockage distant reste à configurer. Delta
et DVC ne jouent pas exactement le même rôle : Delta suit les tables
d'exécution, tandis que DVC relie le projet Git à une version précise des
données.

## Tests automatisés

Les tests vérifient notamment :

- la liste des colonnes ;
- l'exclusion de `duration` ;
- les frontières chronologiques ;
- l'encodage de la cible ;
- la transformation de `pdays` ;
- la détection des métadonnées manquantes.

Un test ne garantit pas que le modèle est bon. Il garantit qu'une règle
technique importante continue de fonctionner après une modification.

## Répartition des responsabilités

| Élément | Responsabilité |
|---|---|
| GitHub | versions du code et de la documentation |
| Git Folder | synchronisation du dépôt dans Databricks |
| Volume | fichier CSV brut |
| Bronze | preuve fidèle de l'entrée |
| Silver | données préparées et segments |
| Spark/Delta | contrôles et tables |
| pandas/scikit-learn | transformations apprises et modèles |
| MLflow | suivi des expériences |
| DVC | provenance durable du fichier local |
