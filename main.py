"""
Script principal pour l'analyse des campagnes marketing.
"""

from pathlib import Path
import subprocess
from rich.console import Console
from rich.progress import Progress
from shutil import copy2

# Configuration des chemins
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "raw"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_FILE = DATA_DIR / "marketing_campaign_dataset.csv"

# Initialisation de la console pour les logs
console = Console()

def generate_report():
    """Génère le rapport Quarto."""
    # Copie du template vers le dossier reports
    template_path = TEMPLATES_DIR / "marketing_report.qmd"
    report_path = REPORTS_DIR / "report.qmd"
    
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    copy2(template_path, report_path)
    
    # Génération du rapport avec Quarto
    try:
        console.print("Génération du rapport Quarto...")
        result = subprocess.run(
            ["quarto", "render", str(report_path), "--to", "html"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            console.print("[green]✓[/green] Rapport Quarto généré avec succès")
        else:
            console.print("[red]✗[/red] Erreur lors de la génération du rapport:")
            console.print(result.stderr)
    except FileNotFoundError:
        console.print("[red]✗[/red] Quarto n'est pas installé ou n'est pas dans le PATH")
        console.print("Pour installer Quarto : https://quarto.org/docs/get-started/")

def main():
    """Point d'entrée principal du programme."""
    with Progress() as progress:
        # Génération du rapport
        task = progress.add_task("[red]Génération du rapport...", total=1)
        generate_report()
        progress.update(task, advance=1)
    
    console.print(f"\n📊 Le rapport est disponible dans: {REPORTS_DIR}/report.html")

if __name__ == "__main__":
    main()