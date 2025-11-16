<?php
// Set the content type to application/json for the response
header('Content-Type: application/json');

// Define the local log file path
$logFile = 'analytics.log';

// --- 1. Read Raw POST Data ---
// This is the correct way to read JSON sent via fetch() POST request.
$input = file_get_contents('php://input');

// Check if input is empty immediately
if (empty($input)) {
    http_response_code(400); // Bad Request
    // Log the error internally (this will appear in your server's PHP error log)
    error_log("Analytics Log Error: Received empty input from client request.", 0);
    echo json_encode(['status' => 'error', 'message' => 'Received empty data in request body.']);
    exit;
}

// --- 2. Decode JSON and Validate ---
$data = json_decode($input, true);

// Simple input validation
if ($data === null && json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(400); // Bad Request
    error_log("Analytics Log Error: Invalid JSON received: " . $input, 0);
    echo json_encode(['status' => 'error', 'message' => 'Invalid JSON data received.', 'raw_input' => $input]);
    exit;
}

// --- 3. Format and Write Log Entry ---
$logEntry = '[' . date('Y-m-d H:i:s') . '] ';
$logEntry .= json_encode($data) . "\n"; 

// Attempt to write to the log file
$writeResult = file_put_contents($logFile, $logEntry, FILE_APPEND | LOCK_EX);

// --- 4. Check Write Result ---
if ($writeResult !== false) {
    http_response_code(200); // OK
    echo json_encode(['status' => 'success', 'message' => 'Log entry recorded successfully.']);
} else {
    // This usually means a permissions failure, but if you fixed it, it's a critical system error.
    http_response_code(500); 
    error_log("CRITICAL: Failed to write log entry to file: $logFile", 0);
    echo json_encode([
        'status' => 'error', 
        'message' => "Failed to write log to file. Check file system status."
    ]);
}
?>
