"""
FastAPI endpoints for UI optimization recommendations.
This module provides a RESTful API to generate and retrieve recommendations based on Amplitude data analysis.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import random

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Pydantic models for requests and responses
class AmplitudeDataRequest(BaseModel):
    """Request model for Amplitude data import"""
    api_key: str = Field(..., description="Amplitude API key")
    secret_key: Optional[str] = Field(None, description="Amplitude secret key (optional)")
    start_date: str = Field(..., description="Start date (format YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (format YYYY-MM-DD)")
    project_id: Optional[str] = Field(None, description="Amplitude project ID")

class RecommendationRequest(BaseModel):
    """Request model for recommendation generation"""
    page_id: str = Field(..., description="Page identifier to analyze")
    metrics: Dict[str, Any] = Field(..., description="Analysis metrics (CTR, bounce rate, etc.)")
    options: Optional[Dict[str, Any]] = Field(None, description="Generation options")

class InsightItem(BaseModel):
    """Model for a UI insight item"""
    id: str = Field(..., description="Unique insight identifier")
    type: str = Field(..., description="Insight type (friction, layout, conversion, etc.)")
    severity: str = Field(..., description="Severity (high, medium, low)")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    recommendation: str = Field(..., description="Improvement recommendation")
    element_selector: Optional[str] = Field(None, description="CSS selector for the affected element")
    before_screenshot: Optional[str] = Field(None, description="URL of the before screenshot")
    after_preview: Optional[str] = Field(None, description="URL of the after preview")
    metrics_impact: Optional[Dict[str, Any]] = Field(None, description="Estimated impact on metrics")
    created_at: str = Field(..., description="Creation date")

class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    page_id: str = Field(..., description="Page identifier")
    insights: List[InsightItem] = Field(..., description="List of generated insights")
    summary: str = Field(..., description="Recommendations summary")
    timestamp: str = Field(..., description="Generation timestamp")
    metrics_analyzed: Dict[str, Any] = Field(..., description="Analyzed metrics")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    status: str = "error"

# Create router for recommendations API
recommendations_router = APIRouter(
    prefix="/api/recommendations",
    tags=["recommendations"],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)

# Cache to store recent results
recommendations_cache = {}
generation_tasks = {}

def analyze_bounce_rate(bounce_rate: float) -> Optional[InsightItem]:
    """Analyze bounce rate and generate insights if needed."""
    if bounce_rate > 60:
        severity = "high" if bounce_rate > 75 else "medium"
        
        return InsightItem(
            id=str(uuid.uuid4()),
            type="friction",
            severity=severity,
            title="High Bounce Rate Detected",
            description=f"The page has a bounce rate of {bounce_rate}%, which is above the recommended threshold of 50%.",
            recommendation="Consider improving the page's initial content engagement, call-to-action visibility, and load time to reduce bounces.",
            element_selector="header, .hero-section, .cta-primary",
            metrics_impact={
                "bounce_rate": "-15-25%",
                "avg_session_duration": "+20-30%"
            },
            created_at=datetime.now().isoformat()
        )
    return None

def analyze_conversion_rate(conversion_rate: float) -> Optional[InsightItem]:
    """Analyze conversion rate and generate insights if needed."""
    if conversion_rate < 3.0:
        severity = "high" if conversion_rate < 1.5 else "medium"
        
        return InsightItem(
            id=str(uuid.uuid4()),
            type="conversion",
            severity=severity,
            title="Low Conversion Rate",
            description=f"The page has a conversion rate of {conversion_rate}%, which is below industry benchmarks of 3-5%.",
            recommendation="Enhance the prominence of your primary CTA button with better contrast, position it above the fold, and clarify the value proposition.",
            element_selector=".cta-button, .signup-form, .pricing-table",
            metrics_impact={
                "conversion_rate": "+40-80%",
                "ctr": "+15-25%"
            },
            created_at=datetime.now().isoformat()
        )
    return None

def analyze_session_duration(duration: float) -> Optional[InsightItem]:
    """Analyze session duration and generate insights if needed."""
    if duration < 90:
        return InsightItem(
            id=str(uuid.uuid4()),
            type="engagement",
            severity="medium",
            title="Short Session Duration",
            description=f"Average session duration is only {duration} seconds, indicating potential engagement issues.",
            recommendation="Add more interactive elements, improve content readability with better typography and spacing, and ensure mobile responsiveness.",
            element_selector="article, .content-section, .text-content",
            metrics_impact={
                "avg_session_duration": "+40-60%",
                "page_views": "+15-30%"
            },
            created_at=datetime.now().isoformat()
        )
    return None

def analyze_click_through_rate(ctr: float) -> Optional[InsightItem]:
    """Analyze CTR and generate insights if needed."""
    if ctr < 4.0:
        return InsightItem(
            id=str(uuid.uuid4()),
            type="layout",
            severity="medium",
            title="Suboptimal Click-Through Rate",
            description=f"The click-through rate of {ctr}% suggests users aren't finding or engaging with important UI elements.",
            recommendation="Improve the visual hierarchy by using size, color, and whitespace to guide users' attention to key actions and information.",
            element_selector=".navigation, .call-to-action, .feature-cards",
            metrics_impact={
                "ctr": "+25-45%",
                "conversion_rate": "+10-20%"
            },
            created_at=datetime.now().isoformat()
        )
    return None

def analyze_page_layout() -> Optional[InsightItem]:
    """Generate layout insights based on common UI patterns."""
    layout_issues = [
        InsightItem(
            id=str(uuid.uuid4()),
            type="layout",
            severity="medium",
            title="Cluttered Above-the-Fold Content",
            description="The above-the-fold section contains too many competing elements, creating visual noise and reducing focus on primary actions.",
            recommendation="Simplify the hero section by reducing the number of elements and creating a clear visual hierarchy that guides users to the primary call-to-action.",
            element_selector=".hero-section, header",
            metrics_impact={
                "bounce_rate": "-10-20%",
                "conversion_rate": "+15-25%"
            },
            created_at=datetime.now().isoformat()
        ),
        InsightItem(
            id=str(uuid.uuid4()),
            type="layout",
            severity="low",
            title="Inconsistent Button Styling",
            description="Button styles vary across the page, creating confusion about which elements are clickable and their relative importance.",
            recommendation="Standardize button styles with a clear visual hierarchy: primary (filled), secondary (outlined), and tertiary (text only) styles.",
            element_selector="button, .btn, .cta",
            metrics_impact={
                "ctr": "+10-20%",
                "conversion_rate": "+5-15%"
            },
            created_at=datetime.now().isoformat()
        ),
        InsightItem(
            id=str(uuid.uuid4()),
            type="friction",
            severity="high",
            title="Poor Mobile Responsiveness",
            description="Key UI elements break or overlap on mobile devices, causing frustration for mobile users who make up a significant portion of traffic.",
            recommendation="Implement a mobile-first approach for critical UI components, ensure sufficient tap targets (min 44×44px), and test thoroughly on multiple device sizes.",
            element_selector=".navigation, .product-grid, form",
            metrics_impact={
                "mobile_bounce_rate": "-30-40%",
                "mobile_conversion_rate": "+20-35%"
            },
            created_at=datetime.now().isoformat()
        )
    ]
    
    # Return a random layout issue
    return random.choice(layout_issues)

@recommendations_router.post("/generate", response_model=RecommendationResponse, 
                     responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate UI optimization recommendations based on data analysis.
    
    This function analyzes the provided metrics and generates insights to improve the user interface.
    """
    try:
        # Get current timestamp
        current_time = datetime.now().isoformat()
        
        # Extract metrics from request
        metrics = request.metrics
        bounce_rate = metrics.get("bounce_rate", 0)
        conversion_rate = metrics.get("conversion_rate", 0)
        avg_session_duration = metrics.get("avg_session_duration", 0)
        ctr = metrics.get("ctr", 0)
        
        # Generate insights based on metrics
        insights = []
        
        # Analyze bounce rate
        bounce_insight = analyze_bounce_rate(bounce_rate)
        if bounce_insight:
            insights.append(bounce_insight)
        
        # Analyze conversion rate
        conversion_insight = analyze_conversion_rate(conversion_rate)
        if conversion_insight:
            insights.append(conversion_insight)
        
        # Analyze session duration
        duration_insight = analyze_session_duration(avg_session_duration)
        if duration_insight:
            insights.append(duration_insight)
        
        # Analyze CTR
        ctr_insight = analyze_click_through_rate(ctr)
        if ctr_insight:
            insights.append(ctr_insight)
        
        # Always add at least one layout insight for demonstration
        layout_insight = analyze_page_layout()
        if layout_insight:
            insights.append(layout_insight)
        
        # Create summary based on number of insights
        insight_count = len(insights)
        if insight_count > 3:
            summary = f"Found {insight_count} significant optimization opportunities that could improve key metrics by 15-30%."
        elif insight_count > 0:
            summary = f"Identified {insight_count} potential improvements that may enhance user experience and key metrics."
        else:
            summary = "No significant issues found. The page appears to be performing adequately."
        
        # Create response object
        response = RecommendationResponse(
            page_id=request.page_id,
            insights=insights,
            summary=summary,
            timestamp=current_time,
            metrics_analyzed=metrics
        )
        
        # Cache the result for this page
        recommendations_cache[request.page_id] = response
        
        return response
        
    except Exception as e:
        # Handle exceptions
        raise HTTPException(status_code=500, detail=str(e))

