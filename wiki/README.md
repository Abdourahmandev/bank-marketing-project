# Wiki du projet Bank Marketing

Ce wiki explique le projet à une personne qui ne connaît ni la programmation ni
l'apprentissage automatique. Il commence par le problème réel de la banque,
puis présente les données, les choix, le fonctionnement et les limites du
système.

## Résumé en une minute

Une banque souhaite proposer un dépôt à terme par téléphone. Appeler tous ses
clients coûte du temps, mobilise des employés et peut agacer des personnes peu
intéressées. Le projet construit donc un outil d'aide à la décision qui attribue
à chaque client une probabilité de souscription **avant l'appel**.

Le système ne décide pas à la place de la banque et ne garantit pas qu'une
personne acceptera. Il sert à classer les clients pour commencer par les plus
susceptibles d'être intéressés, dans la limite d'un budget d'appels.

Le projet utilise 41 188 résultats historiques de campagnes téléphoniques d'une
banque portugaise. La réponse observée est `yes` lorsqu'un dépôt à terme a été
souscrit et `no` autrement.

## Parcours conseillé

Pour comprendre l'essentiel sans lire de code :

1. [Le besoin d'affaires](01_besoin_affaires.md)
2. [Le jeu de données](02_jeu_de_donnees.md)
3. [Les champs du fichier](03_dictionnaire_des_champs.md)
4. [Les choix de variables](04_choix_des_variables.md)
5. [Le fonctionnement du projet](05_fonctionnement_du_projet.md)
6. [Le machine learning sans jargon](06_machine_learning_sans_jargon.md)
7. [La mesure du succès](07_evaluation_et_decision.md)

Pour comprendre la partie plateforme, l'exécution et les risques :

8. [Databricks et les outils](08_databricks_et_outils.md)
9. [Les limites, biais et usages responsables](09_limites_et_ethique.md)
10. [Le guide d'exécution](10_guide_execution.md)
11. [Le glossaire](11_glossaire.md)
12. [L'historique de la documentation](HISTORIQUE.md)

## État actuel

| Élément | État | Signification |
|---|---|---|
| cadrage du besoin | terminé | le décideur, la décision et la cible sont définis |
| données brutes | terminé | le fichier officiel et son empreinte sont vérifiés |
| table Bronze | exécutée | une copie contrôlée existe dans Databricks |
| analyse exploratoire initiale | exécutée | qualité, cible, distributions et fuite principale sont examinées |
| table Silver | préparée | le notebook est en cours d'intégration et doit être exécuté |
| modèles | à venir | aucune performance finale n'est encore annoncée |
| modèle final | à venir | le test final ne sera consulté qu'après sélection du modèle |

Cette distinction est importante : une méthode **prévue** n'est pas encore un
résultat. Le wiki sera mis à jour après chaque jalon vérifié.

## Questions auxquelles le projet doit répondre

- Quel client devrait être appelé en priorité ?
- Quelle information est réellement disponible avant l'appel ?
- Combien de souscriptions peut-on trouver avec un nombre limité d'appels ?
- Le modèle fait-il mieux qu'une stratégie naïve ?
- Ses résultats restent-ils utiles sur une période plus récente ?
- Quels groupes de clients risquent d'être moins bien servis ?
- Peut-on reproduire le résultat et expliquer comment il a été produit ?

## Règle de maintenance du wiki

Lorsqu'une étape du projet change, il faut mettre à jour :

1. l'état dans cette page ;
2. le chapitre concerné ;
3. les chiffres devenus définitifs ;
4. les limites nouvellement découvertes ;
5. [l'historique](HISTORIQUE.md), avec la date et la raison du changement.

Les décisions détaillées et le journal technique restent disponibles dans
[`SUIVI_PROJET.md`](../SUIVI_PROJET.md). Le plan complet se trouve dans
[`plan_action.md`](../plan_action.md).
