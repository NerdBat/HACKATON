# HACKATON 2025

## Membres :
- Ngy François  
- Theissen Antoine  
- Wahba Angélique  
- Wahba Marie  
- Yelemeu Rick Georges  

## Lien de notre dataset  
https://www.kaggle.com/datasets/tanishqdublish/urban-traffic-density-in-cities  

## Pourquoi ce fichier ??

Nous avons choisi ce dataset car il offre une vision riche et complète de la circulation dans des villes futuristes. Il permet d’analyser en profondeur les interactions entre différents facteurs comme la météo, l’économie, le type de véhicule et les événements aléatoires sur la densité du trafic.  

Ce jeu de données, composé de plus de **1,2 million d’enregistrements**, représente un environnement idéal pour développer des modèles de **prévision de la densité du trafic**, d’**optimisation énergétique** ou encore d’**analyse des comportements de mobilité** dans le contexte des **villes intelligentes**.

---

## Description du dataset

Chaque ligne du fichier CSV correspond à un instantané du trafic dans l’une des six villes fictives. Les principales colonnes sont :

| Colonne | Description |
|----------|--------------|
| **City** | Nom de la ville (ex : *MetropolisX*, *SolarisVille*) |
| **Vehicle Type** | Type de véhicule (ex : *Car*, *Bus*, ...) |
| **Weather Conditions** | Conditions météorologiques (ex : *Clear*, *Rainy*) |
| **Economic Conditions** | Contexte économique (ex : *Booming*, *Recession*) |
| **Day of Week** | Jour de la semaine |
| **Hour of Day** | Heure de la journée |
| **Speed** | Vitesse enregistrée du véhicule |
| **Energy Consumption** | Consommation d’énergie estimée selon le type et la vitesse |
| **Is Peak Hour** | Indique si l’enregistrement correspond à une heure de pointe |
| **Random Event Occurred** | Indique si un événement aléatoire s’est produit (accident, fermeture de route, etc.) |
| **Traffic Density** | Densité du trafic au moment de l’enregistrement |

---

## Objectifs de notre projet

Notre objectif est de :
- **Analyser les patterns de circulation** selon la météo, l’économie et les heures de pointe.  
- **Identifier les facteurs principaux** influençant la densité du trafic.  
- **Prédire la densité du trafic** à l’aide de modèles de Machine Learning.  
- **Explorer des approches de gestion intelligente du trafic** dans des contextes urbains futuristes.  

---

## Potentielles applications

- Développement d’algorithmes de **régulation du trafic autonome**.  
- Étude de l’impact des **véhicules volants** sur la mobilité urbaine.  
- Simulation de **scénarios de planification urbaine** pour des villes du futur.  
- Optimisation de la **consommation énergétique** selon les conditions de circulation.  

---

## Format du fichier

Le dataset est fourni au format **CSV**, facilement exploitable avec des outils de data science tels que **Python (Pandas, Python)**, **SQL**, ou des notebooks interactifs comme **JupyterNoteBook**.  

## Dependance :

- boto3 pour minIO
- Mysql
- Python (pandas, numpy, sqlalchemy, ...)
- Power Bi

## Execution :

Au préalable il faut créer la database sur mysql (dans notre cas on a un utilisateur root en localhost avec comme table : hackaton ).
On éxecute le fichier bronze_silver.py pour amener les données brutes de minIO dans notre base mysql en les nettoyant / standardisant.
Puis le script inject_viz arrange les données pour éviter des transformation dans PowerQuery avant de les rentrer dans une autre table qui sert a alimenter la dataviz. Pour ce qui est du ML on part de la base silver pour transformer toutes les valeurs qui ne sont pas des valeurs numérique en valeur numérique avec le traitement.ipynb afin d'avoir un dataset prêt pour le machine learning. Ensuite on utilise Scikit learn et le modèle RandomForestClassfier pour crée un modèle de machine learning. L'utilisaation de MLFlow permet d'exporter ce modèle et de l'utiliser dans une api web. Nôtre api fonctionne avec MLFlow et FastApi et permet d'exploiter le modèle entrainer avec mlflow.ipynb. Pour utiliser la prédiction on éxecute la commmande *unicorn app:app --reload* pour initialiser le serveur, puis on va à l'adresse suivante : localhost:8000.
