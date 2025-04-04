"""
Module pour transformer les recommandations en actions Figma
"""
import json
from typing import Dict, List, Any, Optional, Union
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DesignRecommendationTransformer:
    """
    Transforme les recommandations LLM en actions Figma standardisées
    """
    
    def __init__(self):
        """Initialise le transformateur"""
        self.id_counter = 0
    
    def _generate_id(self, prefix: str = "change") -> str:
        """Génère un ID unique pour une modification"""
        self.id_counter += 1
        return f"{prefix}_{self.id_counter}"
    
    def transform_recommendations(self, 
                                 recommendations: List[Dict[str, Any]],
                                 title: str,
                                 description: str) -> Dict[str, Any]:
        """
        Transforme une liste de recommandations en format JSON standardisé
        
        Args:
            recommendations: Liste de recommandations du LLM
            title: Titre de la collection de modifications
            description: Description de la collection
            
        Returns:
            Un objet JSON standardisé représentant les modifications UI
        """
        try:
            # Convertir chaque recommandation en action Figma
            changes = []
            for rec in recommendations:
                change = self._recommendation_to_change(rec)
                if change:
                    changes.append(change)
            
            # Créer la collection complète
            collection = {
                "id": self._generate_id("collection"),
                "title": title,
                "description": description,
                "changes": changes,
                "metrics": self._calculate_metrics(changes),
                "timestamp": self._get_current_timestamp(),
                "version": "1.0.0"
            }
            
            return collection
        except Exception as e:
            logger.error(f"Erreur lors de la transformation des recommandations: {str(e)}")
            raise
    
    def _recommendation_to_change(self, recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convertit une recommandation individuelle en action Figma
        
        Args:
            recommendation: La recommandation à convertir
            
        Returns:
            Un objet représentant une modification UI, ou None si invalide
        """
        try:
            # Extraire l'action et le type d'élément
            action_type = self._extract_action_type(recommendation)
            if not action_type:
                logger.warning(f"Type d'action non reconnu: {recommendation.get('action', 'inconnu')}")
                return None
            
            # Construire la modification
            change = {
                "id": self._generate_id(),
                "action": action_type,
                "metadata": {
                    "reasonForChange": recommendation.get("reason", ""),
                    "expectedImprovement": recommendation.get("expected_improvement", ""),
                    "confidenceScore": recommendation.get("confidence", 0.7),
                    "dataPoints": recommendation.get("data_points", [])
                }
            }
            
            # Ajouter le targetId pour les actions autres que CREATE
            if action_type != "CREATE":
                change["targetId"] = recommendation.get("element_id", "")
                if not change["targetId"]:
                    logger.warning(f"ID cible manquant pour l'action {action_type}")
                    return None
            
            # Pour CREATE, ajouter le type d'élément
            if action_type == "CREATE":
                element_type = self._extract_element_type(recommendation)
                if not element_type:
                    logger.warning("Type d'élément manquant pour l'action CREATE")
                    return None
                change["elementType"] = element_type
            
            # Ajouter les propriétés
            properties = {}
            
            # Propriétés de style
            style_props = self._extract_style_properties(recommendation)
            if style_props:
                properties["style"] = style_props
            
            # Propriétés de texte
            text_props = self._extract_text_properties(recommendation)
            if text_props:
                properties["text"] = text_props
            
            # Propriétés de mise en page
            layout_props = self._extract_layout_properties(recommendation)
            if layout_props:
                properties["layout"] = layout_props
            
            if properties:
                change["properties"] = properties
            
            return change
        except Exception as e:
            logger.warning(f"Erreur lors de la conversion de la recommandation: {str(e)}")
            return None
    
    def _extract_action_type(self, recommendation: Dict[str, Any]) -> Optional[str]:
        """Extrait le type d'action à partir de la recommandation"""
        action_mapping = {
            "create": "CREATE",
            "update": "UPDATE",
            "delete": "DELETE",
            "move": "REPOSITION",
            "resize": "RESIZE",
            "recolor": "RECOLOR",
            "regroup": "REGROUP"
        }
        
        action = recommendation.get("action", "").lower()
        return action_mapping.get(action)
    
    def _extract_element_type(self, recommendation: Dict[str, Any]) -> Optional[str]:
        """Extrait le type d'élément à partir de la recommandation"""
        element_mapping = {
            "frame": "FRAME",
            "text": "TEXT",
            "rectangle": "RECTANGLE",
            "component": "COMPONENT",
            "instance": "INSTANCE",
            "group": "GROUP"
        }
        
        element_type = recommendation.get("element_type", "").lower()
        return element_mapping.get(element_type)
    
    def _extract_style_properties(self, recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrait les propriétés de style à partir de la recommandation"""
        style = recommendation.get("style", {})
        if not style:
            return None
        
        result = {}
        
        # Couleur de remplissage
        if "fill_color" in style:
            result["fill"] = {
                "color": self._parse_color(style["fill_color"]),
                "type": "SOLID"
            }
        
        # Bordure
        if "stroke_color" in style or "stroke_weight" in style:
            result["stroke"] = {}
            if "stroke_color" in style:
                result["stroke"]["color"] = self._parse_color(style["stroke_color"])
            if "stroke_weight" in style:
                result["stroke"]["weight"] = style["stroke_weight"]
        
        # Effets
        effects = []
        if "shadow" in style:
            shadow = style["shadow"]
            effects.append({
                "type": "DROP_SHADOW",
                "radius": shadow.get("blur", 4),
                "color": self._parse_color(shadow.get("color", "#00000040")),
                "offset": {"x": shadow.get("offset_x", 0), "y": shadow.get("offset_y", 2)}
            })
        
        if effects:
            result["effects"] = effects
        
        # Rayon des coins
        if "corner_radius" in style:
            result["cornerRadius"] = style["corner_radius"]
        
        # Opacité
        if "opacity" in style:
            result["opacity"] = style["opacity"]
        
        return result if result else None
    
    def _extract_text_properties(self, recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrait les propriétés de texte à partir de la recommandation"""
        text = recommendation.get("text", {})
        if not text:
            return None
        
        result = {}
        
        # Contenu
        if "content" in text:
            result["content"] = text["content"]
        
        # Propriétés de police
        if "font_size" in text:
            result["fontSize"] = text["font_size"]
        if "font_family" in text:
            result["fontFamily"] = text["font_family"]
        if "font_weight" in text:
            result["fontWeight"] = text["font_weight"]
        if "letter_spacing" in text:
            result["letterSpacing"] = text["letter_spacing"]
        if "line_height" in text:
            result["lineHeight"] = text["line_height"]
        if "text_align" in text:
            align_mapping = {
                "left": "LEFT",
                "center": "CENTER",
                "right": "RIGHT",
                "justified": "JUSTIFIED"
            }
            result["textAlign"] = align_mapping.get(text["text_align"].lower(), "LEFT")
        
        return result if result else None
    
    def _extract_layout_properties(self, recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrait les propriétés de mise en page à partir de la recommandation"""
        layout = recommendation.get("layout", {})
        if not layout:
            return None
        
        result = {}
        
        # Position
        if "x" in layout:
            result["x"] = layout["x"]
        if "y" in layout:
            result["y"] = layout["y"]
        
        # Dimensions
        if "width" in layout:
            result["width"] = layout["width"]
        if "height" in layout:
            result["height"] = layout["height"]
        
        # Rotation
        if "rotation" in layout:
            result["rotation"] = layout["rotation"]
        
        # Contraintes
        if "constraints" in layout:
            constraints = layout["constraints"]
            result["constraints"] = {
                "horizontal": constraints.get("horizontal", "LEFT").upper(),
                "vertical": constraints.get("vertical", "TOP").upper()
            }
        
        return result if result else None
    
    def _parse_color(self, color_str: str) -> Dict[str, float]:
        """
        Parse une couleur au format hexadécimal ou RGB
        
        Args:
            color_str: Chaîne de couleur (#RRGGBB, #RRGGBBAA, rgb(r,g,b) ou rgba(r,g,b,a))
            
        Returns:
            Un dictionnaire {r, g, b, a} avec des valeurs entre 0 et 1
        """
        # Valeurs par défaut
        color = {"r": 0, "g": 0, "b": 0, "a": 1}
        
        try:
            if color_str.startswith("#"):
                # Format hexadécimal
                hex_color = color_str.lstrip("#")
                
                if len(hex_color) == 6:
                    # #RRGGBB
                    r = int(hex_color[0:2], 16) / 255
                    g = int(hex_color[2:4], 16) / 255
                    b = int(hex_color[4:6], 16) / 255
                    color = {"r": r, "g": g, "b": b, "a": 1}
                elif len(hex_color) == 8:
                    # #RRGGBBAA
                    r = int(hex_color[0:2], 16) / 255
                    g = int(hex_color[2:4], 16) / 255
                    b = int(hex_color[4:6], 16) / 255
                    a = int(hex_color[6:8], 16) / 255
                    color = {"r": r, "g": g, "b": b, "a": a}
            elif color_str.startswith("rgb"):
                # Format RGB ou RGBA
                values = color_str.replace("rgba(", "").replace("rgb(", "").replace(")", "").split(",")
                
                if len(values) >= 3:
                    r = int(values[0].strip()) / 255
                    g = int(values[1].strip()) / 255
                    b = int(values[2].strip()) / 255
                    color = {"r": r, "g": g, "b": b, "a": 1}
                    
                    if len(values) == 4:
                        # RGBA
                        a = float(values[3].strip())
                        color["a"] = a
        except Exception as e:
            logger.warning(f"Erreur lors du parsing de la couleur '{color_str}': {str(e)}")
        
        return color
    
    def _calculate_metrics(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule les métriques globales pour une collection de modifications
        
        Args:
            changes: Liste des modifications
            
        Returns:
            Un dictionnaire de métriques
        """
        # Exemple simple - dans un cas réel, utiliser un algorithme plus sophistiqué
        if not changes:
            return {
                "expectedImprovementScore": 0,
                "impactAreas": [],
                "priority": "LOW",
                "implementationComplexity": "LOW"
            }
        
        # Calcul du score d'amélioration attendu
        score_sum = 0
        confidence_sum = 0
        
        for change in changes:
            metadata = change.get("metadata", {})
            confidence = metadata.get("confidenceScore", 0.5)
            confidence_sum += confidence
            
            # Facteur d'importance basé sur le type d'action
            action_importance = {
                "CREATE": 1.2,
                "UPDATE": 0.8,
                "DELETE": 0.5,
                "REPOSITION": 0.3,
                "RESIZE": 0.4,
                "RECOLOR": 0.6,
                "REGROUP": 0.7
            }
            
            importance = action_importance.get(change.get("action", "UPDATE"), 0.5)
            score_sum += confidence * importance * 20  # Normaliser pour un score sur 100
        
        # Score moyen
        avg_score = min(100, max(0, score_sum / len(changes)))
        
        # Déterminer les domaines d'impact
        impact_areas = self._determine_impact_areas(changes)
        
        # Déterminer la priorité
        priority = "LOW"
        if avg_score >= 70:
            priority = "HIGH"
        elif avg_score >= 40:
            priority = "MEDIUM"
        
        # Déterminer la complexité d'implémentation
        complexity = "LOW"
        if len(changes) > 15:
            complexity = "HIGH"
        elif len(changes) > 5:
            complexity = "MEDIUM"
        
        return {
            "expectedImprovementScore": round(avg_score, 1),
            "impactAreas": impact_areas,
            "priority": priority,
            "implementationComplexity": complexity
        }
    
    def _determine_impact_areas(self, changes: List[Dict[str, Any]]) -> List[str]:
        """
        Détermine les domaines d'impact d'une collection de modifications
        
        Args:
            changes: Liste des modifications
            
        Returns:
            Liste des domaines d'impact
        """
        # Analyse simple des modifications pour déterminer les domaines d'impact
        impact_areas = set()
        
        for change in changes:
            action = change.get("action", "")
            properties = change.get("properties", {})
            
            if action == "RECOLOR" or "fill" in properties.get("style", {}):
                impact_areas.add("Visual Hierarchy")
                impact_areas.add("Brand Alignment")
            
            if action == "REPOSITION" or "layout" in properties:
                impact_areas.add("Layout")
                impact_areas.add("Usability")
            
            if action == "RESIZE" or ("layout" in properties and ("width" in properties.get("layout", {}) or "height" in properties.get("layout", {}))):
                impact_areas.add("Layout")
                impact_areas.add("Responsive Design")
            
            if "text" in properties:
                impact_areas.add("Typography")
                impact_areas.add("Content Clarity")
            
            # Regarder les métadonnées pour d'autres indications
            metadata = change.get("metadata", {})
            reason = metadata.get("reasonForChange", "").lower()
            
            if "access" in reason or "a11y" in reason or "accessibility" in reason:
                impact_areas.add("Accessibility")
            
            if "convers" in reason:
                impact_areas.add("Conversion Rate")
            
            if "engage" in reason:
                impact_areas.add("User Engagement")
        
        return sorted(list(impact_areas))
    
    def _get_current_timestamp(self) -> int:
        """Obtient le timestamp actuel en millisecondes"""
        import time
        return int(time.time() * 1000)
    
    def process_llm_output(self, llm_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite la sortie brute du LLM et la convertit en format JSON standardisé
        
        Args:
            llm_output: Sortie du LLM
            
        Returns:
            Un objet JSON standardisé pour les modifications Figma
        """
        try:
            # Extraire les informations essentielles
            title = llm_output.get("title", "UI Improvement Recommendations")
            description = llm_output.get("description", "Generated design recommendations based on analysis")
            recommendations = llm_output.get("recommendations", [])
            
            # Transformer en format standardisé
            return self.transform_recommendations(recommendations, title, description)
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la sortie LLM: {str(e)}")
            # Retourner un objet minimal en cas d'erreur
            return {
                "id": self._generate_id("collection"),
                "title": "Error Processing Recommendations",
                "description": f"An error occurred: {str(e)}",
                "changes": [],
                "timestamp": self._get_current_timestamp(),
                "version": "1.0.0"
            }

# Exemple d'utilisation:
if __name__ == "__main__":
    # Exemple de recommandations générées par le LLM
    sample_llm_output = {
        "title": "Login Form Optimization",
        "description": "Recommendations to improve the login form UX based on user session analysis",
        "recommendations": [
            {
                "action": "update",
                "element_id": "login_button",
                "element_type": "rectangle",
                "style": {
                    "fill_color": "#4285F4",
                    "corner_radius": 8
                },
                "layout": {
                    "width": 280
                },
                "reason": "Increase button visibility to improve conversion rate",
                "expected_improvement": "14% increase in successful logins",
                "confidence": 0.85,
                "data_points": ["heatmap_analysis", "session_recordings"]
            },
            {
                "action": "create",
                "element_type": "text",
                "text": {
                    "content": "Forgot password?",
                    "font_size": 14,
                    "font_family": "Inter",
                    "text_align": "center"
                },
                "layout": {
                    "x": 150,
                    "y": 250
                },
                "reason": "Users often struggle to find password recovery option",
                "expected_improvement": "Reduce support tickets by 22%",
                "confidence": 0.78,
                "data_points": ["support_ticket_analysis", "user_interviews"]
            }
        ]
    }
    
    # Transformer les recommandations
    transformer = DesignRecommendationTransformer()
    result = transformer.process_llm_output(sample_llm_output)
    
    # Afficher le résultat
    print(json.dumps(result, indent=2)) 