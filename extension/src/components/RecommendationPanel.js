import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Severity badge component
const SeverityBadge = ({ severity }) => {
  const getSeverityColor = () => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor()} border`}>
      {severity}
    </span>
  );
};

// Metrics impact component
const MetricsImpact = ({ impacts }) => {
  if (!impacts || Object.keys(impacts).length === 0) {
    return null;
  }
  
  return (
    <div className="mt-2">
      <h5 className="text-xs font-medium text-gray-500 mb-1">Estimated Impact:</h5>
      <div className="flex flex-wrap gap-1.5">
        {Object.entries(impacts).map(([key, value]) => {
          // Determine if it's a positive or negative impact
          const isPositive = value.startsWith('+');
          const colorClass = isPositive 
            ? 'bg-green-50 text-green-700' 
            : 'bg-amber-50 text-amber-700';
            
          return (
            <span 
              key={key} 
              className={`${colorClass} px-2 py-0.5 rounded text-xs font-medium flex items-center`}
            >
              <span className="capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="ml-1 font-bold">{value}</span>
            </span>
          );
        })}
      </div>
    </div>
  );
};

// Insight card component
const InsightCard = ({ insight, onPreview, onFix }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4 border border-gray-200">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold text-gray-800">{insight.title}</h3>
        <SeverityBadge severity={insight.severity} />
      </div>
      
      <p className="text-gray-600 mb-3">{insight.description}</p>
      
      <div className="border-t border-gray-200 pt-3">
        <h4 className="font-medium text-gray-700 mb-2">Recommendation:</h4>
        <p className="text-gray-600 mb-3">{insight.recommendation}</p>
        
        {insight.element_selector && (
          <div className="mb-2 text-sm text-gray-500">
            <span className="font-medium">Target elements: </span>
            <code className="bg-gray-100 px-1 py-0.5 rounded">{insight.element_selector}</code>
          </div>
        )}
        
        <MetricsImpact impacts={insight.metrics_impact} />
      </div>
      
      <div className="flex justify-end space-x-2 mt-3">
        <button
          onClick={() => onPreview(insight)}
          className="px-3 py-1.5 text-sm bg-indigo-50 text-indigo-700 rounded-md hover:bg-indigo-100"
        >
          Preview
        </button>
        <button
          onClick={() => onFix(insight)}
          className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Fix Issue
        </button>
      </div>
    </div>
  );
};

// Main recommendation panel component
const RecommendationPanel = ({ pageId, apiUrl, token }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [activeTab, setActiveTab] = useState('all');

  // Fetch recommendations from API
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!pageId || !token) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // First try to get existing recommendations
        try {
          const response = await axios.get(`${apiUrl}/api/recommendations/${pageId}`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          if (response.data) {
            setRecommendations(response.data);
            setLoading(false);
            return;
          }
        } catch (err) {
          // If recommendations don't exist, we'll generate new ones
          console.log('No existing recommendations found, generating new ones...');
        }
        
        // Get metrics from your analytics service
        // In a real implementation, this would come from your analytics service like Amplitude
        const currentPageMetrics = {
          bounce_rate: 75.2,
          avg_session_duration: 60,
          conversion_rate: 1.8,
          ctr: 2.5,
          page_views: 15000
        };
        
        // Generate new recommendations using real metrics
        const generateResponse = await axios.post(
          `${apiUrl}/api/recommendations/generate`,
          {
            page_id: pageId,
            metrics: currentPageMetrics,
            options: {
              include_visual_recommendations: true,
              focus_areas: ['conversion', 'engagement', 'layout']
            }
          },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        
        setRecommendations(generateResponse.data);
        
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        setError('Failed to load recommendations. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchRecommendations();
  }, [pageId, apiUrl, token]);
  
  // Filter insights based on active tab
  const filteredInsights = recommendations?.insights?.filter(insight => {
    if (activeTab === 'all') return true;
    return insight.type === activeTab;
  }) || [];
  
  // Handle preview button click
  const handlePreview = (insight) => {
    // In a real implementation, this would preview the change in the UI
    console.log('Preview insight:', insight);
    
    // If we have an element selector, we could highlight it in the DOM
    if (insight.element_selector) {
      console.log('Targeting elements:', insight.element_selector);
    }
    
    alert(`Preview for: ${insight.title}`);
  };
  
  // Handle fix button click
  const handleFix = (insight) => {
    // In a real implementation, this would apply the fix to the page
    console.log('Applying fix for insight:', insight);
    
    // If we have an element selector, we could modify it in the DOM
    if (insight.element_selector) {
      console.log('Modifying elements:', insight.element_selector);
    }
    
    alert(`Applying fix for: ${insight.title}`);
  };
  
  // Handle fix all button click
  const handleFixAll = () => {
    // This would apply all recommended changes
    console.log('Fix all insights');
    
    // Only apply fixes for the filtered insights
    const insightsToFix = filteredInsights.map(insight => insight.id);
    console.log('Applying fixes for insights:', insightsToFix);
    
    alert(`Applying ${filteredInsights.length} fixes`);
  };
  
  // Get the count of insights by type
  const getInsightCountByType = (type) => {
    if (!recommendations?.insights) return 0;
    return recommendations.insights.filter(insight => insight.type === type).length;
  };
  
  if (loading) {
    return (
      <div className="p-6 flex justify-center items-center">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-600"></div>
        <span className="ml-2">Loading recommendations...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      </div>
    );
  }
  
  if (!recommendations || recommendations.insights.length === 0) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
          <p>No recommendations available for this page.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">UI Optimization Insights</h2>
        <p className="text-gray-600">{recommendations.summary}</p>
        
        <div className="mt-3 bg-indigo-50 p-3 rounded-md">
          <h3 className="text-sm font-medium text-indigo-800 mb-1">Analytics Data:</h3>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {Object.entries(recommendations.metrics_analyzed).map(([key, value]) => (
              <div key={key} className="bg-white p-2 rounded shadow-sm">
                <span className="text-xs text-gray-500 block capitalize">{key.replace(/_/g, ' ')}</span>
                <span className="text-indigo-700 font-medium">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="flex justify-between items-center mb-4">
        <div className="flex space-x-2 overflow-x-auto pb-2">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 text-sm rounded-md whitespace-nowrap ${
              activeTab === 'all'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            All ({recommendations.insights.length})
          </button>
          <button
            onClick={() => setActiveTab('friction')}
            className={`px-3 py-1.5 text-sm rounded-md whitespace-nowrap ${
              activeTab === 'friction'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            Friction ({getInsightCountByType('friction')})
          </button>
          <button
            onClick={() => setActiveTab('layout')}
            className={`px-3 py-1.5 text-sm rounded-md whitespace-nowrap ${
              activeTab === 'layout'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            Layout ({getInsightCountByType('layout')})
          </button>
          <button
            onClick={() => setActiveTab('conversion')}
            className={`px-3 py-1.5 text-sm rounded-md whitespace-nowrap ${
              activeTab === 'conversion'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            Conversion ({getInsightCountByType('conversion')})
          </button>
          <button
            onClick={() => setActiveTab('engagement')}
            className={`px-3 py-1.5 text-sm rounded-md whitespace-nowrap ${
              activeTab === 'engagement'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}
          >
            Engagement ({getInsightCountByType('engagement')})
          </button>
        </div>
        
        {filteredInsights.length > 0 && (
          <button
            onClick={handleFixAll}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 whitespace-nowrap"
          >
            Fix All Issues
          </button>
        )}
      </div>
      
      <div className="space-y-4">
        {filteredInsights.map(insight => (
          <InsightCard
            key={insight.id}
            insight={insight}
            onPreview={handlePreview}
            onFix={handleFix}
          />
        ))}
        
        {filteredInsights.length === 0 && (
          <div className="bg-gray-50 border border-gray-200 text-gray-700 px-4 py-3 rounded">
            <p>No insights found for the selected filter.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecommendationPanel; 