@recommendations_router.get("/{page_id}", response_model=RecommendationResponse,
                    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_recommendations(page_id: str):
    """
    Retrieve UI optimization recommendations for a specific page.
    
    If recommendations exist in cache for this page, they are returned.
    Otherwise, a 404 error is returned.
    """
    if page_id in recommendations_cache:
        return recommendations_cache[page_id]
    else:
        raise HTTPException(status_code=404, detail=f"No recommendations found for page {page_id}")

@recommendations_router.post("/import/amplitude", response_model=Dict[str, Any],
                     responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def import_amplitude_data(
    request: AmplitudeDataRequest,
    background_tasks: BackgroundTasks
):
    """
    Import data from Amplitude for analysis.
    
    This function launches a background task to retrieve data from Amplitude
    and prepare it for analysis.
    """
    try:
        # Generate a task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task state
        generation_tasks[task_id] = {
            "status": "pending",
            "request": request.dict(),
            "result": None,
            "error": None
        }
        
        # Define the import task
        def run_import_task():
            try:
                # Simulate actual Amplitude API integration
                # In a real implementation, you would use the Amplitude API client here
                
                # Simulate processing time
                import time
                time.sleep(2)
                
                # Update status when completed with simulated data
                generation_tasks[task_id]["status"] = "completed"
                generation_tasks[task_id]["result"] = {
                    "status": "success",
                    "data_points": random.randint(5000, 25000),
                    "pages_analyzed": random.randint(5, 20),
                    "date_range": f"{request.start_date} to {request.end_date}",
                    "metrics_extracted": [
                        "bounce_rate",
                        "avg_session_duration",
                        "conversion_rate",
                        "ctr",
                        "page_views"
                    ]
                }
                
            except Exception as e:
                # Handle exceptions
                generation_tasks[task_id]["status"] = "failed"
                generation_tasks[task_id]["error"] = str(e)
        
        # Add the background task
        background_tasks.add_task(run_import_task)
        
        # Return the task ID
        return {"task_id": task_id, "status": "pending"}
        
    except Exception as e:
        # Handle exceptions
        raise HTTPException(status_code=500, detail=str(e))

@recommendations_router.get("/import/status/{task_id}", response_model=Dict[str, Any])
async def get_import_status(task_id: str):
    """
    Get the status of a data import task.
    """
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task_info = generation_tasks[task_id]
    
    # Prepare the response
    response = {
        "task_id": task_id,
        "status": task_info["status"],
    }
    
    # Add the result or error if available
    if task_info["status"] == "completed" and task_info["result"]:
        response["result"] = task_info["result"]
    elif task_info["status"] == "failed" and task_info["error"]:
        response["error"] = task_info["error"]
    
    return response 