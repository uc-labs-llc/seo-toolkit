<?php
require_once 'config.php';

class AnalyticsImporter {
    private $conn;
    private $table_name = "analytics_events";

    public function __construct($db) {
        $this->conn = $db;
    }

    /**
     * Parse a single log line and extract the JSON data
     */
    private function parseLogLine($line) {
        // Extract JSON part from log line
        $json_start = strpos($line, '{');
        $json_end = strrpos($line, '}');
        
        if ($json_start === false || $json_end === false) {
            return null;
        }
        
        $json_str = substr($line, $json_start, $json_end - $json_start + 1);
        $data = json_decode($json_str, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return null;
        }
        
        // Extract timestamp from log prefix
        preg_match('/\[([^\]]+)\]/', $line, $matches);
        $log_timestamp = isset($matches[1]) ? $matches[1] : null;
        
        return [
            'log_timestamp' => $log_timestamp,
            'data' => $data
        ];
    }

    /**
     * Insert parsed data into database
     */
    private function insertEvent($parsed_data) {
        $log_data = $parsed_data['data'];
        
        $query = "INSERT INTO " . $this->table_name . " 
            (log_timestamp, action, app_id, event_timestamp, location, user_agent, 
             screen_width, screen_height, page_title, session_id, session_start, 
             referrer, page_load_time, language, timezone, load_time, dom_ready_time, 
             first_paint, first_contentful_paint, session_pages, previous_page) 
            VALUES 
            (:log_timestamp, :action, :app_id, :event_timestamp, :location, :user_agent, 
             :screen_width, :screen_height, :page_title, :session_id, :session_start, 
             :referrer, :page_load_time, :language, :timezone, :load_time, :dom_ready_time, 
             :first_paint, :first_contentful_paint, :session_pages, :previous_page)";
        
        $stmt = $this->conn->prepare($query);
        
        // Bind parameters
        $stmt->bindParam(':log_timestamp', $parsed_data['log_timestamp']);
        $stmt->bindParam(':action', $log_data['action']);
        $stmt->bindParam(':app_id', $log_data['appId']);
        $stmt->bindParam(':event_timestamp', $log_data['timestamp']);
        $stmt->bindParam(':location', $log_data['location']);
        $stmt->bindParam(':user_agent', $log_data['userAgent']);
        $stmt->bindParam(':screen_width', $log_data['screenWidth']);
        $stmt->bindParam(':screen_height', $log_data['screenHeight']);
        
        // Optional fields with null coalescing
        $page_title = $log_data['pageTitle'] ?? null;
        $session_id = $log_data['sessionId'] ?? null;
        $session_start = $log_data['sessionStart'] ?? null;
        $referrer = $log_data['referrer'] ?? null;
        $page_load_time = $log_data['pageLoadTime'] ?? null;
        $language = $log_data['language'] ?? null;
        $timezone = $log_data['timezone'] ?? null;
        $load_time = $log_data['loadTime'] ?? null;
        $dom_ready_time = $log_data['domReadyTime'] ?? null;
        $first_paint = $log_data['firstPaint'] ?? null;
        $first_contentful_paint = $log_data['firstContentfulPaint'] ?? null;
        $session_pages = $log_data['sessionPages'] ?? null;
        $previous_page = $log_data['previousPage'] ?? null;
        
        $stmt->bindParam(':page_title', $page_title);
        $stmt->bindParam(':session_id', $session_id);
        $stmt->bindParam(':session_start', $session_start);
        $stmt->bindParam(':referrer', $referrer);
        $stmt->bindParam(':page_load_time', $page_load_time);
        $stmt->bindParam(':language', $language);
        $stmt->bindParam(':timezone', $timezone);
        $stmt->bindParam(':load_time', $load_time);
        $stmt->bindParam(':dom_ready_time', $dom_ready_time);
        $stmt->bindParam(':first_paint', $first_paint);
        $stmt->bindParam(':first_contentful_paint', $first_contentful_paint);
        $stmt->bindParam(':session_pages', $session_pages);
        $stmt->bindParam(':previous_page', $previous_page);
        
        try {
            return $stmt->execute();
        } catch (PDOException $e) {
            error_log("Insert error: " . $e->getMessage());
            return false;
        }
    }

