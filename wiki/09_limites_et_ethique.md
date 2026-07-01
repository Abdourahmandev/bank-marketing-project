# 9. Limites, biais et usage responsable

[Retour à l'index](README.md)

Un modèle peut être techniquement correct et malgré tout être mal utilisé. Cette
page décrit ce que les données ne permettent pas d'affirmer et les contrôles à
conserver.

## Données anciennes et contexte particulier

Les observations proviennent d'une banque portugaise entre mai 2008 et novembre
2010. Elles couvrent notamment une période économique inhabituelle.

Un résultat obtenu sur ce fichier ne garantit pas la même performance :

- dans un autre pays ;
- pour une autre banque ;
- avec un autre produit ;
- avec les habitudes téléphoniques actuelles ;
- dans un environnement de taux différent.

Avant une utilisation réelle, il faudrait tester le modèle sur des données
récentes de l'organisation concernée.

## Dérive temporelle

Le taux positif passe d'environ 4,81 % dans le premier segment à 30,83 % dans le
dernier. Le comportement de la campagne et le contexte économique changent donc
fortement dans le temps.

Conséquences :

- une séparation aléatoire serait trop confortable ;
- les probabilités pourraient être mal calibrées sur une nouvelle période ;
- le modèle devrait être surveillé et réentraîné lorsque les données changent.

## Biais de sélection

Le fichier contient uniquement les personnes que la banque historique a choisi
de contacter. Il ne révèle pas ce qui serait arrivé pour les clients jamais
appelés.

Le modèle peut donc apprendre la stratégie passée de la banque autant que
l'intérêt réel des clients. Une association observée ne doit pas être présentée
comme une préférence universelle.

## Variables démographiques et financières

`age`, `job`, `marital`, `education`, `default`, `housing` et `loan` peuvent
créer ou renforcer des différences entre groupes.

Contrôles prévus :

- comparer les erreurs par sous-groupe lorsque les effectifs le permettent ;
- examiner si une variable apporte une valeur réelle ou seulement un biais ;
- documenter les groupes trop petits pour conclure ;
- ne jamais utiliser ce modèle comme décision de crédit ;
- garder une supervision humaine.

## Groupes très petits

Certaines catégories sont rares. Par exemple, `default=yes` apparaît seulement
trois fois et `education=illiterate` dix-huit fois. Une métrique calculée sur un
si petit groupe serait instable et pourrait être trompeuse.

Le projet signalera ces limites au lieu d'interpréter de petites différences
comme des faits solides.

## Valeurs inconnues

`unknown` peut signifier plusieurs choses : information non demandée, non
disponible ou non enregistrée. Le modèle pourrait apprendre le processus de
collecte de la banque plutôt qu'un comportement du client.

La première baseline conserve `unknown` comme catégorie. Une autre stratégie
sera comparée sur validation avant toute décision définitive.

## Absence d'identifiant client

Le fichier ne contient pas de nom, numéro de compte ou identifiant client
direct. Cela réduit le risque d'identification dans le projet, mais empêche aussi
de savoir si plusieurs lignes appartiennent à la même personne.

Les douze répétitions exactes sont contrôlées, mais des contacts multiples non
identiques pourraient concerner un même client. Il est impossible de créer une
séparation parfaite par personne sans identifiant.

## Fatigue et consentement

Un meilleur classement ne donne pas le droit d'appeler plus souvent. Une
organisation réelle devrait appliquer :

- les préférences de communication ;
- les listes de retrait ;
- une limite de fréquence ;
- des heures de contact appropriées ;
- les politiques et lois applicables.

Le nombre de contacts doit être considéré comme une contrainte de bien-être du
client, pas seulement comme une variable prédictive.

## Risque de fuite

La durée de l'appel est retirée du modèle déployable. Les transformations sont
ajustées uniquement sur l'entraînement, et le test reste fermé jusqu'à la fin.

Ces règles empêchent une performance irréaliste provenant d'information future.

## Explicabilité

Le responsable doit comprendre :

- quelles variables sont utilisées ;
- pourquoi `duration` est interdite ;
- ce que signifie le score ;
- quelles erreurs sont probables ;
- quand le modèle ne devrait plus être utilisé.

La régression logistique et l'arbre de décision seront conservés dans la
comparaison même si un modèle plus complexe gagne légèrement, car la facilité
d'explication a une valeur métier.

## Conditions minimales avant une utilisation réelle

- données récentes et autorisées ;
- validation sur la population concernée ;
- revue juridique et de confidentialité appropriée ;
- test des performances par sous-groupe ;
- seuil relié à un budget et à des coûts réels ;
- mécanisme de retrait et supervision humaine ;
- surveillance de la dérive ;
- procédure d'arrêt lorsque la qualité baisse.

Ce projet est un exercice pédagogique. Il ne constitue pas à lui seul un
système prêt pour une campagne bancaire réelle.
