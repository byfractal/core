from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Niveaux de sévérité pour les cartes d'analyse."""
    MINOR = "MINOR"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    UNDERPERFORMING = "UNDERPERFORMING"
    CRITICAL = "CRITICAL_UX_DEBT"


class AnalysisCard(BaseModel):
    """Modèle de carte d'analyse UX/UI."""
    id: str
    figma_file_key: str
    node_id: Optional[str] = None
    title: str
    description: str
    root_cause: str = Field(..., description="Explication UX simple et directe")
    supporting_metric: str = Field(..., description="Métrique principale supportant l'analyse (ex: 'CTR = 4.2%, 60% below benchmark')")
    contextual_data: Dict[str, Any] = Field(default_factory=dict, description="Données contextuelles incluant benchmarks, type de page, nombre d'utilisateurs")
    warning_message: str = Field(..., description="Impact UX explicite (ex: 'Potential 60% conversion loss')")
    recommended_fix: str = Field(..., description="Action claire et basée sur preuves")
    impact_estimate: str = Field(..., description="Projection d'amélioration précise (%)")
    sources: List[str] = Field(default_factory=list, description="Sources comme NN Group, Lucidpark")
    severity: SeverityLevel = SeverityLevel.NEEDS_IMPROVEMENT
    tags: List[str] = Field(default_factory=list, description="Classifications filtrables des insights")
    created_at: Optional[str] = None
    is_new: bool = Field(default=True, description="Si l'insight est affiché pour la première fois")
    optimization_number: Optional[int] = None


class AnalysisRequest(BaseModel):
    """Modèle de requête pour générer des analyses."""
    figma_file_key: str
    node_ids: List[str]
    data_sources: Optional[List[str]] = Field(default_factory=list)
    date_range: Optional[List[str]] = None
    api_keys: Optional[dict] = None


class AnalysisResponse(BaseModel):
    """Modèle de réponse pour les analyses paginées."""
    cards: List[AnalysisCard]
    page: int = 1
    per_page: int = 10
    total: int = 0
    total_pages: int = 0 