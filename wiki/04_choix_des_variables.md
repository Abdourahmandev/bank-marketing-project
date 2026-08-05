# 4. Pourquoi ces variables ont été choisies

[Retour à l'index](README.md)

## Principe principal

Une variable n'est pas choisie uniquement parce qu'elle augmente une note. Elle
doit aussi :

1. être disponible au moment où la décision est prise ;
2. avoir un sens métier compréhensible ;
3. être suffisamment fiable ;
4. ne pas révéler directement le résultat futur ;
5. pouvoir être utilisée de façon responsable.

Le fichier UCI fournit 20 variables d'entrée. Pour la première comparaison, le
projet conserve toutes les informations disponibles avant l'appel. Il retire
`duration`, puis transforme `pdays` en deux champs plus honnêtes.

## Variables numériques prévues pour le modèle

| Variable | Pourquoi la conserver | Point à surveiller |
|---|---|---|
| `age` | les besoins d'épargne peuvent varier selon l'étape de vie | variable démographique ; vérifier l'équité entre groupes |
| `campaign` | plusieurs tentatives peuvent signaler l'intérêt ou la fatigue | valeur extrême possible ; association non causale |
| `days_since_previous_contact` | un contact récent ou ancien peut influencer la réponse | n'a de sens qu'avec `previously_contacted` |
| `previously_contacted` | distingue les nouveaux contacts des clients déjà joints | peut refléter une stratégie historique de la banque |
| `previous` | mesure l'intensité des campagnes antérieures | la majorité des valeurs sont faibles |
| `emp_var_rate` | représente le contexte de l'emploi | risque de dérive entre périodes économiques |
| `cons_price_idx` | représente le contexte des prix | variation limitée dans la période observée |
| `cons_conf_idx` | représente le climat de confiance | indicateur agrégé, pas une opinion individuelle |
| `euribor3m` | lié au contexte des taux d'intérêt | relation historique pouvant changer |
| `nr_employed` | autre indicateur du contexte économique | fortement lié au temps et à d'autres indicateurs |

## Variables catégorielles prévues

| Variable | Pourquoi la conserver | Point à surveiller |
|---|---|---|
| `job` | la situation professionnelle peut correspondre à des besoins financiers différents | biais envers certaines professions |
| `marital` | peut représenter des étapes de vie et responsabilités différentes | information personnelle sensible |
| `education` | peut être liée au type de produit ou à sa compréhension | risque de traitement inéquitable |
| `default` | décrit un élément de la situation financière | seulement 3 `yes` et beaucoup de `unknown` ; utilité incertaine |
| `housing` | un prêt immobilier influence les engagements financiers | information financière personnelle |
| `loan` | un prêt personnel influence les engagements financiers | information financière personnelle |
| `contact` | le canal planifié peut affecter la joignabilité | ne prouve pas que le canal cause la réponse |
| `month` | capture saison, calendrier et contexte de campagne | peut surtout mémoriser la période historique |
| `day_of_week` | capture l'organisation de la campagne | effet potentiellement instable |
| `poutcome` | le résultat précédent est un signal métier direct | `nonexistent` domine largement |

## Variable explicitement exclue : `duration`

`duration` serait probablement très utile pour prédire la souscription, car un
appel long peut indiquer une conversation engagée. Mais la durée n'existe
qu'après le début et la fin de l'appel.

Le besoin d'affaires consiste précisément à choisir **avant** l'appel. Utiliser
`duration` donnerait une performance artificielle impossible à reproduire en
production. Ce problème s'appelle une fuite de données.

La colonne est conservée dans la zone d'audit pour montrer l'effet de la fuite,
mais elle n'appartient jamais à la liste des variables déployables.

## Pourquoi les catégories ne deviennent pas simplement des nombres

Attribuer `admin.=1`, `technician=2` et `student=3` créerait un ordre qui n'existe
pas. Le projet prévoit donc un encodage « one-hot » : une petite colonne oui/non
est créée pour chaque catégorie.

Exemple simplifié :

| `contact` original | `contact_cellular` | `contact_telephone` |
|---|---:|---:|
| cellular | 1 | 0 |
| telephone | 0 | 1 |

Cet encodage est appris dans une pipeline afin d'être appliqué de la même façon
aux données d'entraînement, de validation, de test et aux futurs clients.

## Pourquoi les nombres seront normalisés

`age` se mesure en années, tandis que `nr_employed` se mesure en milliers. Pour
les modèles sensibles à l'échelle, comme la régression logistique ou k-NN, le
projet prévoit une standardisation. Elle recentre les variables sans changer le
sens des observations.

Les moyennes et écarts utilisés pour cette opération seront calculés uniquement
sur l'ensemble d'entraînement. Utiliser tout le fichier révélerait indirectement
de l'information sur le futur.

## Choix encore ouverts

- comparer `unknown` comme catégorie à une stratégie d'imputation ;
- mesurer si `default` apporte une information stable ;
- vérifier si certains indicateurs économiques sont trop redondants ;
- évaluer l'impact des variables démographiques sur les sous-groupes ;
- retirer une variable seulement à partir de l'entraînement et de la validation,
  jamais parce qu'elle améliore le test final.

Aucune importance de variable n'est encore annoncée : les modèles n'ont pas
encore été sélectionnés.
