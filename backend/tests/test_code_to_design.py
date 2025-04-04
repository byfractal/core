"""
Tests automatisés pour le module code_to_design.py qui transforme 
les recommandations en actions Figma standardisées
"""
import unittest
import json
from pathlib import Path
import sys
from typing import Dict, Any, List

# Ajout du chemin du projet pour l'importation
sys.path.append(str(Path(__file__).parent.parent))

from services.code_to_design import DesignRecommendationTransformer

class TestDesignRecommendationTransformer(unittest.TestCase):
    """
    Tests unitaires pour la classe DesignRecommendationTransformer
    """
    
    def setUp(self):
        """
        Initialisation avant chaque test
        """
        self.transformer = DesignRecommendationTransformer()
        
        # Exemple de données de test
        self.sample_recommendations = [
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
        
    def test_transform_recommendations(self):
        """
        Teste la transformation des recommandations en format JSON standardisé
        """
        # Transformer les recommandations
        result = self.transformer.transform_recommendations(
            self.sample_recommendations,
            "Test Recommendations",
            "Test description"
        )
        
        # Vérifier la structure de base
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("title", result)
        self.assertIn("description", result)
        self.assertIn("changes", result)
        self.assertIn("metrics", result)
        self.assertIn("timestamp", result)
        self.assertIn("version", result)
        
        # Vérifier le contenu
        self.assertEqual(result["title"], "Test Recommendations")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(len(result["changes"]), len(self.sample_recommendations))
        
        # Vérifier les métriques
        metrics = result["metrics"]
        self.assertIn("expectedImprovementScore", metrics)
        self.assertIn("impactAreas", metrics)
        self.assertIn("priority", metrics)
        self.assertIn("implementationComplexity", metrics)
    
    def test_recommendation_to_change(self):
        """
        Teste la conversion d'une recommandation individuelle en action Figma
        """
        # Tester une recommandation d'action UPDATE
        update_rec = self.sample_recommendations[0]
        change = self.transformer._recommendation_to_change(update_rec)
        
        self.assertIsNotNone(change)
        self.assertEqual(change["action"], "UPDATE")
        self.assertEqual(change["targetId"], "login_button")
        self.assertIn("properties", change)
        self.assertIn("style", change["properties"])
        self.assertIn("layout", change["properties"])
        
        # Tester une recommandation d'action CREATE
        create_rec = self.sample_recommendations[1]
        change = self.transformer._recommendation_to_change(create_rec)
        
        self.assertIsNotNone(change)
        self.assertEqual(change["action"], "CREATE")
        self.assertEqual(change["elementType"], "TEXT")
        self.assertIn("properties", change)
        self.assertIn("text", change["properties"])
        self.assertEqual(change["properties"]["text"]["content"], "Forgot password?")
    
    def test_extract_action_type(self):
        """
        Teste l'extraction du type d'action à partir de la recommandation
        """
        # Test des différents types d'action
        test_cases = [
            {"action": "create", "expected": "CREATE"},
            {"action": "update", "expected": "UPDATE"},
            {"action": "delete", "expected": "DELETE"},
            {"action": "move", "expected": "REPOSITION"},
            {"action": "resize", "expected": "RESIZE"},
            {"action": "recolor", "expected": "RECOLOR"},
            {"action": "regroup", "expected": "REGROUP"},
            {"action": "unknown", "expected": None}
        ]
        
        for case in test_cases:
            action_type = self.transformer._extract_action_type({"action": case["action"]})
            self.assertEqual(action_type, case["expected"])
    
    def test_extract_element_type(self):
        """
        Teste l'extraction du type d'élément à partir de la recommandation
        """
        # Test des différents types d'élément
        test_cases = [
            {"element_type": "frame", "expected": "FRAME"},
            {"element_type": "text", "expected": "TEXT"},
            {"element_type": "rectangle", "expected": "RECTANGLE"},
            {"element_type": "component", "expected": "COMPONENT"},
            {"element_type": "instance", "expected": "INSTANCE"},
            {"element_type": "group", "expected": "GROUP"},
            {"element_type": "unknown", "expected": None}
        ]
        
        for case in test_cases:
            element_type = self.transformer._extract_element_type({"element_type": case["element_type"]})
            self.assertEqual(element_type, case["expected"])
    
    def test_parse_color(self):
        """
        Teste la conversion des couleurs au format hexadécimal ou RGB
        """
        # Test des différents formats de couleur
        test_cases = [
            {"color": "#FF0000", "expected": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}},
            {"color": "#00FF00", "expected": {"r": 0.0, "g": 1.0, "b": 0.0, "a": 1.0}},
            {"color": "#0000FF", "expected": {"r": 0.0, "g": 0.0, "b": 1.0, "a": 1.0}},
            {"color": "#FF000080", "expected": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 0.5}},
            {"color": "rgb(255, 0, 0)", "expected": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}},
            {"color": "rgba(255, 0, 0, 0.5)", "expected": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 0.5}},
            {"color": "invalid", "expected": {"r": 0.0, "g": 0.0, "b": 0.0, "a": 1.0}}
        ]
        
        for case in test_cases:
            color = self.transformer._parse_color(case["color"])
            # Comparer les valeurs avec une tolérance pour les erreurs d'arrondi
            for key, expected_value in case["expected"].items():
                self.assertAlmostEqual(color[key], expected_value, places=2, 
                                      msg=f"Failed for color {case['color']}, key {key}")
    
    def test_calculate_metrics(self):
        """
        Teste le calcul des métriques à partir des modifications
        """
        # Test avec une liste vide
        empty_metrics = self.transformer._calculate_metrics([])
        self.assertEqual(empty_metrics["expectedImprovementScore"], 0)
        self.assertEqual(empty_metrics["priority"], "LOW")
        
        # Test avec des modifications réelles
        result = self.transformer.transform_recommendations(
            self.sample_recommendations,
            "Test Recommendations",
            "Test description"
        )
        
        changes = result["changes"]
        metrics = self.transformer._calculate_metrics(changes)
        
        self.assertGreater(metrics["expectedImprovementScore"], 0)
        self.assertIn(metrics["priority"], ["LOW", "MEDIUM", "HIGH"])
        self.assertIn(metrics["implementationComplexity"], ["LOW", "MEDIUM", "HIGH"])
        self.assertIsInstance(metrics["impactAreas"], list)
    
    def test_determine_impact_areas(self):
        """
        Teste la détermination des domaines d'impact à partir des modifications
        """
        # Test avec différents types de modifications
        changes = [
            {
                "action": "RECOLOR",
                "properties": {"style": {"fill": {"color": {"r": 1, "g": 0, "b": 0}}}}
            },
            {
                "action": "REPOSITION",
                "properties": {"layout": {"x": 100, "y": 100}}
            },
            {
                "action": "UPDATE",
                "properties": {"text": {"content": "Test"}}
            },
            {
                "action": "UPDATE",
                "metadata": {"reasonForChange": "Improve accessibility for users"}
            }
        ]
        
        impact_areas = self.transformer._determine_impact_areas(changes)
        
        # Vérifier que les domaines d'impact attendus sont inclus
        expected_areas = ["Visual Hierarchy", "Brand Alignment", "Layout", "Usability", 
                         "Typography", "Content Clarity", "Accessibility"]
        
        for area in expected_areas:
            self.assertIn(area, impact_areas)
    
    def test_process_llm_output(self):
        """
        Teste le traitement de la sortie brute du LLM
        """
        # Créer un exemple de sortie LLM
        llm_output = {
            "title": "Login Form Optimization",
            "description": "Improve UX of the login form",
            "recommendations": self.sample_recommendations
        }
        
        # Transformer la sortie
        result = self.transformer.process_llm_output(llm_output)
        
        # Vérifier la structure de base
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("title", result)
        self.assertIn("description", result)
        self.assertIn("changes", result)
        
        # Vérifier le contenu
        self.assertEqual(result["title"], "Login Form Optimization")
        self.assertEqual(result["description"], "Improve UX of the login form")
        self.assertEqual(len(result["changes"]), len(self.sample_recommendations))
    
    def test_error_handling(self):
        """
        Teste la gestion des erreurs dans le transformateur
        """
        # Test avec une recommandation invalide
        invalid_recommendation = {
            "action": "invalid_action",
            "element_id": "button1"
        }
        
        change = self.transformer._recommendation_to_change(invalid_recommendation)
        self.assertIsNone(change)
        
        # Test avec une action CREATE sans type d'élément
        invalid_create = {
            "action": "create"
        }
        
        change = self.transformer._recommendation_to_change(invalid_create)
        self.assertIsNone(change)
        
        # Test avec une action UPDATE sans ID cible
        invalid_update = {
            "action": "update"
        }
        
        change = self.transformer._recommendation_to_change(invalid_update)
        self.assertIsNone(change)
    
    def test_complete_workflow(self):
        """
        Teste le flux de travail complet du module
        """
        # Créer un exemple complet de sortie LLM
        llm_output = {
            "title": "Checkout Page Optimization",
            "description": "Recommendations to improve the checkout process",
            "recommendations": [
                {
                    "action": "update",
                    "element_id": "submit_button",
                    "element_type": "rectangle",
                    "style": {
                        "fill_color": "#22C55E",
                        "corner_radius": 8,
                        "shadow": {
                            "color": "#00000020",
                            "blur": 4,
                            "offset_x": 0,
                            "offset_y": 2
                        }
                    },
                    "layout": {
                        "width": 280
                    },
                    "text": {
                        "content": "Complete Purchase",
                        "font_size": 16,
                        "font_weight": 600
                    },
                    "reason": "Users report confusion about the final action, clearer call-to-action needed",
                    "expected_improvement": "Estimated 8% increase in conversion rate",
                    "confidence": 0.92,
                    "data_points": ["heatmap_analysis", "user_interviews", "A/B test results"]
                },
                {
                    "action": "create",
                    "element_type": "text",
                    "text": {
                        "content": "Your card will not be charged until you confirm",
                        "font_size": 12,
                        "font_family": "Inter",
                        "text_align": "center"
                    },
                    "layout": {
                        "x": 150,
                        "y": 320
                    },
                    "reason": "Users express concern about premature charging",
                    "expected_improvement": "Reduce cart abandonment by 15%",
                    "confidence": 0.85,
                    "data_points": ["exit surveys", "session recordings"]
                },
                {
                    "action": "delete",
                    "element_id": "promotional_banner",
                    "reason": "Distracts users from completing checkout process",
                    "expected_improvement": "4% reduction in checkout time",
                    "confidence": 0.78,
                    "data_points": ["funnel analysis", "eye tracking study"]
                }
            ]
        }
        
        # Transformer la sortie
        result = self.transformer.process_llm_output(llm_output)
        
        # Vérifier que tous les types d'actions sont correctement transformés
        actions_in_result = [change["action"] for change in result["changes"]]
        self.assertIn("UPDATE", actions_in_result)
        self.assertIn("CREATE", actions_in_result)
        self.assertIn("DELETE", actions_in_result)
        
        # Vérifier que les métriques sont calculées
        self.assertGreater(result["metrics"]["expectedImprovementScore"], 0)
        self.assertIsInstance(result["metrics"]["impactAreas"], list)
        self.assertGreater(len(result["metrics"]["impactAreas"]), 0)

if __name__ == '__main__':
    unittest.main() 