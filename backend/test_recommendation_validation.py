#!/usr/bin/env python3
"""
Test script for the enhanced design recommendation system with validation.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path to enable imports
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from backend.models.design_recommendations import DesignRecommendationChain
from backend.models.recommendation_validator import RecommendationValidator

def load_sample_analysis(file_path=None):
    """
    Load a sample analysis file or use a default example.
    
    Args:
        file_path (str, optional): Path to an analysis JSON file
        
    Returns:
        dict: Analysis data
    """
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    
    # Use default example if no file provided or file doesn't exist
    return {
        "metadata": {
            "page_id": "/checkout",
            "timestamp": datetime.now().isoformat(),
            "session_count": 250,
            "using_sample_data": False
        },
        "results": {
            "summary": {
                "summary": "Users find the checkout process confusing and lengthy. The form has too many fields and the submit button is difficult to locate. Mobile users report additional issues with menu functionality and image loading. Many users abandon checkout during the payment step.",
                "key_issues": [
                    "Lengthy checkout process",
                    "Too many form fields",
                    "Hard to find submit button",
                    "Mobile menu not working properly",
                    "Images not loading on mobile",
                    "Payment step confusion"
                ],
                "positive_aspects": [
                    "Professional website appearance",
                    "Good color scheme", 
                    "Easy desktop navigation"
                ],
                "overall_sentiment": "Mixed, with significant frustration around checkout and mobile experience",
                "priority_recommendations": [
                    "Simplify checkout form",
                    "Make submit button more prominent",
                    "Fix mobile menu functionality",
                    "Optimize image loading for mobile",
                    "Improve payment step clarity"
                ]
            },
            "confusion_areas": [
                {
                    "area": "payment-form",
                    "score": 8.5,
                    "type": "repeated_clicks"
                },
                {
                    "area": "submit-button",
                    "score": 7.2,
                    "type": "repeated_clicks"
                },
                {
                    "area": "/checkout",
                    "score": 6.8,
                    "type": "navigation_loop"
                }
            ],
            "usage_patterns": {
                "average_time_on_page": 240,  # seconds
                "bounce_rate": 0.35,
                "conversion_rate": 0.42,
                "device_distribution": {
                    "desktop": 0.65,
                    "mobile": 0.30,
                    "tablet": 0.05
                }
            }
        }
    }

def test_recommendation_generation(analysis_data, model="gpt-4o", validate=True, save_to=None, verbose=False):
    """
    Test the enhanced recommendation generation with validation.
    
    Args:
        analysis_data (dict): Analysis data to use for recommendations
        model (str): LLM model to use
        validate (bool): Whether to validate recommendations
        save_to (str, optional): Path to save the recommendations
        verbose (bool): Display detailed output
        
    Returns:
        dict: Generated recommendations
    """
    print(f"\n{'='*80}")
    print(f"TESTING ENHANCED DESIGN RECOMMENDATION SYSTEM")
    print(f"{'='*80}")
    print(f"Using model: {model}")
    print(f"Validation enabled: {validate}")
    
    # Initialize the recommendation chain
    recommendation_chain = DesignRecommendationChain(model=model)
    
    # Extract page ID and summary from analysis data
    page_id = analysis_data["metadata"]["page_id"]
    summary = analysis_data["results"]["summary"]
    
    if verbose:
        print(f"\nAnalyzing page: {page_id}")
        print(f"Key issues identified: {len(summary['key_issues'])}")
        print(f"Key issues: {', '.join(summary['key_issues'])}")
    
    print(f"\nGenerating design recommendations...")
    try:
        # Generate recommendations
        start_time = datetime.now()
        recommendations = recommendation_chain.generate_recommendations(
            analysis_summary=summary,
            page_id=page_id,
            validate=validate
        )
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"Successfully generated recommendations in {generation_time:.2f} seconds")
        
        # Display recommendation statistics
        recommendation_count = len(recommendations.get("recommendations", []))
        print(f"\nGenerated {recommendation_count} recommendations")
        
        if validate and "validation_summary" in recommendations:
            vs = recommendations["validation_summary"]
            print(f"Validation summary:")
            print(f"  - Feasible: {vs.get('feasible_count', 0)}")
            print(f"  - Needs modification: {vs.get('needs_modification_count', 0)}")
            print(f"  - Infeasible: {vs.get('infeasible_count', 0)}")
            print(f"  - Average feasibility score: {vs.get('average_feasibility_score', 0):.1f}/100")
        
        # Display recommendations if verbose
        if verbose:
            print(f"\nTop recommendations:")
            for i, rec in enumerate(recommendations.get("recommendations", [])[:3], 1):
                print(f"\n{i}. {rec.get('title', 'Untitled')}")
                print(f"   Component: {rec.get('component', 'N/A')}")
                print(f"   Priority: {rec.get('priority', 'N/A')}")
                print(f"   Description: {rec.get('description', 'N/A')}")
                
                if validate and "validation" in rec:
                    val = rec["validation"]
                    print(f"   Feasibility: {val.get('feasibility_score', 0)}/100")
                    if "issues" in val and val["issues"]:
                        print(f"   Issues: {len(val['issues'])}")
                        for issue in val["issues"][:2]:  # Show up to 2 issues
                            print(f"     - {issue.get('issue_type', 'unknown')}: {issue.get('description', 'N/A')}")
                
                if "impact_score" in rec:
                    print(f"   Impact Score: {rec.get('impact_score', 0)}/30")
        
        # Save recommendations if requested
        if save_to:
            os.makedirs(os.path.dirname(os.path.abspath(save_to)), exist_ok=True)
            with open(save_to, 'w') as f:
                json.dump(recommendations, f, indent=2)
            print(f"\nRecommendations saved to: {save_to}")
            
        return recommendations
            
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_recommendation_validator(recommendations=None):
    """
    Test the standalone recommendation validator.
    
    Args:
        recommendations (dict, optional): Recommendations to validate
        
    Returns:
        dict: Validation results
    """
    print(f"\n{'='*80}")
    print(f"TESTING RECOMMENDATION VALIDATOR")
    print(f"{'='*80}")
    
    # Create validator
    validator = RecommendationValidator()
    
    # Use sample recommendation if none provided
    if not recommendations or "recommendations" not in recommendations:
        sample_rec = {
            "title": "Add Clear Filters Button",
            "description": "Add a clearly visible 'Clear Filters' button next to the filter controls",
            "component": "Button",
            "location": "Top of search results, next to existing filters",
            "expected_impact": "Users can easily reset search filters without refreshing the page",
            "priority": "medium",
            "justification": "Users reported difficulty clearing multiple filters",
            "before_after": {
                "before": "No way to clear all filters at once",
                "after": "Clear Filters button prominently displayed next to filter controls"
            }
        }
        
        print(f"Testing with sample recommendation: '{sample_rec['title']}'")
        
        try:
            start_time = datetime.now()
            validation_result = validator.validate_recommendation(sample_rec)
            end_time = datetime.now()
            validation_time = (end_time - start_time).total_seconds()
            
            print(f"Validation completed in {validation_time:.2f} seconds")
            print(f"Feasibility score: {validation_result.get('feasibility_score', 0)}/100")
            print(f"Is feasible: {validation_result.get('is_feasible', False)}")
            
            issue_count = len(validation_result.get("issues", []))
            if issue_count > 0:
                print(f"Issues identified: {issue_count}")
                for issue in validation_result.get("issues", []):
                    print(f"  - {issue.get('issue_type', 'unknown')}: {issue.get('description', 'N/A')}")
            else:
                print("No issues identified")
                
            return validation_result
                
        except Exception as e:
            print(f"Error validating recommendation: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    else:
        print(f"Testing with {len(recommendations.get('recommendations', []))} recommendations")
        
        try:
            start_time = datetime.now()
            validation_results = validator.validate_all_recommendations(recommendations)
            end_time = datetime.now()
            validation_time = (end_time - start_time).total_seconds()
            
            print(f"Validation of all recommendations completed in {validation_time:.2f} seconds")
            
            if "validation_summary" in validation_results:
                vs = validation_results["validation_summary"]
                print(f"Validation summary:")
                print(f"  - Total recommendations: {vs.get('total_recommendations', 0)}")
                print(f"  - Feasible: {vs.get('feasible_count', 0)}")
                print(f"  - Needs modification: {vs.get('needs_modification_count', 0)}")
                print(f"  - Infeasible: {vs.get('infeasible_count', 0)}")
                print(f"  - Average feasibility score: {vs.get('average_feasibility_score', 0):.1f}/100")
            
            return validation_results
            
        except Exception as e:
            print(f"Error validating recommendations: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def test_ranking_by_impact(recommendations):
    """
    Test the ranking of recommendations by impact.
    
    Args:
        recommendations (dict): Validated recommendations
        
    Returns:
        dict: Ranked recommendations
    """
    print(f"\n{'='*80}")
    print(f"TESTING RECOMMENDATION RANKING BY IMPACT")
    print(f"{'='*80}")
    
    if not recommendations or "recommendations" not in recommendations:
        print("No recommendations to rank")
        return None
    
    # Initialize recommendation chain
    recommendation_chain = DesignRecommendationChain()
    
    try:
        ranked_recommendations = recommendation_chain.rank_recommendations_by_impact(recommendations)
        
        print(f"Successfully ranked {len(ranked_recommendations.get('recommendations', []))} recommendations")
        
        # Display top 3 recommendations by impact
        print("\nTop 3 recommendations by impact:")
        for i, rec in enumerate(ranked_recommendations.get('recommendations', [])[:3], 1):
            print(f"{i}. {rec.get('title', 'Untitled')} - Impact: {rec.get('impact_score', 0)}/30")
            print(f"   Priority: {rec.get('priority', 'N/A')}")
            if "validation" in rec:
                print(f"   Feasibility: {rec['validation'].get('feasibility_score', 0)}/100")
        
        return ranked_recommendations
        
    except Exception as e:
        print(f"Error ranking recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function for testing the recommendation system."""
    parser = argparse.ArgumentParser(description='Test the enhanced design recommendation system')
    parser.add_argument('--analysis', '-a', type=str, help='Path to analysis JSON file')
    parser.add_argument('--model', '-m', type=str, default='gpt-4o', help='LLM model to use')
    parser.add_argument('--output', '-o', type=str, default='backend/recommendations_output.json', 
                        help='Output file for recommendations')
    parser.add_argument('--validate', '-v', action='store_true', help='Validate recommendations')
    parser.add_argument('--skip-generation', '-s', action='store_true', help='Skip recommendation generation')
    parser.add_argument('--verbose', action='store_true', help='Display detailed output')
    
    args = parser.parse_args()
    
    # Load analysis data
    analysis_data = load_sample_analysis(args.analysis)
    
    recommendations = None
    
    # Test recommendation generation if not skipped
    if not args.skip_generation:
        recommendations = test_recommendation_generation(
            analysis_data=analysis_data,
            model=args.model,
            validate=args.validate,
            save_to=args.output,
            verbose=args.verbose
        )
    else:
        # Try to load existing recommendations
        try:
            with open(args.output, 'r') as f:
                recommendations = json.load(f)
            print(f"Loaded existing recommendations from {args.output}")
        except Exception as e:
            print(f"Could not load existing recommendations: {str(e)}")
    
    # Test standalone validator
    if recommendations:
        validation_results = test_recommendation_validator(recommendations)
    else:
        validation_results = test_recommendation_validator()
    
    # Test ranking by impact if we have recommendations
    if recommendations and "recommendations" in recommendations:
        if "validation_summary" not in recommendations and validation_results:
            # Use validation results if available
            recommendations = validation_results
            
        ranked_recommendations = test_ranking_by_impact(recommendations)
        
        # Save ranked recommendations
        if ranked_recommendations and args.output:
            ranked_output = args.output.replace('.json', '_ranked.json')
            with open(ranked_output, 'w') as f:
                json.dump(ranked_recommendations, f, indent=2)
            print(f"\nRanked recommendations saved to: {ranked_output}")

if __name__ == "__main__":
    main() 