<?php
require_once 'config.php';

class UserAnalysis {
    private $conn;

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getUserDemographics() {
        $query = "
            SELECT 
                language,
                timezone,
                COUNT(DISTINCT session_id) as session_count,
                AVG(load_time) as avg_load_time
            FROM analytics_events 
            WHERE session_id IS NOT NULL AND language IS NOT NULL
            GROUP BY language, timezone
            ORDER BY session_count DESC
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getScreenResolutions() {
        $query = "
            SELECT 
                screen_width || 'x' || screen_height as resolution,
                COUNT(DISTINCT session_id) as session_count,
                COUNT(*) as event_count
            FROM analytics_events 
            WHERE screen_width IS NOT NULL AND screen_height IS NOT NULL
            GROUP BY screen_width, screen_height
            ORDER BY session_count DESC
            LIMIT 10
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

$database = new Database();
$db = $database->getConnection();
$userAnalysis = new UserAnalysis($db);

$demographics = $userAnalysis->getUserDemographics();
$resolutions = $userAnalysis->getScreenResolutions();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Analysis - Analytics Dashboard</title>
    <style>
        /* Reuse styles from previous pages */
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f6fa; margin: 0; padding: 0; }
        .dashboard { display: grid; grid-template-columns: 250px 1fr; min-height: 100vh; }
        .sidebar { background: #2c3e50; color: white; padding: 20px; position: fixed; width: 250px; height: 100vh; }
        .main-content { grid-column: 2; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .table-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background: #f8f9fa; font-weight: 600; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <h2>📊 Analytics Dashboard</h2>
            <nav>
                <ul>
                    <li><a href="dashboard.php">Overview</a></li>
                    <li><a href="sessions.php">Sessions</a></li>
                    <li><a href="performance.php">Performance</a></li>
                    <li><a href="users.php" class="active">User Analysis</a></li>
                    <li><a href="import_analytics.php">Import Data</a></li>
                    <li><a href="view_data.php">Raw Data</a></li>
                </ul>
            </nav>
        </div>

        <div class="main-content">
            <div class="header">
                <h1>User Analysis</h1>
                <p>User demographics and technical information</p>
            </div>

            <div class="table-card">
                <h3>User Demographics</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Language</th>
                            <th>Timezone</th>
                            <th>Sessions</th>
                            <th>Avg Load Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($demographics as $demo): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($demo['language']); ?></td>
                            <td><?php echo htmlspecialchars($demo['timezone']); ?></td>
                            <td><?php echo $demo['session_count']; ?></td>
                            <td><?php echo round($demo['avg_load_time'], 2); ?>ms</td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <div class="table-card">
                <h3>Screen Resolutions</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Resolution</th>
                            <th>Sessions</th>
                            <th>Events</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($resolutions as $res): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($res['resolution']); ?></td>
                            <td><?php echo $res['session_count']; ?></td>
                            <td><?php echo $res['event_count']; ?></td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
