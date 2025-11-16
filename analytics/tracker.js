// Define the global Canvas environment variables for consistency
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};

// ==================== SESSION MANAGEMENT ====================

/**
 * Generates a unique session ID
 * @returns {string} Unique session identifier
 */
function generateSessionId() {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Gets existing session ID or creates a new one
 * Sessions expire after 30 minutes of inactivity
 * @returns {string} Session ID
 */
function getOrCreateSessionId() {
    // Try to get existing session from sessionStorage (persists per tab)
    let sessionId = sessionStorage.getItem('analytics_session_id');
    const lastActivity = sessionStorage.getItem('analytics_last_activity');
    
    // Session expires after 30 minutes of inactivity
    const thirtyMinutesAgo = Date.now() - (30 * 60 * 1000);
    const isExpired = lastActivity && parseInt(lastActivity) < thirtyMinutesAgo;
    
    if (!sessionId || isExpired) {
        sessionId = generateSessionId();
        sessionStorage.setItem('analytics_session_id', sessionId);
        sessionStorage.setItem('analytics_session_start', new Date().toISOString());
        console.log('Analytics: New session started:', sessionId);
    }
    
    // Update last activity timestamp
    sessionStorage.setItem('analytics_last_activity', Date.now().toString());
    
    return sessionId;
}

/**
 * Gets the session start time
 * @returns {string} ISO timestamp of session start
 */
function getSessionStartTime() {
    let startTime = sessionStorage.getItem('analytics_session_start');
    if (!startTime) {
        startTime = new Date().toISOString();
        sessionStorage.setItem('analytics_session_start', startTime);
    }
    return startTime;
}

/**
 * Tracks page views within the session
 */
function trackPageView() {
    const currentPage = window.location.pathname;
    const pageViews = JSON.parse(sessionStorage.getItem('analytics_page_views') || '[]');
    
    // Only track if this is a new page or enough time has passed
    const lastView = pageViews[pageViews.length - 1];
    if (!lastView || lastView.page !== currentPage) {
        pageViews.push({
            page: currentPage,
            timestamp: new Date().toISOString(),
            title: document.title
        });
        sessionStorage.setItem('analytics_page_views', JSON.stringify(pageViews));
    }
}

/**
 * Gets the referring page for the current session
 * @returns {string} Referrer information
 */
function getSessionReferrer() {
    // For the first page view in session, use document.referrer
    // For subsequent views, use the previous page in the session
    const pageViews = JSON.parse(sessionStorage.getItem('analytics_page_views') || '[]');
    
    if (pageViews.length === 0) {
        return document.referrer || 'direct';
    } else if (pageViews.length >= 1) {
        const previousPage = pageViews[pageViews.length - 1].page;
        return previousPage !== window.location.pathname ? previousPage : 'self';
    }
    
    return 'direct';
}

// ==================== CORE TRACKING FUNCTIONS ====================

/**
 * Sends user activity data to the server-side log endpoint.
 * Enhanced with session tracking and additional metadata.
 * @param {string} action - The type of action (e.g., 'PAGE_LOAD', 'BUTTON_CLICK').
 * @param {object} metadata - Additional data related to the action.
 */
async function logUserAction(action, metadata = {}) {
    const sessionId = getOrCreateSessionId();
    const sessionStart = getSessionStartTime();
    const sessionReferrer = getSessionReferrer();
    
    // Enhanced data payload with session information
    const data = {
        // Core tracking fields
        action: action,
        appId: appId,
        timestamp: new Date().toISOString(),
        location: window.location.pathname,
        userAgent: navigator.userAgent,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        pageTitle: document.title,
        
        // Session tracking fields (NEW)
        sessionId: sessionId,
        sessionStart: sessionStart,
        referrer: sessionReferrer,
        pageLoadTime: performance.timing ? performance.timing.loadEventEnd - performance.timing.navigationStart : null,
        
        // Language and timezone (NEW)
        language: navigator.language,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        
        // Additional metadata
        ...metadata
    };

    // CORRECTED ENDPOINT URL: Now points to the file in the same directory
    const endpointUrl = 'log_endpoint.php'; 

    try {
        const response = await fetch(endpointUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            // Ensure cookies (like session IDs) are sent for logging user session
            credentials: 'include',
            // Add timeout to prevent hanging requests
            signal: AbortSignal.timeout(5000)
        });

        // Check for success status (200-299)
        if (response.ok) {
            console.log(`Analytics: ${action} logged successfully for session ${sessionId}`);
        } else {
            // Log a warning if the server returned a status other than 200 OK
            const errorText = await response.text();
            console.warn(`Analytics: Logging failed with status ${response.status}: ${errorText}`);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.warn('Analytics: Request timeout - analytics data not sent');
        } else {
            // Log an error if the network request itself failed (e.g., connection issue)
            console.error('Analytics: Network error during logging:', error);
        }
    }
}

/**
 * Tracks custom events like button clicks, form submissions, etc.
 * @param {string} eventCategory - Category of the event (e.g., 'button', 'form')
 * @param {string} eventAction - Action performed (e.g., 'click', 'submit')
 * @param {string} eventLabel - Label for the event (e.g., 'contact-form')
 * @param {number} eventValue - Numeric value associated with the event
 */
function trackEvent(eventCategory, eventAction, eventLabel = null, eventValue = null) {
    logUserAction('CUSTOM_EVENT', {
        eventCategory: eventCategory,
        eventAction: eventAction,
        eventLabel: eventLabel,
        eventValue: eventValue,
        eventElement: eventLabel ? `[data-track="${eventLabel}"]` : null
    });
}

