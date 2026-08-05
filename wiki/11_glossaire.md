# 11. Glossaire

[Retour à l'index](README.md)

| Terme | Explication simple |
|---|---|
| apprentissage automatique | méthode qui apprend des régularités à partir d'exemples |
| apprentissage supervisé | apprentissage où la réponse historique est connue |
| audit | vérification du fonctionnement, des données et des résultats |
| baseline | méthode simple servant de point de comparaison |
| biais | différence systématique pouvant avantager, désavantager ou tromper |
| Bronze | table fidèle au fichier source, avec contrôles et métadonnées |
| calibration | correspondance entre probabilités annoncées et fréquences observées |
| catégorie | valeur qualitative, par exemple profession ou jour de la semaine |
| cible | résultat que le modèle doit prédire ; ici la souscription |
| classification binaire | choix entre deux classes, ici `yes` et `no` |
| CSV | fichier texte représentant un tableau de lignes et colonnes |
| DataFrame | tableau manipulé par pandas ou Spark |
| Delta Lake | format de table avec schéma et historique des écritures |
| dérive | changement des données ou des relations au fil du temps |
| doublon exact | ligne identique à une autre sur toutes les colonnes métier |
| DVC | outil de versionnement et provenance des données |
| EDA | analyse exploratoire des données avant la modélisation |
| encodage one-hot | transformation d'une catégorie en plusieurs indicateurs 0/1 |
| entraînement | période où le modèle apprend ses paramètres |
| exactitude | proportion totale de réponses correctes |
| faux négatif | souscription réelle que le modèle n'a pas priorisée |
| faux positif | appel priorisé qui n'aboutit pas à une souscription |
| fuite de données | information future ou interdite qui rend l'évaluation irréaliste |
| Git | système qui enregistre les versions des fichiers |
| Git Folder | copie synchronisée d'un dépôt Git dans Databricks |
| GitHub | service qui héberge le dépôt et les revues de changements |
| hyperparamètre | réglage choisi avant l'entraînement d'un modèle |
| imputation | remplacement contrôlé d'une information manquante |
| lift | gain de concentration des positifs par rapport à une sélection moyenne |
| machine learning | synonyme courant d'apprentissage automatique |
| manifeste | fiche qui décrit précisément le fichier attendu et son empreinte |
| médiane | valeur située au milieu lorsque les nombres sont triés |
| métrique | mesure utilisée pour évaluer un modèle |
| MLflow | outil qui conserve les expériences, paramètres, métriques et modèles |
| modèle | fonction apprise qui transforme des variables en estimation |
| notebook | document exécutable mêlant explications, code et résultats |
| observation | une ligne du jeu de données |
| pipeline | recette complète de transformation et de prédiction |
| précision | proportion de vrais positifs parmi les cas recommandés |
| prédiction | estimation produite par le modèle |
| probabilité | niveau estimé entre 0 et 1, et non une certitude individuelle |
| rappel | proportion des positifs réels retrouvés |
| régression logistique | modèle de classification linéaire produisant une probabilité |
| reproductibilité | capacité à refaire les étapes et obtenir le même résultat |
| SHA-256 | signature numérique utilisée pour reconnaître le fichier exact |
| Silver | table nettoyée et préparée pour le modèle |
| Spark | moteur de traitement de données utilisé par Databricks |
| standardisation | mise à une échelle comparable des variables numériques |
| seuil | valeur à partir de laquelle une probabilité devient une décision |
| test | ensemble final utilisé une seule fois après les choix |
| train | ensemble d'entraînement |
| `unknown` | catégorie indiquant qu'une information n'est pas connue |
| validation | ensemble utilisé pour comparer et régler les méthodes |
| valeur sentinelle | nombre spécial représentant un état ; ici 999 signifie jamais contacté |
| variable | information fournie au modèle |
| Volume | espace Databricks contenant le fichier brut |
