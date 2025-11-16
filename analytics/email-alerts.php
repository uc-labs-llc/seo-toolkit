<?php
// Real-time Alert System
require_once 'email-config.php';
require_once 'email-functions.php';

$config = require 'email-config.php';
$logFile = 'analytics.log';

function checkForAlerts($data, $config) {
    $alerts = [];
    $currentHour = date('H');
    
    // Get last hour data for comparison
    $lastHourData = getLastHourData($data);
    $previousHourData = getPreviousHourData($data);
    
    // Traffic spike detection
    if ($lastHourData['sessions'] > 0 && $previousHourData['sessions'] > 0) {
        $growth = (($lastHourData['sessions'] - $previousHourData['sessions']) / $previousHourData['sessions']) * 100;
        
        if ($growth > $config['alert_thresholds']['traffic_spike']) {
            $alerts[] = [
                'type' => 'traffic_spike',
                'message' => "🚀 Traffic spike detected: " . round($growth) . "% increase in the last hour",
                'severity' => 'info'
            ];
        }
        
        if ($growth < -$config['alert_thresholds']['traffic_drop']) {
            $alerts[] = [
                'type' => 'traffic_drop', 
                'message' => "📉 Traffic drop detected: " . round(abs($growth)) . "% decrease in the last hour",
                'severity' => 'warning'
            ];
        }
    }
    
    // Error rate check
    $errorRate = ($lastHourData['errors'] / max(1, $lastHourData['sessions'])) * 100;
    if ($errorRate > $config['alert_thresholds']['error_rate']) {
        $alerts[] = [
            'type' => 'high_errors',
            'message' => "⚠️ High error rate: " . round($errorRate, 1) . "% of sessions had errors",
            'severity' => 'error'
        ];
    }
    
    return $alerts;
}

// Main execution
if (file_exists($logFile)) {
    $logData = parseLogData(file_get_contents($logFile));
    $alerts = checkForAlerts($logData, $config);
    
    if (!empty($alerts)) {
        $alertBody = "<h2>🚨 Analytics Alerts</h2>";
        
        foreach ($alerts as $alert) {
            $alertBody .= "<div style='padding: 10px; margin: 10px 0; border-left: 4px solid " . 
                         ($alert['severity'] == 'error' ? '#dc3545' : 
                          ($alert['severity'] == 'warning' ? '#ffc107' : '#28a745')) . 
                         "; background: #f8f9fa;'>" .
                         "<strong>" . $alert['message'] . "</strong></div>";
        }
        
        $alertBody .= "<p><em>Alert check at " . date('Y-m-d H:i:s') . "</em></p>";
        
        foreach ($config['recipients']['alerts'] as $recipient) {
            sendEmail($recipient, "🚨 Analytics Alerts - " . date('H:i'), $alertBody);
        }
        
        echo "Sent " . count($alerts) . " alerts to " . count($config['recipients']['alerts']) . " recipients\n";
    } else {
        echo "No alerts triggered\n";
    }
}
?>
