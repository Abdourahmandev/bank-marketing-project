# 7. Comment mesurer le succès

[Retour à l'index](README.md)

## Pourquoi l'exactitude ne suffit pas

88,73 % des réponses historiques sont `no`. Un système qui répond toujours
`no` obtiendrait donc 88,73 % d'exactitude, mais ne trouverait aucun client
intéressé.

Le projet utilise plusieurs mesures complémentaires et les relie au coût des
appels.

## Matrice de confusion

La matrice de confusion classe chaque résultat dans quatre cases :

| | Le client souscrit réellement | Le client ne souscrit pas |
|---|---|---|
| le modèle recommande l'appel | vrai positif | faux positif |
| le modèle ne recommande pas l'appel | faux négatif | vrai négatif |

- **Vrai positif** : appel priorisé et souscription obtenue.
- **Faux positif** : appel priorisé sans souscription.
- **Faux négatif** : client non priorisé qui aurait souscrit.
- **Vrai négatif** : client non priorisé qui n'aurait pas souscrit.

## Mesures principales

### Précision

Parmi les personnes recommandées, quelle proportion souscrit réellement ?

Une précision élevée réduit les appels peu productifs.

### Rappel

Parmi toutes les personnes qui auraient souscrit, quelle proportion a été
trouvée par le modèle ?

Un rappel élevé réduit les occasions manquées.

### F1

F1 résume précision et rappel dans une seule mesure. Elle est utile pour comparer
rapidement des modèles, mais ne remplace pas le choix métier du seuil.

### ROC-AUC

Cette mesure évalue la capacité générale du modèle à classer un positif devant
un négatif pour plusieurs seuils. Elle est courante, mais peut paraître
optimiste lorsque la classe positive est rare.

### PR-AUC

L'aire sous la courbe précision-rappel se concentre davantage sur la classe rare
`yes`. Elle sera donc particulièrement importante dans ce projet.

### Lift

Le lift compare la liste priorisée à une sélection sans modèle.

Exemple fictif : si 10 % de la liste sélectionnée par le modèle contient trois
fois plus de souscriptions qu'une sélection moyenne de même taille, le lift à
10 % vaut 3.

### Rappel dans les meilleurs 10 %

Cette mesure répond directement à une question de campagne : si la banque peut
appeler seulement 10 % des clients, quelle part de toutes les souscriptions se
trouve dans cette tranche ?

### Calibration

Un modèle est bien calibré lorsque les groupes auxquels il attribue environ 30 %
de probabilité souscrivent réellement environ 30 % du temps. La calibration est
utile si le responsable veut transformer les probabilités en prévisions de
volume.

## Choisir un seuil

Une probabilité doit être convertie en décision. Le seuil 0,5 n'est pas
automatiquement le meilleur.

Le projet comparera notamment :

- un seuil qui équilibre précision et rappel ;
- un seuil qui atteint un rappel minimal ;
- une sélection des meilleurs scores selon un budget de 10 % d'appels.

Le seuil sera choisi avec la validation, jamais avec le test final.

## Traduire le résultat en coût métier

Lorsque des coûts réalistes sont disponibles, une simulation peut utiliser :

- le coût d'un appel ;
- la valeur moyenne d'une souscription ;
- la capacité quotidienne des agents ;
- le coût d'une occasion manquée ;
- une limite de fréquence de contact.

Sans ces montants, le projet présentera des scénarios plutôt qu'un bénéfice
financier inventé.

## Protocole de choix

1. Entraîner chaque candidat uniquement sur `train`.
2. Mesurer les candidats sur `validation`.
3. Comparer performance, stabilité, interprétabilité et coût.
4. Choisir le traitement de `unknown`, le modèle et le seuil.
5. Figer les décisions dans le journal.
6. Évaluer une seule fois sur `test`.
7. Rapporter les résultats, y compris les faiblesses.

## Analyse par sous-groupe

Une bonne moyenne peut cacher un mauvais résultat pour certains groupes. Le
projet examinera, lorsque les effectifs le permettent :

- des groupes d'âge ;
- des professions ;
- des niveaux d'études ;
- des situations familiales ;
- des canaux de communication.

L'objectif n'est pas d'affirmer qu'une différence est automatiquement injuste,
mais de détecter les écarts et de discuter leurs causes possibles.

## Résultats actuels

Aucune performance de modèle n'est encore définitive. Cette page décrit le
protocole qui sera appliqué. Les métriques réelles seront ajoutées après les
expériences MLflow et la sélection finale.
