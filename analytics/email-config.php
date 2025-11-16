<?php
// Email System Configuration
return [
    // Email Settings
    'from_email' => 'analytics@yourdomain.com',
    'from_name' => 'Web Analytics System',
    
    // Recipients for different report types
    'recipients' => [
        'daily_report' => ['admin@yourdomain.com'],
        'alerts' => ['admin@yourdomain.com', 'tech@yourdomain.com'],
        'weekly_report' => ['ceo@yourdomain.com', 'marketing@yourdomain.com']
    ],
    
    // Alert Thresholds
    'alert_thresholds' => [
        'traffic_spike' => 50,    // 50% increase
        'traffic_drop' => 30,     // 30% decrease  
        'error_rate' => 5,        // 5% error rate
        'bounce_rate' => 70       // 70% bounce rate
    ],
    
    // Postfix/Gmail Relay Settings
    'mail_method' => 'postfix', // 'postfix', 'gmail', or 'sendmail'
    
    // Gmail SMTP Relay (if using Gmail)
    'gmail_smtp' => [
        'host' => 'smtp.gmail.com',
        'port' => 587,
        'username' => 'your-email@gmail.com',
        'password' => 'your-app-password', // Use App Password, not regular password
        'encryption' => 'tls'
    ]
];
?>
