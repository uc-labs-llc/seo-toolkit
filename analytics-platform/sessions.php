<?php
require_once 'config.php';

class SessionAnalysis {
    private $conn;

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getSessionDuration() {
        $query = "
            SELECT 
                session_id,
                MIN(event_timestamp) as session_start,
                MAX(event_timestamp) as session_end,
                COUNT(*) as event_count,
                EXTRACT(EPOCH FROM (MAX(event_timestamp) - MIN(event_timestamp))) as duration_seconds
            FROM analytics_events 
            WHERE session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY session_start DESC
            LIMIT 50
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getSessionFlow() {
        $query = "
            SELECT 
                session_id,
                COUNT(*) as page_views,
                STRING_AGG(action, ' → ' ORDER BY event_timestamp) as flow
            FROM analytics_events 
            WHERE session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY MIN(event_timestamp) DESC
            LIMIT 20
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

$database = new Database();
$db = $database->getConnection();
$sessionAnalysis = new SessionAnalysis($db);

$sessions = $sessionAnalysis->getSessionDuration();
$sessionFlow = $sessionAnalysis->getSessionFlow();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Analysis - Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Reuse styles from dashboard.php */
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f6fa; margin: 0; padding: 0; }
        .dashboard { display: grid; grid-template-columns: 250px 1fr; min-height: 100vh; }
        .sidebar { background: #2c3e50; color: white; padding: 20px; position: fixed; width: 250px; height: 100vh; }
        .main-content { grid-column: 2; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .table-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background: #f8f9fa; font-weight: 600; }
        .sidebar nav ul { list-style: none; }
        .sidebar nav ul li { margin-bottom: 10px; }
        .sidebar nav ul li a { color: #bdc3c7; text-decoration: none; padding: 10px 15px; display: block; border-radius: 5px; }
        .sidebar nav ul li a:hover { background: #34495e; color: #3498db; }
        .sidebar nav ul li a.active { background: #34495e; color: #3498db; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <h2>📊 Analytics Dashboard</h2>
            <nav>
                <ul>
                    <li><a href="dashboard.php">Overview</a></li>
                    <li><a href="sessions.php" class="active">Sessions</a></li>
                    <li><a href="performance.php">Performance</a></li>
                    <li><a href="users.php">User Analysis</a></li>
                    <li><a href="import_analytics.php">Import Data</a></li>
                    <li><a href="view_data.php">Raw Data</a></li>
                </ul>
            </nav>
        </div>

        <div class="main-content">
            <div class="header">
                <h1>Session Analysis</h1>
                <p>Detailed analysis of user sessions and behavior</p>
            </div>

            <div class="table-card">
                <h3>Recent Sessions Duration</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Start Time</th>
                            <th>End Time</th>
                            <th>Duration</th>
                            <th>Events</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($sessions as $session): ?>
                        <tr>
                            <td><?php echo substr($session['session_id'], 0, 15) . '...'; ?></td>
                            <td><?php echo htmlspecialchars($session['session_start']); ?></td>
                            <td><?php echo htmlspecialchars($session['session_end']); ?></td>
                            <td><?php echo round($session['duration_seconds'], 2); ?>s</td>
                            <td><?php echo $session['event_count']; ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <div class="table-card">
                <h3>Session Flow Analysis</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Session ID</th>
                            <th>Page Views</th>
                            <th>User Flow</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($sessionFlow as $flow): ?>
                        <tr>
                            <td><?php echo substr($flow['session_id'], 0, 15) . '...'; ?></td>
                            <td><?php echo $flow['page_views']; ?></td>
                            <td><?php echo htmlspecialchars($flow['flow']); ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
