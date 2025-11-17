<?php
require_once 'config.php';

$database = new Database();
$db = $database->getConnection();

// Get total count
$count_query = "SELECT COUNT(*) as total FROM analytics_events";
$count_stmt = $db->prepare($count_query);
$count_stmt->execute();
$total_count = $count_stmt->fetch(PDO::FETCH_ASSOC)['total'];

// Get recent events
$query = "SELECT * FROM analytics_events ORDER BY event_timestamp DESC LIMIT 50";
$stmt = $db->prepare($query);
$stmt->execute();
$events = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Analytics Data</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .stats { background: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:hover { background-color: #f5f5f5; }
        .back-btn { display: inline-block; padding: 10px 20px; background: #6c757d; color: white; 
                   text-decoration: none; border-radius: 4px; margin-bottom: 20px; }
        .back-btn:hover { background: #545b62; }
    </style>
</head>
<body>
    <div class="container">
        <a href="import_analytics.php" class="back-btn">← Back to Importer</a>
        <h1>Analytics Data Viewer</h1>
        
        <div class="stats">
            <strong>Total Records:</strong> <?php echo $total_count; ?>
        </div>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Action</th>
                    <th>Timestamp</th>
                    <th>Location</th>
                    <th>Session ID</th>
                    <th>Screen Size</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($events as $event): ?>
                <tr>
                    <td><?php echo htmlspecialchars($event['id']); ?></td>
                    <td><?php echo htmlspecialchars($event['action']); ?></td>
                    <td><?php echo htmlspecialchars($event['event_timestamp']); ?></td>
                    <td><?php echo htmlspecialchars($event['location']); ?></td>
                    <td><?php echo htmlspecialchars($event['session_id'] ?? 'N/A'); ?></td>
                    <td><?php echo htmlspecialchars($event['screen_width'] . 'x' . $event['screen_height']); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        
        <?php if (empty($events)): ?>
            <p>No data found. Please import data first.</p>
        <?php endif; ?>
    </div>
</body>
</html>
