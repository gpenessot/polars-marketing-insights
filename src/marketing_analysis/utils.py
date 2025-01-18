"""
Fonctions utilitaires pour l'analyse marketing.
"""

import polars as pl
from typing import Any, List, Dict, Union, Tuple
import numpy as np
from datetime import datetime, date

def clean_monetary_value(df: pl.DataFrame, column: str) -> pl.DataFrame:
    """
    Nettoie une colonne contenant des valeurs monétaires.
    Gère à la fois les formats avec et sans décimales ($1234.00 et $1234).
    
    Args:
        df: DataFrame source
        column: Nom de la colonne à nettoyer
        
    Returns:
        DataFrame avec la colonne nettoyée
    """
    return df.with_columns([
        pl.col(column)
            .str.strip_chars()         # Supprime les espaces avec l'API Polars correcte
            .str.replace(r"\$", "")    # Supprime le symbole dollar
            .str.replace(r",", "")     # Supprime les virgules
            .cast(pl.Float64)          # Convertit en Float64
            .alias(column)
    ])

def calculate_derived_metrics(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcule les métriques dérivées pour l'analyse marketing.
    
    Args:
        df: DataFrame source
        
    Returns:
        DataFrame avec les métriques dérivées ajoutées
    """
    derived = df.with_columns([
        # CTR (Click-Through Rate)
        (pl.col("Clicks") / pl.col("Impressions")).alias("CTR"),
        
        # CPC (Cost per Click)
        (pl.col("Acquisition_Cost") / pl.col("Clicks")).alias("CPC"),
        
        # CPM (Cost per Mille)
        (pl.col("Acquisition_Cost") / pl.col("Impressions") * 1000).alias("CPM"),
        
        # Conversions totales
        (pl.col("Conversion_Rate") * pl.col("Clicks")).alias("Total_Conversions"),
        
        # CPA (Cost per Acquisition)
        (pl.col("Acquisition_Cost") / (pl.col("Conversion_Rate") * pl.col("Clicks")))
            .alias("CPA")
    ])
    
    # Ajout des catégories de performance
    return add_performance_categories(derived)

def add_performance_categories(df: pl.DataFrame) -> pl.DataFrame:
    """
    Ajoute des catégories de performance basées sur différentes métriques.
    
    Args:
        df: DataFrame source
        
    Returns:
        DataFrame avec les catégories de performance ajoutées
    """
    return df.with_columns([
        # Catégorie ROI
        pl.when(pl.col("ROI") >= 7)
          .then(pl.lit("Haute performance"))
          .when(pl.col("ROI") >= 5)
          .then(pl.lit("Performance moyenne"))
          .otherwise(pl.lit("Basse performance"))
          .alias("ROI_Category"),
          
        # Catégorie Engagement
        pl.when(pl.col("Engagement_Score") >= 8)
          .then(pl.lit("Très engageant"))
          .when(pl.col("Engagement_Score") >= 6)
          .then(pl.lit("Engageant"))
          .otherwise(pl.lit("Peu engageant"))
          .alias("Engagement_Category"),
          
        # Catégorie Conversion
        pl.when(pl.col("Conversion_Rate") >= 0.1)
          .then(pl.lit("Haute conversion"))
          .when(pl.col("Conversion_Rate") >= 0.05)
          .then(pl.lit("Conversion moyenne"))
          .otherwise(pl.lit("Basse conversion"))
          .alias("Conversion_Category")
    ])


def calculate_growth_metrics(df: pl.DataFrame) -> Dict[str, float]:
    """
    Calcule les métriques de croissance entre périodes.
    
    Args:
        df: DataFrame contenant les données temporelles
        
    Returns:
        Dict contenant les différentes métriques de croissance
    """
    # Calcul des moyennes par période
    period_metrics = (
        df.groupby("Date")
        .agg([
            pl.col("ROI").mean().alias("avg_roi"),
            pl.col("Conversion_Rate").mean().alias("avg_conversion"),
            pl.col("Acquisition_Cost").sum().alias("total_spend")
        ])
        .sort("Date")
    )
    
    # Calcul des variations
    roi_growth = calculate_percentage_change(
        period_metrics["avg_roi"].to_list()
    )
    
    conversion_growth = calculate_percentage_change(
        period_metrics["avg_conversion"].to_list()
    )
    
    spend_growth = calculate_percentage_change(
        period_metrics["total_spend"].to_list()
    )
    
    return {
        "roi_growth": roi_growth,
        "conversion_growth": conversion_growth,
        "spend_growth": spend_growth
    }

def calculate_percentage_change(values: List[float]) -> float:
    """
    Calcule la variation en pourcentage entre la première et la dernière valeur.
    
    Args:
        values: Liste des valeurs
        
    Returns:
        Pourcentage de variation
    """
    if not values or len(values) < 2:
        return 0.0
    
    start_value = values[0]
    end_value = values[-1]
    
    if start_value == 0:
        return 0.0
        
    return ((end_value - start_value) / start_value) * 100

def calculate_moving_averages(df: pl.DataFrame, 
                            metric: str, 
                            windows: List[int] = [7, 30]) -> pl.DataFrame:
    """
    Calcule les moyennes mobiles pour une métrique donnée.
    
    Args:
        df: DataFrame source
        metric: Nom de la colonne métrique
        windows: Liste des fenêtres pour les moyennes mobiles
        
    Returns:
        DataFrame avec les moyennes mobiles ajoutées
    """
    result = df.sort("Date")
    
    for window in windows:
        result = result.with_columns([
            pl.col(metric)
              .rolling_mean(window_size=window)
              .alias(f"{metric}_MA_{window}")
        ])
    
    return result

def segment_analysis(df: pl.DataFrame) -> Dict[str, pl.DataFrame]:
    """
    Effectue une analyse détaillée par segment.
    
    Args:
        df: DataFrame source
        
    Returns:
        Dict contenant différentes analyses par segment
    """
    # Performance par segment
    segment_performance = (
        df.groupby("Customer_Segment")
        .agg([
            pl.col("ROI").mean().alias("avg_roi"),
            pl.col("Conversion_Rate").mean().alias("avg_conversion"),
            pl.col("Engagement_Score").mean().alias("avg_engagement"),
            pl.col("Acquisition_Cost").sum().alias("total_spend"),
            pl.count().alias("campaign_count")
        ])
        .sort("avg_roi", descending=True)
    )
    
    # Performance segment x canal
    segment_channel = (
        df.groupby(["Customer_Segment", "Channel_Used"])
        .agg([
            pl.col("ROI").mean().alias("avg_roi"),
            pl.col("Conversion_Rate").mean().alias("avg_conversion"),
            pl.count().alias("campaign_count")
        ])
        .sort(["Customer_Segment", "avg_roi"], descending=[False, True])
    )
    
    return {
        "segment_performance": segment_performance,
        "segment_channel": segment_channel
    }

def calculate_efficiency_metrics(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcule les métriques d'efficacité des campagnes.
    
    Args:
        df: DataFrame source
        
    Returns:
        DataFrame avec les métriques d'efficacité ajoutées
    """
    return df.with_columns([
        # ROAS (Return on Ad Spend)
        (pl.col("ROI") * pl.col("Acquisition_Cost") / pl.col("Acquisition_Cost"))
            .alias("ROAS"),
        
        # Efficacité du budget
        (pl.col("Total_Conversions") / pl.col("Acquisition_Cost"))
            .alias("Cost_Efficiency"),
            
        # Score d'efficacité global
        (
            pl.col("ROI") * 0.4 +
            pl.col("Conversion_Rate") * 0.3 +
            pl.col("CTR") * 0.2 +
            (pl.col("Engagement_Score") / 10) * 0.1
        ).alias("Efficiency_Score")
    ])

def format_currency(value: float) -> str:
    """
    Formate une valeur en format monétaire.
    
    Args:
        value: Valeur à formater
        
    Returns:
        Chaîne formatée
    """
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """
    Formate une valeur en pourcentage.
    
    Args:
        value: Valeur à formater
        
    Returns:
        Chaîne formatée
    """
    return f"{value:.2f}%"