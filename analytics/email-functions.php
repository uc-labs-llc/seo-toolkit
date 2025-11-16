<?php
// Core Email Functions
require_once 'email-config.php';

function sendEmail($to, $subject, $body) {
    $config = require 'email-config.php';
    
    $headers = [
        'From: ' . $config['from_name'] . ' <' . $config['from_email'] . '>',
        'Reply-To: ' . $config['from_email'],
        'Content-Type: text/html; charset=UTF-8',
        'X-Mailer: PHP/' . phpversion()
    ];
    
    if ($config['mail_method'] === 'gmail') {
        return sendViaGmail($to, $subject, $body, $config);
    } else {
        // Use Postfix/sendmail
        return mail($to, $subject, $body, implode("\r\n", $headers));
    }
}

function sendViaGmail($to, $subject, $body, $config) {
    // For Gmail, you'd typically use PHPMailer or similar
    // This is a simplified version
    $headers = [
        'From: ' . $config['from_name'] . ' <' . $config['gmail_smtp']['username'] . '>',
        'Reply-To: ' . $config['from_email'],
        'Content-Type: text/html; charset=UTF-8',
        'X-Mailer: PHP/' . phpversion()
    ];
    
    // In production, use PHPMailer for proper SMTP with auth
    return mail($to, $subject, $body, implode("\r\n", $headers));
}

function parseLogData($logText) {
    $entries = [];
    $lines = explode("\n", trim($logText));
    
    foreach ($lines as $line) {
        if (empty($line)) continue;
        
        $jsonStart = strpos($line, '{');
        if ($jsonStart !== false) {
            $jsonStr = substr($line, $jsonStart);
            $entry = json_decode($jsonStr, true);
            
            if ($entry) {
                $entries[] = $entry;
            }
        }
    }
    
    return $entries;
}

function analyzeForReport($data) {
    $sessions = [];
    $bounceSessions = 0;
    $pages = [];
    $browsers = [];
    
    foreach ($data as $entry) {
        if (isset($entry['sessionId'])) {
            $sessionId = $entry['sessionId'];
            
            if (!isset($sessions[$sessionId])) {
                $sessions[$sessionId] = [
                    'start' => strtotime($entry['timestamp']),
                    'end' => strtotime($entry['timestamp']),
                    'pages' => [],
                    'actions' => 0
                ];
            }
            
            $sessions[$sessionId]['end'] = max($sessions[$sessionId]['end'], strtotime($entry['timestamp']));
            $sessions[$sessionId]['actions']++;
            
            if ($entry['location']) {
                $sessions[$sessionId]['pages'][] = $entry['location'];
                $pages[$entry['location']] = ($pages[$entry['location']] ?? 0) + 1;
            }
            
            if ($entry['browser']) {
                $browsers[$entry['browser']] = ($browsers[$entry['browser']] ?? 0) + 1;
            }
        }
    }
    
    // Calculate session durations and bounces
    $sessionData = [];
    foreach ($sessions as $sessionId => $session) {
        $duration = $session['end'] - $session['start'];
        $sessionData[] = [
            'duration' => $duration,
            'pages' => count(array_unique($session['pages']))
        ];
        
        if (count(array_unique($session['pages'])) <= 1 && $duration < 30) {
            $bounceSessions++;
        }
    }
    
    return [
        'sessions' => $sessionData,
        'bounceSessions' => $bounceSessions,
        'topPage' => array_keys($pages, max($pages))[0] ?? null,
        'topBrowser' => array_keys($browsers, max($browsers))[0] ?? null
    ];
}

function getLastHourData($data) {
    $oneHourAgo = time() - 3600;
    $sessions = [];
    $errors = 0;
    
    foreach ($data as $entry) {
        $entryTime = strtotime($entry['timestamp']);
        if ($entryTime >= $oneHourAgo) {
            $sessionId = $entry['sessionId'] ?? null;
            if ($sessionId && !in_array($sessionId, $sessions)) {
                $sessions[] = $sessionId;
            }
            
            if (strpos($entry['action'], 'ERROR') !== false) {
                $errors++;
            }
        }
    }
    
    return [
        'sessions' => count($sessions),
        'errors' => $errors
    ];
}

function getPreviousHourData($data) {
    $twoHoursAgo = time() - 7200;
    $oneHourAgo = time() - 3600;
    $sessions = [];
    
    foreach ($data as $entry) {
        $entryTime = strtotime($entry['timestamp']);
        if ($entryTime >= $twoHoursAgo && $entryTime < $oneHourAgo) {
            $sessionId = $entry['sessionId'] ?? null;
            if ($sessionId && !in_array($sessionId, $sessions)) {
                $sessions[] = $sessionId;
            }
        }
    }
    
    return ['sessions' => count($sessions)];
}
?>
