# Marketing Campaign Performance Analysis

Ce projet fournit un framework d'analyse des performances de campagnes marketing en utilisant des technologies modernes comme Polars et DuckDB. Il permet d'analyser en détail les performances des campagnes marketing à travers différents canaux et segments clients.

## 🎯 Fonctionnalités

- Analyse de performance par canal marketing
- Segmentation client et analyse des cohortes
- Calcul des KPIs essentiels (ROI, taux de conversion, engagement)
- Visualisations interactives avec Plotly
- Génération de rapports automatisés avec Quarto

## 🛠️ Technologies Utilisées

- **Polars**: Pour le traitement efficace des données
- **DuckDB**: Pour les requêtes analytiques complexes
- **Plotly**: Pour les visualisations interactives
- **Quarto**: Pour la génération de rapports
- **Rich**: Pour les interfaces en ligne de commande

## 📦 Installation

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/polars-marketing-insights.git
cd polars-marketing-insights
```

2. Créez un environnement virtuel et installez les dépendances :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Installez Quarto :
```bash
# Sur Ubuntu/Debian
wget https://quarto.org/download/latest/quarto-linux-amd64.deb
sudo dpkg -i quarto-linux-amd64.deb

# Sur Windows avec winget
winget install --id RProject.quarto
```

## 📊 Structure du Projet

```
polars-marketing-insights/
│
├── main.py                # Point d'entrée principal
├── requirements.txt       # Dépendances du projet
│
├── data/                 
│   └── raw/           
│       └── marketing_campaign_dataset.csv
│
├── templates/            
│   └── marketing_report.qmd  # Template Quarto
│
├── src/               
│   └── marketing_analysis/
│       ├── __init__.py
│       ├── analyzer.py     # Logique d'analyse
│       ├── utils.py        # Fonctions utilitaires
│       └── visualization.py # Création des graphiques
│
├── notebooks/         
│   ├── 01_data_exploration.ipynb
│   └── 02_marketing_analysis_demo.ipynb
│
└── reports/          # Rapports générés
```

## 🚀 Utilisation

1. Placez vos données marketing dans `data/raw/marketing_campaign_dataset.csv`

2. Exécutez l'analyse :
```bash
python main.py
```

3. Consultez le rapport généré dans `reports/report.html`

## 📝 Format des Données

Le dataset doit contenir les colonnes suivantes :
- Campaign_ID
- Campaign_Type
- Channel_Used
- Target_Audience
- Conversion_Rate
- Acquisition_Cost
- ROI
- Clicks
- Impressions
- Engagement_Score
- Customer_Segment
- Date

## 🔍 Exemple de Rapport

Le rapport généré inclut :
- Vue d'ensemble des performances
- Analyse par canal marketing
- Segmentation client
- Tendances temporelles
- Analyse croisée segments-canaux
- Analyse des cohortes
- Recommandations

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## ✨ Remerciements

Ce projet utilise plusieurs bibliothèques open source remarquables :
- [Polars](https://pola.rs)
- [DuckDB](https://duckdb.org)
- [Plotly](https://plotly.com)
- [Quarto](https://quarto.org)

## ✍️ Auteur

Créé avec ❤️ par [Gaël Penessot](https://www.linkedin.com/in/gael-penessot), auteur de [Business Intelligence with Python](https://amzn.to/42jjs1o)
