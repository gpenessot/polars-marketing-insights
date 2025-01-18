"""
Script principal pour l'analyse des campagnes marketing.
"""

from pathlib import Path
import polars as pl
import plotly
from rich.console import Console
from rich.progress import Progress
from shutil import copy2
import subprocess

from src.marketing_analysis.analyzer import MarketingAnalyzer
from src.marketing_analysis.utils import format_currency, format_percentage

# Configuration des chemins
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "raw"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_FILE = DATA_DIR / "marketing_campaign_dataset.csv"

# Création des répertoires nécessaires
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Initialisation de la console pour les logs
console = Console()

def generate_report(analyzer, kpis, advanced_analysis, visualizations, output_dir):
    """Génère un rapport Quarto."""
    report_template = """---
title: "Rapport d'Analyse Marketing"
format:
  html:
    code-fold: true
    toc: true
    toc-location: left
    theme: cosmo
    embed-resources: true
---

# Métriques Globales

```{python}
from pathlib import Path
import sys
import polars as pl
from src.marketing_analysis.utils import format_currency, format_percentage

# Chargement des métriques
overall_metrics = kpis["overall_metrics"].to_dicts()[0]

print(f'''
## Performances Globales

- ROI Moyen: {format_percentage(overall_metrics['avg_roi'])}
- Taux de Conversion Moyen: {format_percentage(overall_metrics['avg_conversion_rate'])}
- Dépense Totale: {format_currency(overall_metrics['total_spend'])}
''')
```

# Analyse des Performances

## Performance par Canal

```{python}
import plotly.express as px

channel_data = kpis["channel_performance"]
fig = px.bar(
    channel_data.to_pandas(),
    x="Channel_Used",
    y="avg_roi",
    title="Performance par Canal"
)
fig.show()
```

## Performance par Segment

```{python}
segment_data = kpis["segment_performance"]
fig = px.scatter(
    segment_data.to_pandas(),
    x="avg_conversion",
    y="avg_roi",
    size="campaign_count",
    color="Customer_Segment",
    title="Performance des Segments"
)
fig.show()
```
"""
    
    # Sauvegarde du template Quarto
    template_path = TEMPLATES_DIR / "marketing_report.qmd"
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(report_template)
    
    # Copie vers le dossier reports
    report_path = Path(output_dir) / "report.qmd"
    copy2(template_path, report_path)
    
    # Génération du rapport avec Quarto
    try:
        subprocess.run(
            ["quarto", "render", str(report_path), "--to", "html"],
            check=True,
            capture_output=True
        )
        console.print("[green]✓[/green] Rapport Quarto généré avec succès")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗[/red] Erreur lors de la génération du rapport Quarto : {e}")
        if e.output:
            console.print(e.output.decode())
    except FileNotFoundError:
        console.print("[red]✗[/red] Erreur : Quarto n'est pas installé ou n'est pas dans le PATH")
        console.print("Veuillez installer Quarto : https://quarto.org/docs/get-started/")

def main():
    """Point d'entrée principal du programme."""
    with Progress() as progress:
        # Initialisation de l'analyseur
        task1 = progress.add_task("[cyan]Chargement des données...", total=1)
        analyzer = MarketingAnalyzer(str(DATA_FILE))
        progress.update(task1, advance=1)
        
        # Nettoyage des données
        task2 = progress.add_task("[green]Nettoyage des données...", total=1)
        analyzer.clean_data()
        progress.update(task2, advance=1)
        
        # Calcul des KPIs
        task3 = progress.add_task("[yellow]Calcul des KPIs...", total=1)
        kpis = analyzer.calculate_kpis()
        progress.update(task3, advance=1)
        
        # Analyses avancées
        task4 = progress.add_task("[magenta]Analyses avancées...", total=1)
        advanced_analysis = analyzer.analyze_with_duckdb()
        progress.update(task4, advance=1)
        
        # Création des visualisations
        task5 = progress.add_task("[blue]Création des visualisations...", total=1)
        visualizations = analyzer.create_visualizations()
        progress.update(task5, advance=1)
        
        # Génération du rapport
        task6 = progress.add_task("[red]Génération du rapport...", total=1)
        generate_report(analyzer, kpis, advanced_analysis, visualizations, REPORTS_DIR)
        progress.update(task6, advance=1)
    
    console.print("\n✨ [bold green]Analyse terminée avec succès![/bold green]")
    console.print(f"📊 Le rapport est disponible dans: {REPORTS_DIR}/report.html")

if __name__ == "__main__":
    main()