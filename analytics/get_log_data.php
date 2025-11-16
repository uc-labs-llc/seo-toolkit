<?php
// Set the content type to plain text so the JavaScript can read the file as raw lines.
header('Content-Type: text/plain');

$logFile = 'analytics.log';

if (file_exists($logFile)) {
    // Read the entire file content and output it.
    readfile($logFile);
} else {
    // If the file doesn't exist yet, output nothing or a placeholder message.
    echo "Log file is currently empty or does not exist.";
}
// Exit to prevent any extraneous output.
exit;
?>
