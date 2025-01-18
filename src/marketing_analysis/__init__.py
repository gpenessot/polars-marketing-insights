"""
Marketing Analysis Package

Ce package fournit des outils pour analyser les performances des campagnes marketing
en utilisant Polars et DuckDB pour un traitement efficace des données.
"""

from .analyzer import MarketingAnalyzer
from .utils import clean_monetary_value, calculate_derived_metrics
from .visualization import create_performance_plots

__version__ = "0.1.0"
__author__ = "Gaël Penessot"

__all__ = [
    "MarketingAnalyzer",
    "clean_monetary_value",
    "calculate_derived_metrics",
    "create_performance_plots"
]