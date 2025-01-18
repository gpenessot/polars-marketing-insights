"""
Module principal pour l'analyse des campagnes marketing.
"""

import polars as pl
import duckdb
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime

from .utils import clean_monetary_value, calculate_derived_metrics, format_percentage, format_currency
from .visualization import create_performance_plots

class MarketingAnalyzer:
    """
    Classe principale pour l'analyse des campagnes marketing.
    Utilise Polars pour le traitement des données et DuckDB pour les requêtes complexes.
    """
    
    def __init__(self, data_path: str):
        """
        Initialise l'analyseur avec le chemin vers les données.
        
        Args:
            data_path: Chemin vers le fichier CSV des données marketing
        """
        self.data_path = Path(data_path)
        self.df = None
        self.duckdb_conn = duckdb.connect(':memory:')
        self._load_data()
    
    def _load_data(self) -> None:
        """Charge les données initiales depuis le fichier CSV."""
        try:
            self.df = pl.read_csv(self.data_path)
            print(f"Données chargées avec succès: {len(self.df)} lignes")
        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement des données: {str(e)}")

    def clean_data(self) -> pl.DataFrame:
        """
        Nettoie et prépare les données marketing pour l'analyse.
        
        Returns:
            DataFrame Polars nettoyé
        """
        if self.df is None:
            raise ValueError("Aucune donnée n'a été chargée")
        
        try:
            # Nettoyage monétaire et conversion des types
            self.df = clean_monetary_value(self.df, "Acquisition_Cost")
            
            # Calcul des métriques dérivées
            self.df = calculate_derived_metrics(self.df)
            
            # Conversion des dates
            self.df = self.df.with_columns(
                pl.col("Date").str.strptime(pl.Date, format="%Y-%m-%d")
            )
            
            return self.df
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors du nettoyage des données: {str(e)}")

    def calculate_kpis(self) -> Dict[str, Any]:
        """
        Calcule les KPIs essentiels des campagnes marketing.
        
        Returns:
            Dict contenant les différents KPIs calculés
        """
        if self.df is None:
            raise ValueError("Aucune donnée n'a été chargée")

        try:
            # Performance globale
            overall_metrics = self._calculate_global_metrics()
            
            # Performances par dimensions
            channel_perf = self._analyze_channel_performance()
            segment_perf = self._analyze_segment_performance()
            temporal_perf = self._analyze_temporal_performance()
            
            return {
                "overall_metrics": overall_metrics,
                "channel_performance": channel_perf,
                "segment_performance": segment_perf,
                "temporal_analysis": temporal_perf
            }
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors du calcul des KPIs: {str(e)}")

    def _calculate_global_metrics(self) -> pl.DataFrame:
        """Calcule les métriques globales."""
        return self.df.select([
            pl.col("Conversion_Rate").mean().alias("avg_conversion_rate"),
            pl.col("ROI").mean().alias("avg_roi"),
            pl.col("Acquisition_Cost").sum().alias("total_spend"),
            pl.col("CTR").mean().alias("avg_ctr"),
            pl.col("Engagement_Score").mean().alias("avg_engagement")
        ])

    def _analyze_channel_performance(self) -> pl.DataFrame:
        """Analyse la performance par canal."""
        return (
            self.df.group_by("Channel_Used")
            .agg([
                pl.col("Conversion_Rate").mean().alias("avg_conversion"),
                pl.col("ROI").mean().alias("avg_roi"),
                pl.count().alias("campaign_count"),
                pl.col("Engagement_Score").mean().alias("avg_engagement"),
                pl.col("Acquisition_Cost").sum().alias("total_cost")
            ])
            .sort("avg_roi", descending=True)
        )

    def _analyze_segment_performance(self) -> pl.DataFrame:
        """Analyse la performance par segment client."""
        return (
            self.df.group_by("Customer_Segment")
            .agg([
                pl.col("Conversion_Rate").mean().alias("avg_conversion"),
                pl.col("ROI").mean().alias("avg_roi"),
                pl.col("Engagement_Score").mean().alias("avg_engagement"),
                pl.count().alias("campaign_count")
            ])
            .sort("avg_roi", descending=True)
        )

    def _analyze_temporal_performance(self) -> pl.DataFrame:
        """Analyse la performance temporelle."""
        return (
            self.df.group_by("Date")
            .agg([
                pl.col("ROI").mean().alias("avg_roi"),
                pl.col("Conversion_Rate").mean().alias("avg_conversion"),
                pl.col("Clicks").sum().alias("total_clicks"),
                pl.col("Acquisition_Cost").sum().alias("daily_spend")
            ])
            .sort("Date")
        )

    def analyze_with_duckdb(self) -> Dict[str, pl.DataFrame]:
        """
        Effectue des analyses avancées avec DuckDB.
        
        Returns:
            Dict contenant les résultats des analyses DuckDB
        """
        try:
            # Enregistrement des données dans DuckDB
            self.duckdb_conn.register("marketing_data", self.df.to_pandas())
            
            # Analyses avancées
            segment_channel = self._analyze_segment_channel_performance()
            cohort = self._analyze_cohorts()
            
            return {
                "segment_channel_analysis": segment_channel,
                "cohort_analysis": cohort
            }
            
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'analyse DuckDB: {str(e)}")

    def _analyze_segment_channel_performance(self) -> pl.DataFrame:
        """Analyse croisée segments/canaux avec DuckDB."""
        query = """
        SELECT 
            Customer_Segment,
            Channel_Used,
            AVG(Conversion_Rate) as avg_conversion,
            AVG(ROI) as avg_roi,
            COUNT(*) as campaign_count,
            SUM(Acquisition_Cost) as total_cost
        FROM marketing_data
        GROUP BY Customer_Segment, Channel_Used
        HAVING campaign_count >= 10
        ORDER BY avg_roi DESC
        """
        return pl.from_pandas(self.duckdb_conn.execute(query).df())

    def _analyze_cohorts(self) -> pl.DataFrame:
        """Analyse des cohortes avec DuckDB."""
        query = """
        SELECT 
            DATE_TRUNC('month', Date) as cohort_month,
            Customer_Segment,
            COUNT(DISTINCT Campaign_ID) as campaigns,
            AVG(ROI) as avg_roi,
            AVG(Conversion_Rate) as avg_conversion
        FROM marketing_data
        GROUP BY 1, 2
        ORDER BY 1, 2
        """
        return pl.from_pandas(self.duckdb_conn.execute(query).df())
    
    def create_visualizations(self) -> Dict[str, Any]:
            """
            Crée toutes les visualisations pour l'analyse.
            
            Returns:
                Dict contenant les différentes visualisations
            """
            if self.df is None:
                raise ValueError("Aucune donnée n'a été chargée")

            try:
                # On récupère d'abord les KPIs nécessaires
                kpis = self.calculate_kpis()
                
                # On utilise la fonction de visualization.py
                return create_performance_plots(
                    kpis["temporal_analysis"],
                    kpis["channel_performance"],
                    kpis["segment_performance"]
                )
                
            except Exception as e:
                raise RuntimeError(f"Erreur lors de la création des visualisations: {str(e)}")

    def generate_report(analyzer, kpis, advanced_analysis, visualizations, output_dir):
        """Génère un rapport complet au format HTML."""
        report_path = Path(output_dir) / "report.html"
        
        # Extraction des métriques clés
        overall_metrics = kpis["overall_metrics"].to_dicts()[0]
        top_channels = kpis["channel_performance"].head(3).to_dicts()
        top_segments = kpis["segment_performance"].head(3).to_dicts()
        
        # Création du contenu HTML avec iframes pour les visualizations
        html_content = f"""
        <html>
        <head>
            <title>Rapport d'Analyse Marketing</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <style>
                iframe {{
                    width: 100%;
                    height: 600px;
                    border: none;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
            </style>
        </head>
        <body class="bg-gray-100 p-8">
            <div class="max-w-7xl mx-auto">
                <h1 class="text-3xl font-bold mb-8">Rapport d'Analyse Marketing</h1>
                
                <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 class="text-xl font-semibold mb-4">Métriques Globales</h2>
                    <div class="grid grid-cols-3 gap-4">
                        <div class="p-4 bg-blue-50 rounded">
                            <p class="text-sm text-gray-600">ROI Moyen</p>
                            <p class="text-2xl font-bold">{format_percentage(overall_metrics["avg_roi"])}</p>
                        </div>
                        <div class="p-4 bg-green-50 rounded">
                            <p class="text-sm text-gray-600">Taux de Conversion Moyen</p>
                            <p class="text-2xl font-bold">{format_percentage(overall_metrics["avg_conversion_rate"])}</p>
                        </div>
                        <div class="p-4 bg-purple-50 rounded">
                            <p class="text-sm text-gray-600">Dépense Totale</p>
                            <p class="text-2xl font-bold">{format_currency(overall_metrics["total_spend"])}</p>
                        </div>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-8 mb-8">
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">Top Canaux</h2>
                        <iframe src="visualizations/channel_comparison.html"></iframe>
                    </div>
                    <div class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-xl font-semibold mb-4">Top Segments</h2>
                        <iframe src="visualizations/segment_matrix.html"></iframe>
                    </div>
                </div>
                
                <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 class="text-xl font-semibold mb-4">Tendances Temporelles</h2>
                    <iframe src="visualizations/temporal_trends.html"></iframe>
                </div>

                <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 class="text-xl font-semibold mb-4">Vue d'Ensemble des Performances</h2>
                    <iframe src="visualizations/performance_overview.html"></iframe>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Sauvegarde du rapport
        report_path.write_text(html_content)