import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import RecommendationPanel from '../components/RecommendationPanel';

// Mock axios
jest.mock('axios');

describe('RecommendationPanel', () => {
  const mockRecommendations = {
    page_id: 'test-page',
    insights: [
      {
        id: '1',
        type: 'friction',
        severity: 'high',
        title: 'High Bounce Rate',
        description: 'The page has a high bounce rate of 75%',
        recommendation: 'Improve content engagement',
        element_selector: '.hero-section',
        metrics_impact: {
          bounce_rate: '-15-25%',
          avg_session_duration: '+20-30%'
        },
        created_at: '2023-05-01T12:00:00Z'
      },
      {
        id: '2',
        type: 'layout',
        severity: 'medium',
        title: 'Poor Visual Hierarchy',
        description: 'Elements lack clear hierarchy',
        recommendation: 'Adjust sizing and spacing',
        element_selector: '.content-section',
        metrics_impact: {
          ctr: '+25-45%'
        },
        created_at: '2023-05-01T12:05:00Z'
      }
    ],
    summary: 'Found 2 optimization opportunities',
    timestamp: '2023-05-01T12:00:00Z',
    metrics_analyzed: {
      bounce_rate: 75.2,
      avg_session_duration: 60,
      conversion_rate: 1.8,
      ctr: 2.5
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    console.log = jest.fn();
    window.alert = jest.fn();
  });

  it('shows loading state initially', () => {
    axios.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 500)));
    
    render(
      <RecommendationPanel 
        pageId="test-page" 
        apiUrl="http://localhost:8088" 
        token="test-token" 
      />
    );
    
    expect(screen.getByText('Loading recommendations...')).toBeInTheDocument();
  });

  it('displays recommendations when loaded', async () => {
    // Mock successful API response
    axios.get.mockResolvedValue({ data: mockRecommendations });
    
    render(
      <RecommendationPanel 
        pageId="test-page" 
        apiUrl="http://localhost:8088" 
        token="test-token" 
      />
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('UI Optimization Insights')).toBeInTheDocument();
    });
    
    // Check insights are displayed
    expect(screen.getByText('High Bounce Rate')).toBeInTheDocument();
    expect(screen.getByText('Poor Visual Hierarchy')).toBeInTheDocument();
    
    // Check severity badges are displayed
    expect(screen.getByText('high')).toBeInTheDocument();
    expect(screen.getByText('medium')).toBeInTheDocument();
    
    // Check recommendations are displayed
    expect(screen.getByText('Improve content engagement')).toBeInTheDocument();
  });

  it('generates new recommendations if none exist', async () => {
    // Mock 404 for GET, success for POST
    axios.get.mockRejectedValue({ response: { status: 404 } });
    axios.post.mockResolvedValue({ data: mockRecommendations });
    
    render(
      <RecommendationPanel 
        pageId="test-page" 
        apiUrl="http://localhost:8088" 
        token="test-token" 
      />
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('UI Optimization Insights')).toBeInTheDocument();
    });
    
    // Verify POST was called to generate recommendations
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8088/api/recommendations/generate',
      expect.objectContaining({ page_id: 'test-page' }),
      expect.anything()
    );
  });

  it('filters insights by type when tabs are clicked', async () => {
    // Mock successful API response
    axios.get.mockResolvedValue({ data: mockRecommendations });
    
    render(
      <RecommendationPanel 
        pageId="test-page" 
        apiUrl="http://localhost:8088" 
        token="test-token" 
      />
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('UI Optimization Insights')).toBeInTheDocument();
    });
    
    // Both insights should be visible initially
    expect(screen.getByText('High Bounce Rate')).toBeInTheDocument();
    expect(screen.getByText('Poor Visual Hierarchy')).toBeInTheDocument();
    
    // Click on Friction tab
    fireEvent.click(screen.getByText(/Friction/));
    
    // Only friction insight should be visible
    expect(screen.getByText('High Bounce Rate')).toBeInTheDocument();
    expect(screen.queryByText('Poor Visual Hierarchy')).not.toBeInTheDocument();
    
    // Click on Layout tab
    fireEvent.click(screen.getByText(/Layout/));
    
    // Only layout insight should be visible
    expect(screen.queryByText('High Bounce Rate')).not.toBeInTheDocument();
    expect(screen.getByText('Poor Visual Hierarchy')).toBeInTheDocument();
  });

  it('handles preview and fix button clicks', async () => {
    // Mock successful API response
    axios.get.mockResolvedValue({ data: mockRecommendations });
    
    render(
      <RecommendationPanel 
        pageId="test-page" 
        apiUrl="http://localhost:8088" 
        token="test-token" 
      />
    );
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('UI Optimization Insights')).toBeInTheDocument();
    });
    
    // Find and click the Preview button for the first insight
    const previewButtons = screen.getAllByText('Preview');
    fireEvent.click(previewButtons[0]);
    
    // Check that console.log and alert were called
    expect(console.log).toHaveBeenCalledWith('Preview insight:', expect.anything());
    expect(window.alert).toHaveBeenCalledWith('Preview for: High Bounce Rate');
    
    // Find and click the Fix Issue button for the first insight
    const fixButtons = screen.getAllByText('Fix Issue');
    fireEvent.click(fixButtons[0]);
    
    // Check that console.log and alert were called
    expect(console.log).toHaveBeenCalledWith('Applying fix for insight:', expect.anything());
    expect(window.alert).toHaveBeenCalledWith('Applying fix for: High Bounce Rate');
  });
}); 