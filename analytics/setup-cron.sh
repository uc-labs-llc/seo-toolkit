#!/bin/bash
# Analytics Email System - Cron Setup

echo "Setting up analytics email system cron jobs..."

# Add to crontab
(crontab -l 2>/dev/null; echo "# Analytics Email System") | crontab -
(crontab -l 2>/dev/null; echo "0 6 * * * /usr/bin/php /var/www/html/analytics/email-reports.php >> /var/log/analytics-reports.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/bin/php /var/www/html/analytics/email-alerts.php >> /var/log/analytics-alerts.log 2>&1") | crontab -

echo "Cron jobs installed!"
echo "Daily reports: 6:00 AM"
echo "Alert checks: Every 10 minutes"
