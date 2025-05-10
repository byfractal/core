/**
 * HCentric UI Optimizer - Type Definitions
 */

// Interface for an insight 
export interface Insight {
  id: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  pageUrl: string;
  timestamp: string;
  fixAvailable: boolean;
  selector?: string;
  cssModifications?: Record<string, string>;
  attributeChanges?: Record<string, string>;
  innerHTML?: string;
}

// Extension state interface
export interface ExtensionState {
  isAuthenticated: boolean;
  apiKey?: string;
  lastFetch?: number;
  activeSite?: string;
  insights: Insight[];
  settings: ExtensionSettings;
}

// Extension settings interface
export interface ExtensionSettings {
  showNotifications: boolean;
  highlightElements: boolean;
}

// Current site information
export interface SiteInfo {
  name: string;
  url: string;
}

// Message types
export type MessageType = 
  | 'AUTHENTICATE'
  | 'FETCH_INSIGHTS'
  | 'GET_INSIGHTS'
  | 'APPLY_FIX'
  | 'LOG_OUT'
  | 'PAGE_HAS_INSIGHTS'
  | 'COLLECT_PAGE_DATA'
  | 'HIGHLIGHT_ELEMENT'
  | 'CONTENT_LOADED';

// Base message interface
export interface Message {
  action: MessageType;
}

// Authentication message
export interface AuthMessage extends Message {
  action: 'AUTHENTICATE';
  apiKey: string;
}

// Fetch insights message
export interface FetchInsightsMessage extends Message {
  action: 'FETCH_INSIGHTS';
  siteUrl: string;
}

// Apply fix message
export interface ApplyFixMessage extends Message {
  action: 'APPLY_FIX';
  insightId: string;
  tabId?: number;
}

// Highlight element message
export interface HighlightElementMessage extends Message {
  action: 'HIGHLIGHT_ELEMENT';
  selector: string;
}

// Content loaded message
export interface ContentLoadedMessage extends Message {
  action: 'CONTENT_LOADED';
  url: string;
}

// Page has insights message
export interface PageHasInsightsMessage extends Message {
  action: 'PAGE_HAS_INSIGHTS';
  insights: Insight[];
}

// Combined message type
export type ExtensionMessage = 
  | Message
  | AuthMessage
  | FetchInsightsMessage
  | ApplyFixMessage
  | HighlightElementMessage
  | ContentLoadedMessage
  | PageHasInsightsMessage;

// Response interfaces
export interface BaseResponse {
  success: boolean;
  message?: string;
}

export interface InsightsResponse extends BaseResponse {
  insights?: Insight[];
}

export interface PageDataResponse extends BaseResponse {
  data?: Record<string, any>;
} 