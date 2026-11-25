# SysWatch-API

## Présentation

SysWatch-API est un projet de supervision système développé en Python. Il permet de collecter et de surveiller les ressources d'un ordinateur, de contrôler la disponibilité de services et de visualiser les données avec Grafana.

## Fonctionnalités

- Collecte des métriques système : CPU, RAM et disques.
- Surveillance des processus : consommation CPU et mémoire.
- Contrôle de disponibilité HTTP et TCP.
- Vérification de la date d'expiration des certificats SSL.
- Détection des dépassements de seuils.
- Détection des augmentations continues de mémoire sur 10 relevés.
- Enregistrement des incidents dans une base SQLite.
- Calcul du taux de disponibilité des services (SLA).
- Visualisation des métriques avec Grafana.

## Technologies utilisées

- Python : Développement de l'agent et des collecteurs
- SQLite : Stockage des données
- Grafana : Visualisation et tableaux de bord
- psutil : Collecte des métriques système et processus
- Git / GitHub : Gestion de versions et hébergement du projet

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/akichanmano00-jpg/SysWatch-API.git
cd SysWatch-API
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Lancement

Démarrer la supervision :

```bash
python main.py
```

Le programme collecte les données à intervalles réguliers et les enregistre dans la base SQLite.

Pour arrêter la supervision : `Ctrl + C`.

## Base de données

Les données sont enregistrées dans `database/syswatch.db`.

Les principales tables sont :
- `host_metrics`
- `disk_partitions`
- `process_metrics`
- `service_health`
- `system_incidents`

## Visualisation

Le projet utilise Grafana avec une source de données SQLite pour afficher les métriques et l'historique des incidents.

## Auteur

Projet réalisé dans le cadre d'un travail de formation.