/**
 * Tracks form submissions
 * @param {HTMLFormElement} form - The form element that was submitted
 */
function trackFormSubmit(form) {
    logUserAction('FORM_SUBMIT', {
        formId: form.id || 'unknown',
        formAction: form.action || 'unknown',
        formMethod: form.method || 'GET',
        formFields: Array.from(form.elements)
            .filter(el => el.name)
            .map(el => ({ name: el.name, type: el.type }))
    });
}

/**
 * Tracks JavaScript errors
 * @param {string} message - Error message
 * @param {string} source - Source file where error occurred
 * @param {number} lineno - Line number
 * @param {number} colno - Column number
 * @param {Error} error - Error object
 */
function trackError(message, source, lineno, colno, error) {
    logUserAction('JS_ERROR', {
        errorMessage: message,
        errorSource: source,
        errorLine: lineno,
        errorColumn: colno,
        errorStack: error ? error.stack : null,
        errorType: error ? error.constructor.name : 'Unknown'
    });
}

// ==================== INITIALIZATION ====================

/**
 * Sets up automatic event tracking for common interactions
 */
function setupAutomaticTracking() {
    // Track button clicks with data-track attribute
    document.addEventListener('click', function(event) {
        const trackableElement = event.target.closest('[data-track]');
        if (trackableElement) {
            const trackData = trackableElement.getAttribute('data-track');
            trackEvent('button', 'click', trackData);
        }
    });
    
    // Track form submissions
    document.addEventListener('submit', function(event) {
        trackFormSubmit(event.target);
    });
    
    // Track outbound links
    document.addEventListener('click', function(event) {
        const link = event.target.closest('a');
        if (link && link.href && link.hostname !== window.location.hostname) {
            trackEvent('outbound', 'click', link.href);
        }
    });
    
    // Track file downloads
    document.addEventListener('click', function(event) {
        const link = event.target.closest('a');
        if (link && link.href) {
            const isDownload = link.download || 
                              /\.(pdf|doc|docx|xls|xlsx|zip|rar|exe|dmg)$/i.test(link.href);
            if (isDownload) {
                trackEvent('download', 'click', link.href);
            }
        }
    });
}

/**
 * Initializes the tracker and logs the initial page load event.
 * Enhanced with session management and automatic tracking.
 */
function initializeTracker() {
    // Track page view for session management
    trackPageView();
    
    // Log initial page load
    logUserAction('PAGE_LOAD', { 
        pageTitle: document.title,
        previousPage: document.referrer || 'direct'
    });
    
    // Set up automatic event tracking
    setupAutomaticTracking();
    
    // Set up global error tracking
    window.addEventListener('error', function(event) {
        trackError(event.message, event.filename, event.lineno, event.colno, event.error);
    });
    
    // Track performance metrics if available
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const perfData = performance.timing;
                const loadTime = perfData.loadEventEnd - perfData.navigationStart;
                const domReadyTime = perfData.domContentLoadedEventEnd - perfData.navigationStart;
                
                logUserAction('PERFORMANCE', {
                    loadTime: loadTime,
                    domReadyTime: domReadyTime,
                    firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,
                    firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime
                });
            }, 0);
        });
    }
    
    console.log('Analytics: Tracker initialized with session management');
}

// ==================== SESSION LIFECYCLE ====================

/**
 * Ends the current session (useful for logout scenarios)
 */
function endSession() {
    const sessionId = sessionStorage.getItem('analytics_session_id');
    if (sessionId) {
        logUserAction('SESSION_END', {
            sessionDuration: Date.now() - parseInt(sessionStorage.getItem('analytics_last_activity') || '0')
        });
    }
    
    // Clear session storage
    sessionStorage.removeItem('analytics_session_id');
    sessionStorage.removeItem('analytics_session_start');
    sessionStorage.removeItem('analytics_last_activity');
    sessionStorage.removeItem('analytics_page_views');
    
    console.log('Analytics: Session ended');
}

/**
 * Updates session activity (call this on user interactions)
 */
function updateSessionActivity() {
    sessionStorage.setItem('analytics_last_activity', Date.now().toString());
}

// ==================== PUBLIC API ====================

// Make tracking functions available globally
window.AnalyticsTracker = {
    trackEvent: trackEvent,
    trackError: trackError,
    endSession: endSession,
    updateActivity: updateSessionActivity,
    getSessionId: getOrCreateSessionId
};

// ==================== EVENT LISTENERS ====================

// Start tracking once the DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTracker);
} else {
    initializeTracker();
}

// Track user interactions to keep session alive
document.addEventListener('click', updateSessionActivity);
document.addEventListener('keypress', updateSessionActivity);
document.addEventListener('scroll', updateSessionActivity);

// Track when the user closes or navigates away
window.addEventListener('beforeunload', () => {
    // Note: The fetch might not complete, but it's a best effort for tracking
    logUserAction('PAGE_UNLOAD', {
        sessionPages: JSON.parse(sessionStorage.getItem('analytics_page_views') || '[]').length
    });
});

// Track visibility changes (tab switching)
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'hidden') {
        logUserAction('PAGE_HIDDEN');
    } else if (document.visibilityState === 'visible') {
        logUserAction('PAGE_VISIBLE');
    }
});
