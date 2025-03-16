"""
Ce module gère l'intégration avec l'API Code.to.Design pour transformer
les recommandations de design en composants Figma manipulables.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# Importation du module de recommandations pour accéder au format des recommandations
from models.design_recommendations import DesignRecommendationChain

class CodeToDesignClient:
    """
    Client pour interagir avec l'API Code.to.Design.
    Permet de transformer les recommandations de design en composants Figma.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le client Code.to.Design avec une clé API.
        
        Args:
            api_key (str, optional): Clé API pour Code.to.Design.
                                     Si non fournie, utilise la variable d'environnement.
        """
        self.api_key = api_key or os.getenv("CODETODESIGN_API_KEY")
        self.api_url = os.getenv("CODETODESIGN_API_URL", "https://api.code.to.design")
        
        if not self.api_key:
            raise ValueError("Code.to.Design API key is required. Set CODETODESIGN_API_KEY environment variable.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_component(self, component_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un composant Figma à partir d'une spécification.
        
        Args:
            component_spec (Dict): Spécification détaillée du composant à générer
            
        Returns:
            Dict: Informations sur le composant généré, y compris l'URL Figma
        """
        endpoint = f"{self.api_url}/components/generate"
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=component_spec
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error generating component: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            return {"error": str(e)}
    
    def transform_recommendations_to_components(
        self, 
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transforme les recommandations de design en composants Figma.
        
        Args:
            recommendations (Dict): Recommandations générées par DesignRecommendationChain
            
        Returns:
            Dict: Informations sur les composants générés, organisés par recommandation
        """
        components_result = {
            "page_id": recommendations.get("page_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "components": []
        }
        
        # Parcourir chaque recommandation
        for rec in recommendations.get("recommendations", []):
            # Transformer la recommandation en spécification de composant
            component_spec = self._recommendation_to_component_spec(rec)
            
            # Générer le composant
            component_result = self.generate_component(component_spec)
            
            # Ajouter le résultat
            components_result["components"].append({
                "recommendation_title": rec.get("title"),
                "component_result": component_result,
                "priority": rec.get("priority", "medium")
            })
        
        # Ajouter des notes d'implémentation générales
        components_result["implementation_notes"] = recommendations.get("implementation_notes", "")
        
        return components_result
    
    def _recommendation_to_component_spec(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforme une recommandation en spécification de composant pour l'API Code.to.Design.
        
        Args:
            recommendation (Dict): Recommandation individuelle
            
        Returns:
            Dict: Spécification du composant pour l'API Code.to.Design
        """
        # Extraire les informations pertinentes de la recommandation
        component_type = recommendation.get("component", "Generic")
        title = recommendation.get("title", "Unnamed Component")
        description = recommendation.get("description", "")
        before_state = recommendation.get("before_after", {}).get("before", "")
        after_state = recommendation.get("before_after", {}).get("after", "")
        
        # Construire une description technique pour le composant
        technical_description = f"""
        Component: {component_type}
        Change: {description}
        From: {before_state}
        To: {after_state}
        """
        
        # Construire la spécification du composant
        return {
            "name": title,
            "componentType": self._map_component_type(component_type),
            "description": technical_description,
            "style": {
                "priority": recommendation.get("priority", "medium")
            },
            "content": {
                "before": before_state,
                "after": after_state
            }
        }
    
    def _map_component_type(self, component_type: str) -> str:
        """
        Mappe les types de composants de nos recommandations aux types 
        supportés par Code.to.Design.
        
        Args:
            component_type (str): Type de composant dans la recommandation
            
        Returns:
            str: Type de composant equivalent dans Code.to.Design
        """
        # Mapping entre nos types de composants et ceux de Code.to.Design
        mapping = {
            "Button": "button",
            "Form": "form",
            "Input": "input",
            "Dropdown": "dropdown",
            "Menu": "menu",
            "Card": "card",
            "Modal": "modal",
            "Navbar": "navigation",
            "Sidebar": "sidebar",
            "Header": "header",
            "Footer": "footer",
            "Table": "table",
            "List": "list",
            "Checkbox": "checkbox",
            "Radio": "radio",
            "Toggle": "toggle",
        }
        
        # Retourner le type mappé ou "generic" par défaut
        return mapping.get(component_type, "generic")

class FigmaLayoutGenerator:
    """
    Générateur de layouts Figma basé sur les recommandations de design.
    Utilise Code.to.Design pour créer des composants Figma manipulables.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le générateur de layouts.
        
        Args:
            api_key (str, optional): Clé API pour Code.to.Design.
                                     Si non fournie, utilise la variable d'environnement.
        """
        self.code_to_design = CodeToDesignClient(api_key)
        self.recommendation_chain = DesignRecommendationChain()
    
    def generate_layout_from_analysis(
        self, 
        analysis_summary: Dict[str, Any],
        page_id: str
    ) -> Dict[str, Any]:
        """
        Génère un layout Figma à partir d'une analyse de feedback.
        
        Args:
            analysis_summary (Dict): Résumé de l'analyse de feedback
            page_id (str): Identifiant de la page analysée
            
        Returns:
            Dict: Informations sur le layout généré, y compris les composants Figma
        """
        # Générer des recommandations à partir de l'analyse
        recommendations = self.recommendation_chain.generate_recommendations(
            analysis_summary,
            page_id
        )
        
        # Transformer les recommandations en composants Figma
        return self.generate_layout_from_recommendations(recommendations)
    
    def generate_layout_from_recommendations(
        self, 
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un layout Figma à partir de recommandations existantes.
        
        Args:
            recommendations (Dict): Recommandations générées précédemment
            
        Returns:
            Dict: Informations sur le layout généré, y compris les composants Figma
        """
        # Transformer les recommandations en composants Figma
        components_result = self.code_to_design.transform_recommendations_to_components(recommendations)
        
        # Agréger les composants en layout
        return self._aggregate_components_to_layout(components_result)
    
    def _aggregate_components_to_layout(self, components_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agrège les composants générés en un layout complet.
        
        Args:
            components_result (Dict): Résultat de la génération des composants
            
        Returns:
            Dict: Layout complet avec organisation des composants
        """
        # Le layout contient les informations sur la page et les composants,
        # mais organisés dans une structure adaptée à Figma
        layout = {
            "page_id": components_result.get("page_id"),
            "timestamp": components_result.get("timestamp"),
            "layout": {
                "name": f"Redesign for {components_result.get('page_id')}",
                "sections": [],
                "components": []
            },
            "implementation_notes": components_result.get("implementation_notes", "")
        }
        
        # Organiser les composants par priorité
        priority_groups = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for comp in components_result.get("components", []):
            priority = comp.get("priority", "medium")
            priority_groups[priority].append(comp)
        
        # Ajouter des sections au layout en fonction de la priorité
        if priority_groups["high"]:
            layout["layout"]["sections"].append({
                "name": "Critical Improvements",
                "description": "High priority changes that should be implemented first",
                "components": [c.get("recommendation_title") for c in priority_groups["high"]]
            })
        
        if priority_groups["medium"]:
            layout["layout"]["sections"].append({
                "name": "Recommended Improvements",
                "description": "Medium priority changes for better user experience",
                "components": [c.get("recommendation_title") for c in priority_groups["medium"]]
            })
        
        if priority_groups["low"]:
            layout["layout"]["sections"].append({
                "name": "Nice-to-have Improvements",
                "description": "Low priority changes to consider after main improvements",
                "components": [c.get("recommendation_title") for c in priority_groups["low"]]
            })
        
        # Ajouter tous les composants à la liste principale
        for comp in components_result.get("components", []):
            layout["layout"]["components"].append({
                "name": comp.get("recommendation_title"),
                "figma_url": comp.get("component_result", {}).get("figma_url", ""),
                "component_id": comp.get("component_result", {}).get("component_id", ""),
                "priority": comp.get("priority")
            })
        
        return layout

# Fonction pour extraire les designs d'un site existant
def extract_components_from_website(url: str) -> Dict[str, Any]:
    """
    Extrait les composants UI d'un site web existant pour les réutiliser.
    
    Args:
        url (str): URL du site à analyser
        
    Returns:
        Dict: Bibliothèque de composants extraits du site
    """
    client = CodeToDesignClient()
    endpoint = f"{client.api_url}/extract/components"
    
    try:
        response = requests.post(
            endpoint,
            headers=client.headers,
            json={"url": url}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error extracting components: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return {"error": str(e)} 