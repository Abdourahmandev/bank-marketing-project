# 6. Le machine learning sans jargon

[Retour à l'index](README.md)

## Idée générale

Le machine learning cherche des régularités dans des exemples historiques afin
de produire une estimation sur un nouvel exemple.

Dans ce projet, chaque ancienne ligne dit :

- ce qui était connu sur le client et la campagne ;
- si la personne a finalement souscrit.

Le modèle examine de nombreuses lignes et apprend une relation statistique entre
les informations d'entrée et la réponse. Il ne « comprend » pas une personne et
ne lit pas ses intentions.

## Une comparaison simple

Imaginez un responsable expérimenté qui a observé des milliers de campagnes. Il
remarque peut-être que certains historiques de contact ou contextes économiques
sont plus souvent associés à une souscription. Le modèle automatise ce type de
comparaison sur beaucoup de variables à la fois.

Il peut cependant apprendre les erreurs du passé, confondre une coïncidence avec
un signal durable ou devenir mauvais lorsque le contexte change.

## Apprentissage supervisé

Le projet utilise un apprentissage supervisé : la bonne réponse historique est
connue. La colonne `y` joue le rôle de réponse ou cible.

Les deux réponses possibles sont :

- 1 : souscription ;
- 0 : absence de souscription.

Comme il faut choisir entre deux classes, le problème est une classification
binaire.

## Variables et cible

- Une **variable** est une information fournie au modèle, par exemple l'âge ou
  le résultat d'une campagne précédente.
- La **cible** est ce que le modèle doit estimer, ici la souscription.
- Une **observation** est une ligne du fichier.
- Une **prédiction** est la réponse produite pour une nouvelle observation.

## Pourquoi obtenir une probabilité

Une réponse rigide `yes/no` cache l'incertitude. Une probabilité permet de
classer les clients.

Exemple fictif :

| Client | Probabilité estimée | Rang |
|---|---:|---:|
| A | 0,72 | 1 |
| B | 0,41 | 2 |
| C | 0,08 | 3 |

Ces nombres ne garantissent rien pour un individu. Ils servent à organiser une
population selon le signal appris.

## Entraînement, validation et test

### Entraînement

Le modèle apprend avec ce premier ensemble. C'est l'équivalent des exercices
utilisés pour étudier.

### Validation

Cet ensemble sert à comparer les méthodes et régler les choix. C'est
l'équivalent d'un examen pratique utilisé pour s'améliorer.

### Test

Cet ensemble reste fermé jusqu'à la fin. C'est l'examen final. Le consulter à
chaque modification finirait par adapter le projet à cet examen précis et
donnerait une impression exagérée de sa qualité.

## Les modèles prévus

### Modèle naïf

Il applique une règle très simple, par exemple toujours prédire la classe la
plus fréquente. Il ne doit pas gagner ; il fixe le minimum à dépasser.

### Régression logistique

Elle combine les variables avec des poids et produit une probabilité. Elle est
souvent un bon premier modèle parce que ses coefficients peuvent être examinés.

### Arbre de décision

Il construit une suite de questions, par exemple « le résultat précédent était-
il un succès ? ». Il est intuitif, mais un arbre trop profond peut mémoriser les
données.

### Forêt aléatoire

Elle combine plusieurs arbres construits avec des variations. Le vote collectif
est souvent plus stable qu'un seul arbre, au prix d'une explication moins simple.

### k plus proches voisins

k-NN recherche des observations historiques ressemblant à la nouvelle. La
méthode exige une bonne normalisation et peut devenir coûteuse lors des
prédictions.

## Surapprentissage

Un modèle surapprend lorsqu'il mémorise trop bien l'entraînement et fonctionne
mal sur une période nouvelle.

Signes possibles :

- résultat excellent sur `train`, beaucoup plus faible sur `validation` ;
- arbre extrêmement complexe ;
- performance très sensible à quelques lignes ;
- dépendance à une variable temporelle instable.

La validation chronologique, la limitation de complexité et la comparaison de
plusieurs modèles servent à contrôler ce risque.

## Fuite de données

Une fuite apparaît lorsqu'une information indisponible au moment réel de la
décision entre dans le modèle.

Ici, `duration` est l'exemple principal : la durée complète d'un appel ne peut
être connue avant de choisir qui appeler. Un modèle qui l'utilise répondrait à
une question plus facile mais inutile pour le besoin réel.

## Corrélation et causalité

Si un groupe souscrit plus souvent dans le fichier, cela ne prouve pas que son
caractère cause la souscription. Il peut exister d'autres raisons : stratégie de
la banque, période, sélection historique ou variables absentes.

Le projet construit un outil prédictif. Il ne prétend pas découvrir les causes
du comportement humain.
