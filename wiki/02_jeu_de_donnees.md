# 2. Le jeu de données

[Retour à l'index](README.md)

## Source

Le projet utilise le jeu public
[Bank Marketing de l'UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/222/bank).
Il a été créé par Sergio Moro, Paulo Cortez et Paulo Rita à partir de campagnes
de marketing direct d'une banque portugaise.

- variante : `bank-additional-full.csv` ;
- période : mai 2008 à novembre 2010 ;
- ordre : observations classées chronologiquement ;
- licence : Creative Commons Attribution 4.0 ;
- DOI : [10.24432/C5K306](https://doi.org/10.24432/C5K306).

La licence permet la réutilisation et l'adaptation, à condition de citer la
source. Le fichier exact utilisé est décrit dans
[`data/dataset_manifest.json`](../data/dataset_manifest.json).

## Pourquoi cette variante a été choisie

L'archive UCI contient plusieurs variantes. `bank-additional-full.csv` a été
retenue parce qu'elle :

- contient les 41 188 observations disponibles dans la version enrichie ;
- possède 20 variables d'entrée, donc davantage de contexte économique ;
- est ordonnée dans le temps, ce qui permet une évaluation plus réaliste ;
- est assez grande pour comparer plusieurs modèles ;
- reste assez petite pour être traitée gratuitement dans Databricks ;
- contient des problèmes pédagogiques utiles : déséquilibre, catégories,
  valeur sentinelle, doublons et fuite de données.

La variante de 10 % aurait été plus rapide, mais aurait réduit la fiabilité des
comparaisons et l'analyse de petits groupes.

## Que représente une ligne ?

Une ligne décrit le résultat d'un contact de campagne pour un client :

- quelques caractéristiques du client ;
- la façon et le moment du contact ;
- l'historique de campagne ;
- le contexte économique ;
- la réponse finale : souscription ou non.

Une même personne a pu être contactée plusieurs fois pendant une campagne. Le
fichier ne fournit toutefois aucun identifiant client permettant de relier avec
certitude plusieurs lignes à la même personne.

## Dimensions vérifiées

| Mesure | Valeur |
|---|---:|
| observations | 41 188 |
| variables d'entrée | 20 |
| cible | 1 (`y`) |
| réponses `yes` | 4 640 (11,27 %) |
| réponses `no` | 36 548 (88,73 %) |
| valeurs `NaN` brutes | 0 |
| répétitions exactes après la première | 12 |

La classe positive est rare : presque neuf lignes sur dix sont `no`. Un modèle
qui répond toujours `no` aurait donc environ 88,73 % d'exactitude tout en étant
inutile pour trouver des souscriptions. C'est pourquoi le projet ne juge jamais
un modèle avec l'exactitude seule.

## Problèmes de qualité importants

### Valeur `unknown`

Le fichier n'a pas de cellule vide classique, mais certaines catégories valent
`unknown`. Cela signifie que l'information n'est pas connue. Les champs touchés
sont `job`, `marital`, `education`, `default`, `housing` et `loan`.

Le cas le plus important est `default` : 8 597 lignes, soit 20,87 %, sont
`unknown`. Remplacer arbitrairement ces valeurs par `no` pourrait introduire une
fausse information. La première version les conserve donc comme une catégorie.

### Répétitions exactes

Douze lignes sont la répétition exacte d'une ligne précédente. La table Bronze
les conserve pour rester fidèle au fichier. La table Silver prévoit de garder
la première occurrence et de retirer les 12 répétitions.

L'inspection confirme que chaque paire reste à l'intérieur du même segment
chronologique : aucune paire ne traverse entraînement, validation et test.

### Sentinelle `pdays=999`

`pdays` représente le nombre de jours depuis un contact antérieur. La valeur 999
ne veut pas dire « il y a 999 jours » : elle signifie que le client n'avait pas
été contacté auparavant. Elle doit donc être transformée pour ne pas tromper le
modèle.

### Variable `duration`

`duration` indique la durée de l'appel qui vient d'avoir lieu. Elle est très liée
à la souscription, mais elle est inconnue avant l'appel. L'utiliser pour choisir
qui appeler reviendrait à donner au modèle une information provenant du futur.
Elle est analysée pour démontrer ce piège, puis exclue du modèle utilisable.

## Vérification de l'identité du fichier

Avant la création de la table Bronze, le projet contrôle :

- le nom de la variante ;
- la taille, soit 5 834 924 octets ;
- l'empreinte SHA-256 ;
- les 21 colonnes et leur ordre ;
- les 41 188 lignes ;
- la distribution exacte de la cible ;
- les 12 répétitions.

L'empreinte agit comme une signature numérique. Si un seul caractère du fichier
change, la signature change et l'ingestion s'arrête au lieu de produire
silencieusement des résultats différents.
