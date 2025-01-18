"""
Fonctions de visualisation pour l'analyse marketing avec Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
from typing import Dict, Any, List, Optional

def create_performance_plots(
    temporal_data: pl.DataFrame,
    channel_data: pl.DataFrame,
    segment_data: pl.DataFrame
) -> Dict[str, go.Figure]:
    """
    Crée l'ensemble des visualisations pour l'analyse des performances.
    
    Args:
        temporal_data: DataFrame des données temporelles
        channel_data: DataFrame des performances par canal
        segment_data: DataFrame des performances par segment
        
    Returns:
        Dict contenant les figures Plotly
    """
    return {
        "temporal_trends": create_temporal_analysis(temporal_data),
        "channel_comparison": create_channel_analysis(channel_data),
        "segment_matrix": create_segment_analysis(segment_data),
        "performance_overview": create_performance_overview(
            temporal_data, channel_data, segment_data
        )
    }

def create_temporal_analysis(df: pl.DataFrame) -> go.Figure:
    """
    Crée une visualisation des tendances temporelles.
    
    Args:
        df: DataFrame contenant les données temporelles
        
    Returns:
        Figure Plotly
    """
    # Création d'un graphique avec axes secondaires
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Ligne pour le ROI
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["avg_roi"],
            name="ROI moyen",
            line=dict(color="#1f77b4", width=2),
            mode="lines"
        ),
        secondary_y=False
    )
    
    # Ligne pour le taux de conversion
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["avg_conversion"],
            name="Taux de conversion",
            line=dict(color="#ff7f0e", width=2),
            mode="lines"
        ),
        secondary_y=True
    )
    
    # Mise en forme
    fig.update_layout(
        title="Évolution temporelle des performances",
        xaxis_title="Date",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Axes
    fig.update_yaxes(title_text="ROI", secondary_y=False)
    fig.update_yaxes(title_text="Taux de conversion", secondary_y=True)
    
    return fig

def create_channel_analysis(df: pl.DataFrame) -> go.Figure:
    """
    Crée une visualisation des performances par canal.
    
    Args:
        df: DataFrame des performances par canal
        
    Returns:
        Figure Plotly
    """
    # Graphique en barres avec indicateurs multiples
    fig = go.Figure()
    
    # Barres pour le ROI
    fig.add_trace(
        go.Bar(
            x=df["Channel_Used"],
            y=df["avg_roi"],
            name="ROI moyen",
            marker_color="#1f77b4"
        )
    )
    
    # Ligne pour l'engagement
    fig.add_trace(
        go.Scatter(
            x=df["Channel_Used"],
            y=df["avg_engagement"],
            name="Score d'engagement",
            mode="lines+markers",
            line=dict(color="#ff7f0e", width=2),
            yaxis="y2"
        )
    )
    
    # Mise en forme
    fig.update_layout(
        title="Performance par canal",
        barmode="group",
        xaxis_title="Canal",
        yaxis_title="ROI moyen",
        yaxis2=dict(
            title="Score d'engagement",
            overlaying="y",
            side="right"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_segment_analysis(df: pl.DataFrame) -> go.Figure:
    """
    Crée une matrice de performance des segments.
    
    Args:
        df: DataFrame des performances par segment
        
    Returns:
        Figure Plotly
    """
    # Création du scatter plot
    fig = px.scatter(
        df.to_pandas(),
        x="avg_conversion",
        y="avg_roi",
        size="campaign_count",
        color="Customer_Segment",
        hover_data=["avg_engagement"],
        title="Matrice de performance des segments"
    )
    
    # Mise en forme
    fig.update_layout(
        xaxis_title="Taux de conversion moyen",
        yaxis_title="ROI moyen",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_performance_overview(
    temporal_data: pl.DataFrame,
    channel_data: pl.DataFrame,
    segment_data: pl.DataFrame
) -> go.Figure:
    """
    Crée un dashboard de synthèse des performances.
    
    Args:
        temporal_data: DataFrame des données temporelles
        channel_data: DataFrame des performances par canal
        segment_data: DataFrame des performances par segment
        
    Returns:
        Figure Plotly
    """
    # Création d'une grille 2x2
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Tendances temporelles",
            "Performance par canal",
            "Performance par segment",
            "Distribution des métriques"
        ),
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Ajout des sous-graphiques
    _add_temporal_subplot(fig, temporal_data, row=1, col=1)
    _add_channel_subplot(fig, channel_data, row=1, col=2)
    _add_segment_subplot(fig, segment_data, row=2, col=1)
    _add_metrics_subplot(fig, temporal_data, row=2, col=2)
    
    # Mise en forme globale
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Synthèse des performances marketing",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def _add_temporal_subplot(
    fig: go.Figure,
    df: pl.DataFrame,
    row: int,
    col: int
) -> None:
    """Ajoute le sous-graphique temporel."""
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["avg_roi"],
            name="ROI",
            line=dict(color="#1f77b4")
        ),
        row=row, col=col, secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["avg_conversion"],
            name="Conversion",
            line=dict(color="#ff7f0e")
        ),
        row=row, col=col, secondary_y=True
    )

def _add_channel_subplot(
    fig: go.Figure,
    df: pl.DataFrame,
    row: int,
    col: int
) -> None:
    """Ajoute le sous-graphique des canaux."""
    fig.add_trace(
        go.Bar(
            x=df["Channel_Used"],
            y=df["avg_roi"],
            name="ROI par canal"
        ),
        row=row, col=col
    )

def _add_segment_subplot(
    fig: go.Figure,
    df: pl.DataFrame,
    row: int,
    col: int
) -> None:
    """Ajoute le sous-graphique des segments."""
    fig.add_trace(
        go.Scatter(
            x=df["avg_conversion"],
            y=df["avg_roi"],
            mode="markers",
            marker=dict(
                size=df["campaign_count"],
                sizeref=2.*max(df["campaign_count"])/(40.**2),
                sizemin=4
            ),
            text=df["Customer_Segment"],
            name="Segments"
        ),
        row=row, col=col
    )

def _add_metrics_subplot(
    fig: go.Figure,
    df: pl.DataFrame,
    row: int,
    col: int
) -> None:
    """Ajoute le sous-graphique des distributions."""
    fig.add_trace(
        go.Box(
            y=df["avg_roi"],
            name="Distribution ROI",
            boxpoints="outliers"
        ),
        row=row, col=col
    )

def create_funnel_analysis(df: pl.DataFrame) -> go.Figure:
    """
    Crée une analyse en entonnoir des conversions.
    
    Args:
        df: DataFrame avec les métriques de conversion
        
    Returns:
        Figure Plotly
    """
    # Calcul des métriques d'entonnoir
    funnel_metrics = [
        ("Impressions", df["Impressions"].sum()),
        ("Clics", df["Clicks"].sum()),
        ("Interactions", (df["Clicks"] * df["Engagement_Score"]/10).sum()),
        ("Conversions", (df["Clicks"] * df["Conversion_Rate"]).sum())
    ]
    
    # Création du graphique en entonnoir
    fig = go.Figure(go.Funnel(
        y=[x[0] for x in funnel_metrics],
        x=[x[1] for x in funnel_metrics],
        textinfo="value+percent initial"
    ))
    
    # Mise en forme
    fig.update_layout(
        title="Analyse en entonnoir des conversions",
        showlegend=False
    )
    
    return fig

def create_heatmap_analysis(
    df: pl.DataFrame,
    metrics: List[str],
    segments: Optional[List[str]] = None
) -> go.Figure:
    """
    Crée une heatmap pour analyser les corrélations entre métriques.
    
    Args:
        df: DataFrame source
        metrics: Liste des métriques à analyser
        segments: Liste optionnelle des segments à inclure
        
    Returns:
        Figure Plotly
    """
    # Filtrage par segment si nécessaire
    if segments:
        df = df.filter(pl.col("Customer_Segment").is_in(segments))
    
    # Calcul des corrélations
    corr_matrix = df.select(metrics).corr()
    
    # Création de la heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=metrics,
        y=metrics,
        colorscale="RdBu",
        zmin=-1,
        zmax=1
    ))
    
    # Mise en forme
    fig.update_layout(
        title="Analyse des corrélations entre métriques",
        xaxis_title="Métriques",
        yaxis_title="Métriques"
    )
    
    return fig