    /**
     * Main function to process the log file
     */
    public function processLogFile($filename) {
        if (!file_exists($filename)) {
            return [
                'success' => false,
                'message' => "File not found: $filename"
            ];
        }

        $lines = file($filename, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        $total_lines = count($lines);
        $processed = 0;
        $successful = 0;
        $errors = [];

        foreach ($lines as $line_number => $line) {
            $processed++;
            
            $parsed_data = $this->parseLogLine($line);
            
            if (!$parsed_data) {
                $errors[] = "Line " . ($line_number + 1) . ": Invalid JSON format";
                continue;
            }
            
            if ($this->insertEvent($parsed_data)) {
                $successful++;
            } else {
                $errors[] = "Line " . ($line_number + 1) . ": Failed to insert into database";
            }
        }

        return [
            'success' => true,
            'total_lines' => $total_lines,
            'processed' => $processed,
            'successful' => $successful,
            'failed' => count($errors),
            'errors' => $errors
        ];
    }
}

// Main execution
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $database = new Database();
    $db = $database->getConnection();
    
    if ($db) {
        $importer = new AnalyticsImporter($db);
        $result = $importer->processLogFile('analytics.log');
        
        // Store result in session for display
        session_start();
        $_SESSION['import_result'] = $result;
        
        header('Location: ' . $_SERVER['PHP_SELF']);
        exit;
    } else {
        $error = "Failed to connect to database";
    }
}

// Check for previous results
session_start();
$result = $_SESSION['import_result'] ?? null;
if ($result) {
    unset($_SESSION['import_result']);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Log Importer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .btn {
            background-color: #007cba;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 20px auto;
        }
        .btn:hover {
            background-color: #005a87;
        }
        .result {
            margin: 20px 0;
            padding: 15px;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .stats {
            background-color: #e2e3e5;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .file-info {
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Analytics Log Importer</h1>
        
        <?php
        // Display file information
        $filename = 'analytics.log';
        if (file_exists($filename)) {
            $file_size = filesize($filename);
            $line_count = count(file($filename, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES));
            echo "<div class='file-info'>";
            echo "<strong>File:</strong> $filename<br>";
            echo "<strong>Size:</strong> " . number_format($file_size) . " bytes<br>";
            echo "<strong>Lines:</strong> " . number_format($line_count);
            echo "</div>";
        } else {
            echo "<div class='error result'>File 'analytics.log' not found in the same directory.</div>";
        }
        ?>

        <form method="POST">
            <button type="submit" class="btn" <?php echo !file_exists($filename) ? 'disabled' : ''; ?>>
                Import Analytics Data
            </button>
        </form>

        <?php if (isset($error)): ?>
            <div class="error result">
                <strong>Error:</strong> <?php echo htmlspecialchars($error); ?>
            </div>
        <?php endif; ?>

        <?php if ($result): ?>
            <div class="result <?php echo $result['success'] ? 'success' : 'error'; ?>">
                <h3>Import Results</h3>
                
                <div class="stats">
                    <strong>Total Lines:</strong> <?php echo $result['total_lines']; ?><br>
                    <strong>Processed:</strong> <?php echo $result['processed']; ?><br>
                    <strong>Successful:</strong> <?php echo $result['successful']; ?><br>
                    <strong>Failed:</strong> <?php echo $result['failed']; ?><br>
                    <strong>Success Rate:</strong> <?php echo $result['total_lines'] > 0 ? round(($result['successful'] / $result['total_lines']) * 100, 2) : 0; ?>%
                </div>

                <?php if (!empty($result['errors'])): ?>
                    <div style="margin-top: 15px;">
                        <strong>Errors:</strong>
                        <ul>
                            <?php foreach (array_slice($result['errors'], 0, 10) as $error): ?>
                                <li><?php echo htmlspecialchars($error); ?></li>
                            <?php endforeach; ?>
                            <?php if (count($result['errors']) > 10): ?>
                                <li>... and <?php echo count($result['errors']) - 10; ?> more errors</li>
                            <?php endif; ?>
                        </ul>
                    </div>
                <?php endif; ?>
            </div>

            <?php if ($result['successful'] > 0): ?>
                <div class="success result">
                    <strong>Success!</strong> Data has been imported into the database.
                    <br><br>
                    <a href="view_data.php" style="color: #155724; text-decoration: underline;">
                        View Imported Data →
                    </a>
                </div>
            <?php endif; ?>
        <?php endif; ?>
    </div>
</body>
</html>
