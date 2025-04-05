import json
import time
from typing import Dict, List, Any, Optional, Union
import warnings

# Nouvel import
from backend.models import DesignRecommendationTransformer

class DesignRecommendationTransformer:
    """
    Transforms AI-generated recommendations into actionable Figma modifications.
    
    This class bridges the gap between textual recommendations and concrete
    UI modifications that can be applied to a Figma design.
    """
    
    def __init__(self):
        """Initialize the converter."""
        self.recommendation_id = 0
    
    def parse_llm_recommendation(self, text_recommendation: str) -> Dict[str, Any]:
        """
        Parse a textual recommendation from LLM into structured data.
        
        Args:
            text_recommendation: Raw text from the LLM containing recommendations
            
        Returns:
            Structured dictionary with parsed recommendations
        """
        # TODO: Implement NLP parsing or structured output extraction
        # For now, this is a simplified example
        
        recommendations = []
        
        # Split recommendation into sections
        sections = text_recommendation.split("\n\n")
        
        for section in sections:
            if not section.strip():
                continue
                
            # Simple parsing logic - in production, use more robust NLP
            if ":" in section:
                parts = section.split(":")
                target = parts[0].strip()
                recommendation = ":".join(parts[1:]).strip()
                
                # Generate a recommendation object
                recommendation_obj = {
                    "id": f"rec_{self.recommendation_id}",
                    "targetId": self._extract_element_id(target),
                    "type": self._determine_recommendation_type(recommendation),
                    "property": self._extract_property(recommendation),
                    "oldValue": None,  # Would be filled from current design
                    "newValue": self._extract_value(recommendation),
                    "priority": self._determine_priority(recommendation),
                    "impact": self._estimate_impact(recommendation),
                    "reason": recommendation,
                    "isApplied": False,
                    "isRejected": False
                }
                
                recommendations.append(recommendation_obj)
                self.recommendation_id += 1
        
        # Create the full recommendation set
        recommendation_set = {
            "id": f"set_{int(time.time())}",
            "timestamp": int(time.time()),
            "sourceUrl": "",  # Would be filled from context
            "recommendations": recommendations,
            "stats": self._calculate_stats(recommendations)
        }
        
        return recommendation_set
    
    def generate_figma_actions(self, recommendation_set: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert a recommendation set into executable Figma actions.
        
        Args:
            recommendation_set: Structured recommendations
            
        Returns:
            List of Figma actions that can be executed by the plugin
        """
        figma_actions = []
        
        for rec in recommendation_set["recommendations"]:
            # Skip rejected recommendations
            if rec["isRejected"]:
                continue
                
            # Convert to Figma action based on type
            if rec["type"] == "style":
                action = self._create_style_action(rec)
            elif rec["type"] == "layout":
                action = self._create_layout_action(rec)
            elif rec["type"] == "accessibility":
                action = self._create_accessibility_action(rec)
            else:
                # Default action
                action = {
                    "action": "updateProperty",
                    "nodeId": rec["targetId"],
                    "property": rec["property"],
                    "value": rec["newValue"]
                }
            
            figma_actions.append(action)
        
        return figma_actions
    
    # Helper methods
    def _extract_element_id(self, target_text: str) -> str:
        # Simple extraction - in production use more robust methods
        import re
        id_match = re.search(r'id[=:][\s]*[\'"]?([^\'"]+)[\'"]?', target_text)
        if id_match:
            return id_match.group(1)
        return target_text
    
    def _determine_recommendation_type(self, text: str) -> str:
        keywords = {
            "style": ["color", "font", "size", "background", "border", "radius", "shadow"],
            "layout": ["padding", "margin", "position", "flex", "grid", "align", "justify"],
            "accessibility": ["contrast", "aria", "alt", "focus", "keyboard", "screen reader"],
            "usability": ["click", "tap", "interaction", "feedback", "animation"],
            "performance": ["load", "render", "optimize", "lazy", "images"]
        }
        
        text_lower = text.lower()
        for type_name, type_keywords in keywords.items():
            for keyword in type_keywords:
                if keyword in text_lower:
                    return type_name
        
        return "style"  # Default
    
    def _extract_property(self, text: str) -> str:
        # Simple property extraction
        property_mappings = {
            "color": ["color", "text color", "text-color"],
            "backgroundColor": ["background", "background color", "bg color"],
            "fontSize": ["font size", "text size"],
            "padding": ["padding", "internal spacing"],
            "margin": ["margin", "external spacing"],
            "borderRadius": ["radius", "corner radius", "rounded corners"]
        }
        
        text_lower = text.lower()
        for prop, keywords in property_mappings.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return prop
        
        return "style"  # Default fallback
    
    def _extract_value(self, text: str) -> Any:
        # This would need more sophisticated parsing in production
        import re
        
        # Try to extract color values
        color_match = re.search(r'#[0-9A-Fa-f]{3,8}', text)
        if color_match:
            return color_match.group(0)
        
        # Try to extract pixel values
        pixel_match = re.search(r'(\d+)px', text)
        if pixel_match:
            return int(pixel_match.group(1))
        
        # Try to extract percentage values
        percent_match = re.search(r'(\d+)%', text)
        if percent_match:
            return f"{percent_match.group(1)}%"
        
        return None
    
    def _determine_priority(self, text: str) -> int:
        text_lower = text.lower()
        if "critical" in text_lower or "severe" in text_lower:
            return 3  # Critical
        elif "important" in text_lower or "high" in text_lower:
            return 2  # High
        elif "medium" in text_lower or "moderate" in text_lower:
            return 1  # Medium
        return 0  # Low (default)
    
    def _estimate_impact(self, text: str) -> int:
        # Simplified impact estimation
        impact_score = 50  # Default middle impact
        
        text_lower = text.lower()
        impact_keywords = {
            "significant": 15,
            "major": 20,
            "important": 15,
            "critical": 25,
            "minor": -10,
            "small": -15,
            "subtle": -20
        }
        
        for keyword, score_mod in impact_keywords.items():
            if keyword in text_lower:
                impact_score += score_mod
        
        return max(0, min(100, impact_score))  # Clamp between 0-100
    
    def _calculate_stats(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for a set of recommendations"""
        if not recommendations:
            return {
                "total": 0,
                "byPriority": {},
                "byType": {},
                "estimatedImpactScore": 0
            }
            
        # Count recommendations by priority
        priority_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for rec in recommendations:
            priority = rec.get("priority", 0)
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
        # Count recommendations by type
        type_counts = {}
        for rec in recommendations:
            rec_type = rec.get("type", "style")
            type_counts[rec_type] = type_counts.get(rec_type, 0) + 1
            
        # Calculate overall impact score (weighted by priority)
        total_impact = 0
        priority_weights = {0: 0.25, 1: 0.5, 2: 0.75, 3: 1.0}
        for rec in recommendations:
            priority = rec.get("priority", 0)
            impact = rec.get("impact", 50)
            total_impact += impact * priority_weights.get(priority, 0.5)
            
        avg_impact = total_impact / len(recommendations) if recommendations else 0
            
        return {
            "total": len(recommendations),
            "byPriority": priority_counts,
            "byType": type_counts,
            "estimatedImpactScore": min(100, avg_impact)  # Cap at 100
        }
    
    # Actions creation methods
    def _create_style_action(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "updateStyle",
            "nodeId": recommendation["targetId"],
            "property": recommendation["property"],
            "value": recommendation["newValue"]
        }
    
    def _create_layout_action(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "updateLayout",
            "nodeId": recommendation["targetId"],
            "property": recommendation["property"],
            "value": recommendation["newValue"]
        }
    
    def _create_accessibility_action(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "updateAccessibility",
            "nodeId": recommendation["targetId"],
            "property": recommendation["property"],
            "value": recommendation["newValue"]
        }

# Avertissement pour l'utilisation de l'ancien nom
class CodeToDesign(DesignRecommendationTransformer):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "CodeToDesign is deprecated, use DesignRecommendationTransformer instead",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
