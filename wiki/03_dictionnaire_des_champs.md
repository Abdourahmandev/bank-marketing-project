# 3. Dictionnaire des champs

[Retour à l'index](README.md)

Cette page décrit chaque colonne du fichier source. « Disponible avant l'appel »
signifie que la valeur peut raisonnablement être connue au moment où la banque
choisit la personne à contacter.

## Informations sur le client

| Champ | Type | Signification | Disponible avant l'appel | Traitement prévu |
|---|---|---|---|---|
| `age` | nombre | âge du client | oui | conserver comme nombre et surveiller les écarts entre groupes d'âge |
| `job` | catégorie | profession | oui | conserver les catégories, dont `unknown` |
| `marital` | catégorie | situation familiale ; `divorced` inclut aussi les personnes veuves selon UCI | oui | conserver, avec audit des biais possibles |
| `education` | catégorie | niveau d'études | oui | conserver, sans inventer de hiérarchie arbitraire |
| `default` | catégorie | présence connue d'un défaut de crédit | oui | conserver prudemment ; presque 21 % des valeurs sont inconnues |
| `housing` | catégorie | présence d'un prêt immobilier | oui | conserver `yes`, `no` et `unknown` |
| `loan` | catégorie | présence d'un prêt personnel | oui | conserver `yes`, `no` et `unknown` |

Valeurs observées :

- `job` : `admin.`, `blue-collar`, `entrepreneur`, `housemaid`, `management`,
  `retired`, `self-employed`, `services`, `student`, `technician`, `unemployed`,
  `unknown` ;
- `marital` : `married`, `single`, `divorced`, `unknown` ;
- `education` : `basic.4y`, `basic.6y`, `basic.9y`, `high.school`, `illiterate`,
  `professional.course`, `university.degree`, `unknown` ;
- `default`, `housing`, `loan` : `yes`, `no`, `unknown`.

## Informations sur le contact courant

| Champ | Type | Signification | Disponible avant l'appel | Traitement prévu |
|---|---|---|---|---|
| `contact` | catégorie | canal de communication : cellulaire ou téléphone | oui, si le canal est planifié | encodage catégoriel |
| `month` | catégorie | mois du contact | oui, lorsque la campagne est planifiée | conserver comme catégorie, car décembre n'est pas « douze fois » janvier |
| `day_of_week` | catégorie | jour de la semaine du contact | oui, lorsque l'appel est planifié | conserver comme catégorie |
| `duration` | nombre | durée du contact, en secondes | **non** | audit seulement ; exclure du modèle avant appel |

Les mois présents sont `mar`, `apr`, `may`, `jun`, `jul`, `aug`, `sep`, `oct`,
`nov` et `dec`. Les jours sont `mon`, `tue`, `wed`, `thu` et `fri`.

Le mois et le jour peuvent aussi capturer des changements de campagne ou de
conjoncture. Leur utilité doit donc être interprétée avec prudence : une forte
importance ne prouverait pas que le jour lui-même cause la souscription.

## Historique des campagnes

| Champ | Type | Signification | Disponible avant l'appel | Traitement prévu |
|---|---|---|---|---|
| `campaign` | nombre | numéro/nombre de contacts de la campagne courante, contact présent inclus | oui si l'appel courant est planifié | conserver comme nombre ; surveiller les valeurs extrêmes |
| `pdays` | nombre avec sentinelle | jours depuis le contact d'une campagne précédente ; 999 signifie « jamais contacté » | oui | remplacer par deux champs explicites |
| `previous` | nombre | nombre de contacts avant la campagne courante | oui | conserver comme nombre |
| `poutcome` | catégorie | résultat de la campagne précédente | oui | conserver `success`, `failure`, `nonexistent` |

La transformation de `pdays` produit :

- `previously_contacted` : 1 si un contact précédent existe, 0 autrement ;
- `days_since_previous_contact` : nombre de jours réel, ou 0 si aucun contact
  antérieur n'existe.

Grâce au premier champ, le modèle peut distinguer « aucun contact précédent »
d'un véritable délai de zéro jour.

## Contexte social et économique

| Champ source | Nom Silver | Type | Signification | Périodicité indiquée par UCI |
|---|---|---|---|---|
| `emp.var.rate` | `emp_var_rate` | nombre | taux de variation de l'emploi | trimestrielle |
| `cons.price.idx` | `cons_price_idx` | nombre | indice des prix à la consommation | mensuelle |
| `cons.conf.idx` | `cons_conf_idx` | nombre | indice de confiance des consommateurs | mensuelle |
| `euribor3m` | `euribor3m` | nombre | taux Euribor à trois mois | quotidienne |
| `nr.employed` | `nr_employed` | nombre | nombre d'employés, indicateur agrégé | trimestrielle |

Ces valeurs sont connues au moment de la campagne et peuvent représenter la
conjoncture économique. Elles ne décrivent pas directement un client. Comme les
données couvrent 2008 à 2010, elles risquent de perdre de leur pertinence dans
une autre période économique.

## Cible à prédire

| Champ | Valeurs | Signification | Disponible avant l'appel |
|---|---|---|---|
| `y` | `yes`, `no` | le client a-t-il souscrit au dépôt à terme ? | non ; c'est le résultat à apprendre |

Dans Silver, `y` devient `target` :

- `yes` devient 1 ;
- `no` devient 0.

## Résumé statistique des nombres

Les valeurs ci-dessous ont été calculées sur les 41 188 lignes brutes.

| Champ | Minimum | Médiane | Moyenne | Maximum |
|---|---:|---:|---:|---:|
| `age` | 17 | 38 | 40,02 | 98 |
| `duration` | 0 | 180 | 258,29 | 4 918 |
| `campaign` | 1 | 2 | 2,57 | 56 |
| `pdays` | 0 | 999 | 962,48 | 999 |
| `previous` | 0 | 0 | 0,17 | 7 |
| `emp.var.rate` | -3,4 | 1,1 | 0,08 | 1,4 |
| `cons.price.idx` | 92,201 | 93,749 | 93,576 | 94,767 |
| `cons.conf.idx` | -50,8 | -41,8 | -40,503 | -26,9 |
| `euribor3m` | 0,634 | 4,857 | 3,621 | 5,045 |
| `nr.employed` | 4 963,6 | 5 191,0 | 5 167,036 | 5 228,1 |

La médiane de `pdays` égale 999 parce que la majorité des clients n'avaient pas
été contactés dans une campagne antérieure. C'est un exemple clair d'une valeur
numérique qui ne doit pas être interprétée sans son sens métier.

## Quantité de valeurs `unknown`

| Champ | Nombre | Pourcentage |
|---|---:|---:|
| `default` | 8 597 | 20,87 % |
| `education` | 1 731 | 4,20 % |
| `housing` | 990 | 2,40 % |
| `loan` | 990 | 2,40 % |
| `job` | 330 | 0,80 % |
| `marital` | 80 | 0,19 % |

Les définitions originales proviennent de la
[fiche UCI du dataset](https://archive.ics.uci.edu/dataset/222/bank).
