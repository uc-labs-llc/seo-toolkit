<?php
require_once 'config.php';

class PerformanceAnalysis {
    private $conn;

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getPerformanceMetrics() {
        $query = "
            SELECT 
                location,
                COUNT(*) as samples,
                AVG(load_time) as avg_load_time,
                AVG(dom_ready_time) as avg_dom_time,
                AVG(first_contentful_paint) as avg_fcp,
                MIN(load_time) as min_load_time,
                MAX(load_time) as max_load_time,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY load_time) as median_load_time
            FROM analytics_events 
            WHERE action = 'PERFORMANCE' AND load_time > 0
            GROUP BY location
            ORDER BY avg_load_time DESC
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function getLoadTimeDistribution() {
        $query = "
            SELECT 
                FLOOR(load_time/100) * 100 as load_time_range,
                COUNT(*) as count
            FROM analytics_events 
            WHERE action = 'PERFORMANCE' AND load_time > 0
            GROUP BY FLOOR(load_time/100)
            ORDER BY load_time_range
        ";
        $stmt = $this->conn->prepare($query);
        $stmt->execute();
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}

$database = new Database();
$db = $database->getConnection();
$performance = new PerformanceAnalysis($db);

$metrics = $performance->getPerformanceMetrics();
$distribution = $performance->getLoadTimeDistribution();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Analysis - Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        .chart-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .chart-container { height: 300px; }
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
                    <li><a href="performance.php" class="active">Performance</a></li>
                    <li><a href="users.php">User Analysis</a></li>
                    <li><a href="import_analytics.php">Import Data</a></li>
                    <li><a href="view_data.php">Raw Data</a></li>
                </ul>
            </nav>
        </div>

        <div class="main-content">
            <div class="header">
                <h1>Performance Analysis</h1>
                <p>Website performance metrics and load time analysis</p>
            </div>

            <div class="chart-card">
                <h3>Load Time Distribution</h3>
                <div class="chart-container">
                    <canvas id="loadTimeChart"></canvas>
                </div>
            </div>

            <div class="table-card">
                <h3>Performance Metrics by Page</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Page</th>
                            <th>Samples</th>
                            <th>Avg Load Time</th>
                            <th>Median Load Time</th>
                            <th>Min Load Time</th>
                            <th>Max Load Time</th>
                            <th>Avg DOM Ready</th>
                            <th>Avg FCP</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($metrics as $metric): ?>
                        <tr>
                            <td><?php echo htmlspecialchars($metric['location']); ?></td>
                            <td><?php echo $metric['samples']; ?></td>
                            <td><?php echo round($metric['avg_load_time'], 2); ?>ms</td>
                            <td><?php echo round($metric['median_load_time'], 2); ?>ms</td>
                            <td><?php echo round($metric['min_load_time'], 2); ?>ms</td>
                            <td><?php echo round($metric['max_load_time'], 2); ?>ms</td>
                            <td><?php echo round($metric['avg_dom_time'] ?? 0, 2); ?>ms</td>
                            <td><?php echo round($metric['avg_fcp'] ?? 0, 2); ?>ms</td>
                        </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Load Time Distribution Chart
        const loadTimeCtx = document.getElementById('loadTimeChart').getContext('2d');
        new Chart(loadTimeCtx, {
            type: 'bar',
            data: {
                labels: <?php echo json_encode(array_column($distribution, 'load_time_range')); ?>,
                datasets: [{
                    label: 'Number of Loads',
                    data: <?php echo json_encode(array_column($distribution, 'count')); ?>,
                    backgroundColor: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Load Time Range (ms)'
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
