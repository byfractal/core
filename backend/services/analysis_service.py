import os
import uuid
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

from backend.services.supabase_service import get_supabase_client
from backend.models.analysis_card import AnalysisCard, AnalysisResponse, SeverityLevel

class AnalysisService:
    def __init__(self):
        self.supabase = get_supabase_client()
        # Tags disponibles pour les insights
        self.available_tags = [
            "High Friction", 
            "Navigation Drop-off", 
            "Low Conversion", 
            "Accessibility Issue",
            "Mobile Usability",
            "Load Performance",
            "Visual Hierarchy",
            "Information Architecture"
        ]
        
        # Modèles de sources pour les insights
        self.available_sources = [
            "Nielsen Norman Group",
            "Lucidpark Research",
            "Baymard Institute",
            "UX Metrics Database",
            "Industry Benchmarks"
        ]
    
    def generate_analysis(self, figma_file_key: str, node_ids: List[str], metrics_data: Dict = None) -> List[AnalysisCard]:
        """
        Génère des cartes d'analyse basées sur les données Figma et les métriques.
        
        Args:
            figma_file_key: La clé du fichier Figma
            node_ids: Liste des IDs de nœuds Figma à analyser
            metrics_data: Données de métriques pour l'analyse
            
        Returns:
            Une liste de cartes d'analyse
        """
        cards = []
        
        # Pour chaque node_id, créez une carte d'analyse avec tous les champs requis
        for i, node_id in enumerate(node_ids):
            # Détermine la sévérité en fonction de valeurs aléatoires (à remplacer par une logique basée sur les données réelles)
            severity_values = list(SeverityLevel)
            severity = random.choice(severity_values)
            
            # Sélectionne aléatoirement 2-3 tags
            tags = random.sample(self.available_tags, k=random.randint(2, 3))
            
            # Sélectionne aléatoirement 1-2 sources
            sources = random.sample(self.available_sources, k=random.randint(1, 2))
            
            # Génère des métriques contextuelles
            benchmark_value = random.randint(40, 90) / 10  # Entre 4.0 et 9.0
            actual_value = benchmark_value * (random.randint(40, 95) / 100)  # Entre 40% et 95% du benchmark
            difference = round(((actual_value / benchmark_value) - 1) * 100)  # Différence en pourcentage
            
            # Calcule l'impact estimé (sera toujours positif en pourcentage)
            impact_value = random.randint(15, 85)
            
            # Génère des métriques de support et un warning message basés sur la sévérité
            supporting_metric = f"CTR = {actual_value:.1f}%, {abs(difference)}% {'below' if difference < 0 else 'above'} benchmark"
            warning_message = f"Potential {abs(difference)}% conversion loss" if difference < 0 else f"Underperforming by {abs(difference)}%"
            
            # Structure des données contextuelles
            contextual_data = {
                "benchmark": f"{benchmark_value:.1f}%",
                "industry_average": f"{benchmark_value * 0.9:.1f}%",
                "users_affected": random.randint(500, 5000),
                "page_type": "Product Page" if i % 2 == 0 else "Checkout Flow",
                "device_breakdown": {
                    "mobile": f"{random.randint(50, 80)}%",
                    "desktop": f"{random.randint(20, 50)}%"
                }
            }
            
            # Générateur d'exemples - serait remplacé par une vraie analyse
            title_prefix = "Optimization" if i == 0 else f"Optimization #{i+1}"
            card = AnalysisCard(
                id=str(uuid.uuid4()),
                figma_file_key=figma_file_key,
                node_id=node_id,
                title=f"{title_prefix}: {random.choice(['Improve visibility', 'Enhance contrast', 'Simplify navigation', 'Reduce cognitive load'])}",
                description=f"Users are experiencing difficulty with this component, resulting in {difference}% {'lower' if difference < 0 else 'higher'} engagement.",
                root_cause=f"The {random.choice(['button', 'form', 'navigation', 'layout'])} doesn't follow established UX patterns, creating cognitive friction.",
                supporting_metric=supporting_metric,
                contextual_data=contextual_data,
                warning_message=warning_message,
                recommended_fix=f"Update the {random.choice(['color contrast', 'button placement', 'information hierarchy', 'visual feedback'])} to align with best practices.",
                impact_estimate=f"+{impact_value}% potential improvement in conversion",
                sources=sources,
                severity=severity,
                tags=tags,
                created_at=datetime.now().isoformat(),
                is_new=True,
                optimization_number=i+1
            )
            cards.append(card)
            
            # Enregistrer la carte dans Supabase
            self._save_card_to_database(card)
        
        return cards
    
    def _save_card_to_database(self, card: AnalysisCard) -> Dict:
        """
        Enregistre une carte d'analyse dans la base de données Supabase.
        
        Args:
            card: La carte d'analyse à enregistrer
            
        Returns:
            Les données de la carte enregistrée
        """
        # Convertir la carte en dictionnaire pour l'insertion
        card_dict = {
            "id": card.id,
            "figma_file_key": card.figma_file_key,
            "node_id": card.node_id,
            "title": card.title,
            "description": card.description,
            "root_cause": card.root_cause,
            "supporting_metric": card.supporting_metric,
            "contextual_data": json.dumps(card.contextual_data),  # Convertir en JSON
            "warning_message": card.warning_message,
            "recommended_fix": card.recommended_fix,
            "impact_estimate": card.impact_estimate,
            "sources": card.sources,
            "severity": card.severity.value,  # Convertir l'enum en string
            "tags": card.tags,
            "created_at": card.created_at,
            "is_new": card.is_new,
            "optimization_number": card.optimization_number
        }
        
        # Insérer dans Supabase
        result = self.supabase.table('analysis_cards').insert(card_dict).execute()
        
        # Retourner les données de la carte enregistrée
        return result.data[0] if result and result.data else {}
    
    def get_cards_by_file_key(self, figma_file_key: str) -> List[AnalysisCard]:
        """
        Récupère les cartes d'analyse pour un fichier Figma spécifique.
        
        Args:
            figma_file_key: La clé du fichier Figma
            
        Returns:
            Une liste de cartes d'analyse
        """
        # Récupérer les cartes depuis Supabase
        result = self.supabase.table('analysis_cards').select('*').eq('figma_file_key', figma_file_key).execute()
        
        # Convertir les données en objets AnalysisCard
        cards = []
        if result and result.data:
            for card_data in result.data:
                # Convertir le string de sévérité en enum
                severity = SeverityLevel(card_data.get('severity', 'NEEDS_IMPROVEMENT'))
                
                # Convertir contextual_data de JSON à dictionnaire
                contextual_data = {}
                if card_data.get('contextual_data'):
                    try:
                        contextual_data = json.loads(card_data.get('contextual_data'))
                    except json.JSONDecodeError:
                        contextual_data = {}
                
                card = AnalysisCard(
                    id=card_data.get('id'),
                    figma_file_key=card_data.get('figma_file_key'),
                    node_id=card_data.get('node_id'),
                    title=card_data.get('title'),
                    description=card_data.get('description'),
                    root_cause=card_data.get('root_cause', ''),
                    supporting_metric=card_data.get('supporting_metric', ''),
                    contextual_data=contextual_data,
                    warning_message=card_data.get('warning_message', ''),
                    recommended_fix=card_data.get('recommended_fix', ''),
                    impact_estimate=card_data.get('impact_estimate', ''),
                    sources=card_data.get('sources', []),
                    severity=severity,
                    tags=card_data.get('tags', []),
                    created_at=card_data.get('created_at'),
                    is_new=card_data.get('is_new', False),
                    optimization_number=card_data.get('optimization_number')
                )
                cards.append(card)
        
        return cards
    
    def filter_cards_by_severity(self, cards: List[AnalysisCard], severity_levels: List[SeverityLevel]) -> List[AnalysisCard]:
        """
        Filtre les cartes par niveau de sévérité.
        
        Args:
            cards: Liste de cartes à filtrer
            severity_levels: Liste des niveaux de sévérité à conserver
            
        Returns:
            Liste filtrée de cartes
        """
        return [card for card in cards if card.severity in severity_levels]
    
    def filter_cards_by_tags(self, cards: List[AnalysisCard], tags: List[str]) -> List[AnalysisCard]:
        """
        Filtre les cartes par tags.
        
        Args:
            cards: Liste de cartes à filtrer
            tags: Liste des tags à rechercher
            
        Returns:
            Liste filtrée de cartes
        """
        return [card for card in cards if any(tag in card.tags for tag in tags)]
    
    def mark_card_as_viewed(self, card_id: str) -> bool:
        """
        Marque une carte comme déjà vue (désactive l'animation "shine").
        
        Args:
            card_id: ID de la carte
            
        Returns:
            Succès de l'opération
        """
        result = self.supabase.table('analysis_cards').update({"is_new": False}).eq('id', card_id).execute()
        return bool(result and result.data)
    
    def get_paginated_response(
        self, 
        cards: List[AnalysisCard], 
        page: int = 1, 
        per_page: int = 10,
        filter_tags: Optional[List[str]] = None,
        filter_severity: Optional[List[SeverityLevel]] = None,
        sort_by: Optional[str] = None
    ) -> AnalysisResponse:
        """
        Crée une réponse paginée avec les cartes d'analyse.
        
        Args:
            cards: Liste de cartes à paginer
            page: Numéro de page (commence à 1)
            per_page: Nombre d'éléments par page
            filter_tags: Filtrer par tags
            filter_severity: Filtrer par sévérité
            sort_by: Critère de tri
            
        Returns:
            Réponse paginée
        """
        # Filtrer par tags si spécifié
        if filter_tags:
            cards = self.filter_cards_by_tags(cards, filter_tags)
        
        # Filtrer par sévérité si spécifié
        if filter_severity:
            cards = self.filter_cards_by_severity(cards, filter_severity)
        
        # Trier si spécifié
        if sort_by:
            if sort_by == "severity":
                # Les sévérités plus critiques d'abord
                severity_order = {
                    SeverityLevel.MINOR: 0,
                    SeverityLevel.NEEDS_IMPROVEMENT: 1,
                    SeverityLevel.UNDERPERFORMING: 2,
                    SeverityLevel.CRITICAL: 3
                }
                cards.sort(key=lambda card: severity_order.get(card.severity, 0), reverse=True)
            elif sort_by == "created_at":
                # Les plus récentes d'abord
                cards.sort(key=lambda card: card.created_at, reverse=True)
            elif sort_by == "optimization_number":
                # Trier par numéro d'optimisation
                cards.sort(key=lambda card: card.optimization_number or 999)
        
        # Calculer la pagination
        total_cards = len(cards)
        total_pages = (total_cards + per_page - 1) // per_page if total_cards > 0 else 1
        
        # Limiter la page à la plage valide
        page = max(1, min(page, total_pages))
        
        # Extraire la page demandée
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_cards = cards[start_idx:end_idx]
        
        # Créer la réponse
        return AnalysisResponse(
            cards=page_cards,
            page=page,
            per_page=per_page,
            total=total_cards,
            total_pages=total_pages
        )
    
    def save_cards_to_cache(self, cards: List[AnalysisCard], figma_file_key: str) -> str:
        """
        Sauvegarde les cartes dans un fichier cache (pour démonstration).
        Dans un cas réel, vous utiliseriez une base de données ou un cache distribué.
        
        Args:
            cards: Liste de cartes à sauvegarder
            figma_file_key: Clé du fichier Figma
            
        Returns:
            Chemin du fichier cache
        """
        # Cette fonction est conservée pour compatibilité, mais nous utilisons Supabase désormais
        # Les cartes sont déjà sauvegardées dans Supabase lors de leur génération
        return f"Cache for {figma_file_key} with {len(cards)} cards" 