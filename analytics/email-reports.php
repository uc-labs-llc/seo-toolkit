<?php
// Daily/Weekly Analytics Reports
require_once 'email-config.php';
require_once 'email-functions.php';

$config = require 'email-config.php';
$logFile = 'analytics.log';

function generateDailyReport($data) {
    $totalSessions = count($data['sessions']);
    $avgDuration = array_sum(array_column($data['sessions'], 'duration')) / max(1, $totalSessions);
    $bounceRate = ($data['bounceSessions'] / max(1, $totalSessions)) * 100;
    
    return [
        'subject' => "📊 Daily Analytics Report - " . date('Y-m-d'),
        'body' => "
            <h2>📈 Daily Analytics Summary</h2>
            <p><strong>Date:</strong> " . date('F j, Y') . "</p>
            
            <div style='background: #f8f9fa; padding: 20px; border-radius: 8px;'>
                <h3>📊 Key Metrics</h3>
                <ul>
                    <li><strong>Total Sessions:</strong> " . number_format($totalSessions) . "</li>
                    <li><strong>Avg. Session Duration:</strong> " . round($avgDuration) . " seconds</li>
                    <li><strong>Bounce Rate:</strong> " . round($bounceRate, 1) . "%</li>
                    <li><strong>Top Page:</strong> " . ($data['topPage'] ?? 'N/A') . "</li>
                    <li><strong>Most Used Browser:</strong> " . ($data['topBrowser'] ?? 'N/A') . "</li>
                </ul>
            </div>
            
            <p><em>Report generated on " . date('Y-m-d H:i:s') . "</em></p>
        "
    ];
}

// Main execution
if (file_exists($logFile)) {
    $logData = parseLogData(file_get_contents($logFile));
    $reportData = analyzeForReport($logData);
    $report = generateDailyReport($reportData);
    
    foreach ($config['recipients']['daily_report'] as $recipient) {
        sendEmail($recipient, $report['subject'], $report['body']);
    }
    
    echo "Daily report sent to " . count($config['recipients']['daily_report']) . " recipients\n";
} else {
    echo "No analytics data found\n";
}
?>
