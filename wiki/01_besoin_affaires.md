# 1. Le besoin d'affaires

[Retour à l'index](README.md)

## Situation de départ

Une banque commercialise des dépôts à terme. Un dépôt à terme est un produit
d'épargne : le client place une somme pendant une période convenue, généralement
en échange d'un taux d'intérêt déterminé.

Pour trouver des clients intéressés, la banque mène des campagnes
téléphoniques. Un appel a cependant un coût : temps d'un agent, infrastructure,
suivi administratif et risque de déranger le client. Lorsque les ressources
sont limitées, appeler tout le monde n'est pas une bonne stratégie.

## Décision que le système doit soutenir

Le système répond à la question suivante :

> Parmi les clients qui pourraient être contactés, lesquels faut-il appeler en
> premier pour augmenter les chances de souscription à un dépôt à terme ?

Il produit pour chaque ligne :

- une probabilité estimée de souscription ;
- un rang de priorité ;
- éventuellement une recommandation « appeler » ou « ne pas appeler
  maintenant », selon le budget de la campagne.

Par exemple, si la banque peut appeler seulement 10 % de sa liste, elle peut
commencer par les 10 % ayant les probabilités les plus élevées.

## Utilisateur principal

Le principal utilisateur fictif est le responsable de la campagne marketing.
Il doit :

- choisir le volume d'appels ;
- organiser le travail des agents ;
- suivre les souscriptions ;
- éviter les campagnes coûteuses ou trop insistantes ;
- expliquer pourquoi une stratégie a été retenue.

Les agents utilisent ensuite la liste priorisée. Ils conservent leur jugement et
doivent respecter les préférences de communication des clients.

## Ce que le système ne fait pas

Le projet ne sert pas à :

- accepter ou refuser un crédit ;
- déterminer le taux d'intérêt offert ;
- prouver qu'un client souscrira ;
- appeler automatiquement une personne ;
- remplacer le consentement, les règles de communication ou le jugement humain ;
- mesurer la valeur financière complète d'un client.

## Deux types d'erreurs

### Faux positif

Le modèle recommande d'appeler une personne qui ne souscrit pas.

Conséquences possibles : coût d'appel, temps perdu et mécontentement du client.

### Faux négatif

Le modèle ne priorise pas une personne qui aurait souscrit.

Conséquence possible : occasion commerciale manquée.

Le meilleur compromis dépend de la campagne. Si les appels sont très coûteux,
la banque recherche davantage de précision. Si rater un client intéressé coûte
très cher, elle peut préférer un rappel plus élevé. Ces termes sont expliqués
dans [la mesure du succès](07_evaluation_et_decision.md).

## Définition d'un projet réussi

Le projet sera utile si :

- il classe mieux les clients qu'une stratégie naïve ;
- il trouve une part importante des souscriptions avec moins d'appels ;
- il n'utilise que l'information disponible au moment de la décision ;
- son fonctionnement est reproductible et explicable ;
- ses limites et ses effets sur différents groupes sont documentés ;
- le responsable peut choisir un seuil selon son budget réel.

Une bonne note de modèle n'est donc pas suffisante. Le résultat doit aussi être
compréhensible, utilisable et honnête sur ses limites.
